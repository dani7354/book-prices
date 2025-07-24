import flask_login
from flask import render_template, current_app, Blueprint, request, redirect, url_for, Response, jsonify
from flask_login import login_required
from werkzeug.local import LocalProxy

from bookprices.web.cache.redis import cache
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.web.mapper.booklist import map_to_booklist_list, map_to_details_view_model
from bookprices.web.service.auth_service import require_member
from bookprices.web.service.booklist_service import BookListService
from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.shared.db_session import SessionFactory
from bookprices.web.shared.enum import HttpMethod, BookListTemplate, Endpoint
from bookprices.web.viewmodels.booklist import BookListEditViewModel, AddToListRequest

booklist_blueprint = Blueprint("booklist", __name__)
logger = LocalProxy(lambda: current_app.logger)


def _create_booklist_service() -> BookListService:
    return BookListService(UnitOfWork(SessionFactory()), cache)


@booklist_blueprint.context_processor
def include_csrf_token() -> dict[str, str]:
    return get_csrf_token()


@booklist_blueprint.route("", methods=[HttpMethod.GET.value])
@login_required
@require_member
def index() -> str:
    booklist_service = _create_booklist_service()
    booklists = booklist_service.get_booklists(flask_login.current_user.id)
    view_model = map_to_booklist_list(booklists)
    return render_template(BookListTemplate.INDEX.value, view_model=view_model)


@booklist_blueprint.route("<int:booklist_id>", methods=[HttpMethod.GET.value])
@login_required
@require_member
def view(booklist_id: int) -> str:
    booklist_service = _create_booklist_service()
    booklist = booklist_service.get_booklist(booklist_id, flask_login.current_user.id)
    view_model = map_to_details_view_model(booklist)
    return render_template(BookListTemplate.BOOKLIST.value, view_model=view_model)


@booklist_blueprint.route("create", methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@login_required
@require_member
def create() -> str | Response:
    return_url = url_for(Endpoint.BOOKLIST_INDEX.value)
    form_action_url = url_for(Endpoint.BOOKLIST_CREATE.value)
    if request.method == HttpMethod.POST.value:
        name = request.form.get(BookListEditViewModel.name_field_name) or None

        view_model = BookListEditViewModel(
            name=name,
            form_action_url=form_action_url,
            return_url=return_url)
        if not view_model.is_valid():
            return render_template(BookListTemplate.CREATE.value, view_model=view_model)
        booklist_service = _create_booklist_service()
        if not booklist_service.name_available(view_model.name, flask_login.current_user.id):
            view_model.add_error(BookListEditViewModel.name_field_name, "Bogliste findes allerede")
            return render_template(BookListTemplate.CREATE.value, view_model=view_model)

        booklist_service.create_booklist(name= view_model.name, user_id=flask_login.current_user.id)
        return redirect(url_for(Endpoint.BOOKLIST_INDEX.value))

    return render_template(
        BookListTemplate.CREATE.value,
        view_model=BookListEditViewModel.empty(form_action_url=form_action_url, return_url=return_url))


@booklist_blueprint.route("add", methods=[HttpMethod.POST.value])
@login_required
@require_member
def add_to_list() -> tuple[Response, int]:
    book_id = request.form.get(AddToListRequest.book_id_field_name, type=int)
    booklist_id = request.form.get(AddToListRequest.booklist_id_field_name, type=int)

    if not book_id or not booklist_id:
        return jsonify({"error": "Book and book list id is required!"}), 400

    booklist_service = _create_booklist_service()
    booklist_service.add_book(
        book_id=book_id,
        booklist_id=booklist_id,
        user_id=flask_login.current_user.id)
    logger.info(f"Book {book_id} added to booklist {booklist_id} for user {flask_login.current_user.id}")

    return jsonify({}), 200
