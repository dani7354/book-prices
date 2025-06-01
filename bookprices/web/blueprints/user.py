import flask_login
import bookprices.web.mapper.user as usermapper
from flask import Blueprint, request, render_template, Response, redirect, url_for
from bookprices.shared.db import database
from bookprices.web.cache.redis import cache
from bookprices.web.service.auth_service import AuthService, require_member
from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_PORT
from bookprices.web.shared.enum import HttpMethod, UserTemplate
from bookprices.web.viewmodels.user import UserEditViewModel

user_blueprint = Blueprint("user", __name__)

db = database.Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
auth_service = AuthService(db, cache)


@user_blueprint.context_processor
def include_csrf_token() -> dict[str, str]:
    return get_csrf_token()


@user_blueprint.route("/", methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@flask_login.login_required
@require_member
def index() -> str | Response:
    if request.method == "POST":
        email = request.form.get(UserEditViewModel.email_field_name)
        firstname = request.form.get(UserEditViewModel.firstname_field_name)
        lastname = request.form.get(UserEditViewModel.lastname_field_name)
        is_active = bool(request.form.get(UserEditViewModel.is_active_field_name))

        view_model = UserEditViewModel(
            image_url=flask_login.current_user.image_url,
            id=flask_login.current_user.id,
            created=flask_login.current_user.created.isoformat(),
            updated=flask_login.current_user.updated.isoformat(),
            email=email.strip(),
            firstname=firstname.strip(),
            lastname=lastname.strip(),
            is_active=is_active,
            access_level=flask_login.current_user.access_level)

        if not view_model.is_valid():
            return render_template(UserTemplate.EDIT_USER.value, view_model=view_model)

        auth_service.update_user_info(
            view_model.id,
            view_model.email,
            view_model.firstname,
            view_model.lastname,
            flask_login.current_user.access_level,
            view_model.is_active)

        return redirect(url_for("index"))

    view_model = usermapper.map_user_view_model(flask_login.current_user)
    return render_template(UserTemplate.EDIT_USER.value, view_model=view_model)
