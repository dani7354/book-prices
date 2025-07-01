from flask import Blueprint, abort, current_app, render_template, Response, request
from flask_login import login_required
from werkzeug.local import LocalProxy

from bookprices.shared.model.user import UserAccessLevel
from bookprices.web.service.auth_service import require_admin, AuthService
from bookprices.web.service.bookstore_service import BookStoreService
from bookprices.shared.db.database import Database
from bookprices.web.mapper.bookstore import map_to_bookstore_list, map_bookstore_edit_view_model
from bookprices.web.cache.redis import cache
from bookprices.web.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from bookprices.web.shared.enum import BookStoreTemplate, HttpMethod, HttpStatusCode
from bookprices.web.viewmodels.bookstore import BookStoreEditViewModel

logger = LocalProxy(lambda: current_app.logger)

bookstore_blueprint = Blueprint("bookstore", __name__)


db = Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
bookstore_service = BookStoreService(db, cache)


@bookstore_blueprint.route("", methods=[HttpMethod.GET.value])
@login_required
@require_admin
def index() -> str:
    bookstores = bookstore_service.get_bookstores()
    auth_service = AuthService(db, cache)
    is_admin = auth_service.user_can_access(UserAccessLevel.ADMIN)
    view_model = map_to_bookstore_list(bookstores, current_user_is_admin=is_admin)

    return render_template(BookStoreTemplate.INDEX.value, view_model=view_model)


@bookstore_blueprint.route("edit/<int:bookstore_id>", methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@login_required
@require_admin
def edit(bookstore_id: int) -> str | Response:
    if not (bookstore := bookstore_service.get_bookstore(bookstore_id)):
        return abort(HttpStatusCode.NOT_FOUND, "Boghandlen blev ikke fundet")

    if request.method == HttpMethod.POST.value:
        bookstore_id_from_form = request.form.get(BookStoreEditViewModel.id_field_name)
        name = request.form.get(BookStoreEditViewModel.name_field_name) or ""
        url = request.form.get(BookStoreEditViewModel.url_field_name) or ""
        search_url = request.form.get(BookStoreEditViewModel.search_url_field_name) or ""
        search_result_css = request.form.get(BookStoreEditViewModel.search_result_css_field_name) or ""
        image_css = request.form.get(BookStoreEditViewModel.image_css_field_name) or ""
        isbn_css = request.form.get(BookStoreEditViewModel.isbn_css_field_name) or ""
        price_format = request.form.get(BookStoreEditViewModel.price_format_field_name) or ""


    view_model = map_bookstore_edit_view_model(bookstore)
    return render_template(BookStoreTemplate.EDIT.value, view_model=view_model)
