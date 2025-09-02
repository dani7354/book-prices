import flask_login
from flask import render_template, current_app, Blueprint, request, redirect, url_for, Response, jsonify, abort
from flask_login import login_required
from werkzeug.local import LocalProxy

from bookprices.shared.db.database import Database
from bookprices.web.cache.redis import cache
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.web.mapper.booklist import map_to_booklist_list, map_to_details_view_model, map_to_edit_view_model
from bookprices.web.service.auth_service import require_member
from bookprices.web.service.book_service import BookService
from bookprices.web.service.booklist_service import BookListService, BookListNotFoundError
from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, \
    PAGE_URL_PARAMETER
from bookprices.web.shared.db_session import SessionFactory
from bookprices.web.shared.enum import HttpMethod, BookListTemplate, Endpoint, HttpStatusCode
from bookprices.web.viewmodels.booklist import BookListEditViewModel, AddToListRequest, RemoveFromListRequest

booklist_blueprint = Blueprint("booklist", __name__)
logger = LocalProxy(lambda: current_app.logger)


def _create_booklist_service() -> BookListService:
    return BookListService(UnitOfWork(SessionFactory()), cache)


def _create_book_service() -> BookService:
    db = Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
    return BookService(db, cache)


@booklist_blueprint.context_processor
def include_csrf_token() -> dict[str, str]:
    return get_csrf_token()


@booklist_blueprint.route("", methods=[HttpMethod.GET.value])
@login_required
@require_member
def index() -> str:
    booklist_service = _create_booklist_service()
    user = flask_login.current_user
    booklists = booklist_service.get_booklists(user.id)
    view_model = map_to_booklist_list(booklists, selected_booklist_id=user.booklist_id if user.booklist_id else None)
    return render_template(BookListTemplate.INDEX.value, view_model=view_model)


@booklist_blueprint.route("<int:booklist_id>", methods=[HttpMethod.GET.value])
@login_required
@require_member
def view(booklist_id: int) -> str:
    booklist_service = _create_booklist_service()
    user = flask_login.current_user
    if not (booklist := booklist_service.get_booklist(booklist_id, user.id)):
        return abort(HttpStatusCode.NOT_FOUND.value, "Boglisten blev ikke fundet")

    page = request.args.get(PAGE_URL_PARAMETER, type=int, default=1)

    book_service = _create_book_service()
    books = book_service.get_books_by_ids([book.book_id for book in booklist.books])

    view_model = map_to_details_view_model(booklist, books, user.booklist_id, page)
    return render_template(BookListTemplate.BOOKLIST.value, view_model=view_model)


