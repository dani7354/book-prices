import flask_login
from flask_login import login_required, logout_user
from werkzeug.local import LocalProxy

import bookprices.web.mapper.user as usermapper
from flask import Blueprint, request, render_template, Response, redirect, url_for, abort, current_app, jsonify
from bookprices.shared.db import database
from bookprices.shared.model.user import UserAccessLevel
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.web.cache.redis import cache
from bookprices.web.service.auth_service import AuthService, require_member, require_admin
from bookprices.web.service.booklist_service import BookListService
from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_PORT
from bookprices.web.shared.db_session import SessionFactory
from bookprices.web.shared.enum import HttpMethod, UserTemplate, Endpoint, HttpStatusCode
from bookprices.web.viewmodels.user import UserEditViewModel

user_blueprint = Blueprint("user", __name__)

db = database.Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
auth_service = AuthService(db, cache)

logger = LocalProxy(lambda: current_app.logger)


@user_blueprint.context_processor
def include_csrf_token() -> dict[str, str]:
    return get_csrf_token()


@user_blueprint.route("/", methods=[HttpMethod.GET.value])
@flask_login.login_required
@require_admin
def index() -> str:
    page_number = request.args.get("page", 1, type=int)
    users = auth_service.get_users(page_number)
    can_edit_and_delete = auth_service.user_can_access(UserAccessLevel.ADMIN)

    previous_page = page_number - 1 if page_number > 1 else None
    next_page = page_number + 1 if len(users) == auth_service.max_users_per_page else None

    view_model = usermapper.map_user_list_view_model(
        users,
        page_number,
        next_page,
        previous_page,
        can_edit_and_delete,
        can_edit_and_delete)

    return render_template(UserTemplate.INDEX.value, view_model=view_model)


@user_blueprint.route("edit-current", methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@flask_login.login_required
@require_member
def edit_current() -> str | Response:
    if request.method == "POST":
        firstname = request.form.get(UserEditViewModel.firstname_field_name)
        lastname = request.form.get(UserEditViewModel.lastname_field_name)
        form_action_url = url_for(Endpoint.USER_EDIT_CURRENT.value, user_id=flask_login.current_user.id)

        view_model = UserEditViewModel(
            image_url=flask_login.current_user.image_url,
            id=flask_login.current_user.id,
            created=flask_login.current_user.created.isoformat(),
            updated=flask_login.current_user.updated.isoformat(),
            email=flask_login.current_user.email,
            firstname=firstname.strip(),
            lastname=lastname.strip(),
            is_active=flask_login.current_user.is_active,
            edit_current_user=True,
            access_level=flask_login.current_user.access_level.name,
            form_action_url=form_action_url)

        if not view_model.is_valid():
            return render_template(UserTemplate.EDIT_CURRENT.value, view_model=view_model)

        auth_service.update_user_info(
            view_model.id,
            view_model.email,
            view_model.firstname,
            view_model.lastname,
            UserAccessLevel.from_string(view_model.access_level),
            view_model.is_active)

        return redirect(url_for(Endpoint.USER_EDIT_CURRENT.value))

    view_model = usermapper.map_user_view_model(
        flask_login.current_user,
        form_action_url=url_for(Endpoint.USER_EDIT_CURRENT.value),
        edit_current_user=True)

    return render_template(UserTemplate.EDIT_CURRENT.value, view_model=view_model)


@user_blueprint.route("edit/<user_id>", methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@flask_login.login_required
@require_admin
def edit(user_id: str) -> str | Response:
    if not (user := auth_service.get_user(str(user_id))):
        abort(HttpStatusCode.NOT_FOUND, f"Brugeren med id {user_id} blev ikke fundet")

    if request.method == "POST":
        email = request.form.get(UserEditViewModel.email_field_name)
        firstname = request.form.get(UserEditViewModel.firstname_field_name)
        lastname = request.form.get(UserEditViewModel.lastname_field_name)
        is_active = bool(request.form.get(UserEditViewModel.is_active_field_name))
        access_level = request.form.get(UserEditViewModel.access_level_field_name)

        view_model = UserEditViewModel(
            id=user.id,
            image_url=user.image_url,
            created=user.created.isoformat(),
            updated=user.updated.isoformat(),
            email=email.strip(),
            firstname=firstname.strip(),
            lastname=lastname.strip(),
            is_active=is_active,
            edit_current_user=False,
            access_level=access_level,
            form_action_url=url_for(Endpoint.USER_EDIT.value, user_id=user.id))

        if not view_model.is_valid():
            return render_template(UserTemplate.EDIT_USER.value, view_model=view_model)

        parsed_access_level = UserAccessLevel.from_string(access_level)
        auth_service.update_user_info(
            user_id=view_model.id,
            email=view_model.email,
            firstname=view_model.firstname,
            lastname=view_model.lastname,
            access_level=parsed_access_level,
            is_active=view_model.is_active)
        logger.info(f"User {user.email} updated successfully by {flask_login.current_user.email}.")

        return redirect(url_for(Endpoint.USER_INDEX.value))

    view_model = usermapper.map_user_view_model(
        user,
        form_action_url=url_for(Endpoint.USER_EDIT.value, user_id=user.id),
        edit_current_user=False)

    return render_template(UserTemplate.EDIT_USER.value, view_model=view_model)


@user_blueprint.route("delete/<user_id>", methods=[HttpMethod.POST.value])
@login_required
@require_member
def delete(user_id: str) -> tuple[Response, int]:
    try:
        if not (deleting_current_user := flask_login.current_user.id == user_id) and not auth_service.user_can_access(UserAccessLevel.ADMIN):
            return jsonify("You cannot delete other users than your own."), HttpStatusCode.FORBIDDEN

        if not (user := auth_service.get_user(user_id)):
            return jsonify(f"User with ID {user_id} not found"), HttpStatusCode.NOT_FOUND

        logger.debug(f"Deleting user with email {user.email}...")
        auth_service.delete_user(user_id)
        logger.info(f"User {user.email} deleted by user {flask_login.current_user.email}.")
        if deleting_current_user:
            logger.info("Current user deleted, logging out...")
            logout_user()

        return jsonify({}), HttpStatusCode.OK
    except Exception as ex:
        logger.error(f"Failed to delete user {user_id}: {ex}")
        return (jsonify({"error": f"Der opstod en fejl under sletning af brugeren med id {user_id}"}),
                HttpStatusCode.INTERNAL_SERVER_ERROR)


@user_blueprint.route("set-booklist/<int:booklist_id>", methods=[HttpMethod.POST.value])
@login_required
@require_member
def set_booklist(booklist_id: int) -> tuple[Response, int]:
    user_id = flask_login.current_user.id
    try:
        booklist_service  = BookListService(UnitOfWork(SessionFactory()), cache)
        if not (booklist_service.get_booklist(booklist_id, user_id)):
            return jsonify({"error": f"Booklist with ID {booklist_id} not found"}), HttpStatusCode.NOT_FOUND
        auth_service.set_booklist_for_user(user_id, booklist_id)
        return jsonify({}), HttpStatusCode.OK
    except Exception as ex:
        logger.error(f"Failed to set booklist {booklist_id} for user {user_id}: {ex}")
        return jsonify({"error": str(ex)}), HttpStatusCode.INTERNAL_SERVER_ERROR