@booklist_blueprint.route("create", methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@login_required
@require_member
def create() -> str | Response:
    return_url = url_for(Endpoint.BOOKLIST_INDEX.value)
    form_action_url = url_for(Endpoint.BOOKLIST_CREATE.value)
    if request.method == HttpMethod.POST.value:
        name = request.form.get(BookListEditViewModel.name_field_name) or None
        description = request.form.get(BookListEditViewModel.description_field_name) or None

        view_model = BookListEditViewModel(
            name=name,
            description=description,
            form_action_url=form_action_url,
            return_url=return_url)
        if not view_model.is_valid():
            return render_template(BookListTemplate.CREATE.value, view_model=view_model)
        booklist_service = _create_booklist_service()
        if not booklist_service.name_available(view_model.name, flask_login.current_user.id):
            view_model.add_error(BookListEditViewModel.name_field_name, "Bogliste findes allerede")
            return render_template(BookListTemplate.CREATE.value, view_model=view_model)

        booklist_service.create_booklist(name=view_model.name, description=description, user_id=flask_login.current_user.id)
        return redirect(url_for(Endpoint.BOOKLIST_INDEX.value))

    return render_template(
        BookListTemplate.CREATE.value,
        view_model=BookListEditViewModel.empty(form_action_url=form_action_url, return_url=return_url))


@booklist_blueprint.route("edit/<int:booklist_id>", methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@login_required
@require_member
def edit(booklist_id: int) -> str | Response:
    booklist_service = _create_booklist_service()
    user_id = flask_login.current_user.id
    if not (booklist := booklist_service.get_booklist(booklist_id, user_id)):
        return abort(HttpStatusCode.NOT_FOUND.value, "Boghandlen blev ikke fundet")

    if request.method == HttpMethod.POST.value:
        name = request.form.get(BookListEditViewModel.name_field_name, type=str) or None
        description = request.form.get(BookListEditViewModel.description_field_name, type=str) or None
        return_url = url_for(Endpoint.BOOKLIST_VIEW.value, booklist_id=booklist_id)
        form_action_url = url_for(Endpoint.BOOKLIST_EDIT.value, booklist_id=booklist_id)

        view_model = BookListEditViewModel(
            name=name,
            description=description,
            form_action_url=form_action_url,
            return_url=return_url)

        if not view_model.is_valid():
            return render_template(BookListTemplate.EDIT.value, view_model=view_model)

        if not booklist_service.name_available(view_model.name, user_id, booklist_id):
            view_model.add_error(BookListEditViewModel.name_field_name, "Bogliste findes allerede")
            return render_template(BookListTemplate.EDIT.value, view_model=view_model)

        booklist_service.update_booklist(
            booklist_id=booklist_id,
            name=view_model.name,
            description=view_model.description,
            user_id=flask_login.current_user.id)
        logger.info(f"Booklist {booklist_id} updated for user with id {user_id}")
        return redirect(return_url)

    view_model = map_to_edit_view_model(
        booklist,
        form_action_url=url_for(Endpoint.BOOKLIST_EDIT.value, booklist_id=booklist_id),
        return_url=url_for(Endpoint.BOOKLIST_INDEX.value))

    return render_template(BookListTemplate.EDIT.value, view_model=view_model)


@booklist_blueprint.route("delete/<int:booklist_id>", methods=[HttpMethod.POST.value])
@login_required
@require_member
def delete(booklist_id: int) -> tuple[Response, int]:
    booklist_service = _create_booklist_service()
    try:
        booklist_service.delete_booklist(booklist_id, flask_login.current_user.id)
        logger.info(f"Booklist {booklist_id} deleted for user {flask_login.current_user.id}")
        return jsonify({}), 200
    except BookListNotFoundError as ex:
        logger.error(f"Failed to delete booklist {booklist_id} for user {flask_login.current_user.id}: {ex}")
        return jsonify({"error": str(ex)}), 404


@booklist_blueprint.route("add", methods=[HttpMethod.POST.value])
@login_required
@require_member
def add_to_list() -> tuple[Response, int]:
    if not (book_id := request.form.get(AddToListRequest.book_id_field_name, type=int)):
        return jsonify({"error": "Book id is required!"}), 400

    booklist_service = _create_booklist_service()
    user = flask_login.current_user
    if not (booklist := booklist_service.get_booklist(user.booklist_id, user.id)):
        return jsonify({"error": "No booklist found for user, cannot add book to booklist."}), 400

    if not (booklist_service.add_book(book_id=book_id, booklist_id=booklist.id, user_id=flask_login.current_user.id)):
        return jsonify({"error": "Could not add book to booklist, booklist not found or not accessible."}), 400

    logger.info(f"Book {book_id} added to booklist {booklist.id} for user {flask_login.current_user.id}")

    return jsonify({}), 200


@booklist_blueprint.route("remove", methods=[HttpMethod.POST.value])
@login_required
@require_member
def remove_from_list() -> tuple[Response, int]:
    if not (book_id := request.form.get(RemoveFromListRequest.book_id_field_name, type=int)):
        return jsonify({"error": "Book id is required!"}), 400

    booklist_service = _create_booklist_service()
    user = flask_login.current_user
    if not (booklist := booklist_service.get_booklist(user.booklist_id, user.id)):
        return jsonify({"error": "No booklist found for user, cannot add book to booklist."}), 400

    if not (booklist_service.delete_book(book_id=book_id, booklist_id=booklist.id, user_id=user.id)):
        return jsonify({"error": "Could not remove book from booklist, booklist not found or not accessible."}), 400

    return jsonify({}), 200
