from flask import Blueprint, abort, current_app, render_template, Response, request, url_for, redirect
from flask_login import login_required
from werkzeug.local import LocalProxy

from bookprices.shared.model.user import UserAccessLevel
from bookprices.web.service.auth_service import require_admin, AuthService
from bookprices.web.service.bookstore_service import BookStoreService
from bookprices.shared.db.database import Database
from bookprices.web.mapper.bookstore import map_to_bookstore_list, map_bookstore_edit_view_model
from bookprices.web.cache.redis import cache
from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from bookprices.web.shared.enum import BookStoreTemplate, HttpMethod, HttpStatusCode, Endpoint
from bookprices.web.viewmodels.bookstore import BookStoreEditViewModel

logger = LocalProxy(lambda: current_app.logger)

bookstore_blueprint = Blueprint("bookstore", __name__)


db = Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
bookstore_service = BookStoreService(db, cache)


@bookstore_blueprint.context_processor
def include_csrf_token() -> dict[str, str]:
    return get_csrf_token()


@bookstore_blueprint.route("", methods=[HttpMethod.GET.value])
@login_required
@require_admin
def index() -> str:
    bookstores = bookstore_service.get_bookstores()
    auth_service = AuthService(db, cache)
    is_admin = auth_service.user_can_access(UserAccessLevel.ADMIN)
    view_model = map_to_bookstore_list(bookstores, current_user_is_admin=is_admin)

    return render_template(BookStoreTemplate.INDEX.value, view_model=view_model)


@bookstore_blueprint.route("create", methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@login_required
@require_admin
def create() -> str | Response:
    if request.method == HttpMethod.POST.value:
        pass

    view_model = BookStoreEditViewModel.empty(
        form_action_url=url_for(Endpoint.BOOKSTORE_CREATE.value),
        return_url=url_for(Endpoint.BOOKSTORE_INDEX.value))

    return render_template(BookStoreTemplate.CREATE.value, view_model=view_model)


@bookstore_blueprint.route("edit/<int:bookstore_id>", methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@login_required
@require_admin
def edit(bookstore_id: int) -> str | Response:
    if not (bookstore := bookstore_service.get_bookstore(bookstore_id)):
        return abort(HttpStatusCode.NOT_FOUND, "Boghandlen blev ikke fundet")

    if request.method == HttpMethod.POST.value:
        bookstore_id_from_form = request.form.get(BookStoreEditViewModel.id_field_name) or bookstore_id
        name = request.form.get(BookStoreEditViewModel.name_field_name) or ""
        url = request.form.get(BookStoreEditViewModel.url_field_name) or ""
        search_url = request.form.get(BookStoreEditViewModel.search_url_field_name) or None
        search_result_css = request.form.get(BookStoreEditViewModel.search_result_css_field_name) or None
        image_css = request.form.get(BookStoreEditViewModel.image_css_field_name) or None
        isbn_css = request.form.get(BookStoreEditViewModel.isbn_css_field_name) or None
        price_css = request.form.get(BookStoreEditViewModel.price_css_field_name) or None
        price_format = request.form.get(BookStoreEditViewModel.price_format_field_name) or None
        has_dynamic_content = bool(request.form.get(BookStoreEditViewModel.has_dynamic_content_field_name)) or False

        view_model = BookStoreEditViewModel(
            id=bookstore_id_from_form,
            name=name,
            url=url,
            search_url=search_url,
            search_result_css=search_result_css,
            image_css=image_css,
            isbn_css=isbn_css,
            price_css=price_css,
            price_format=price_format,
            has_dynamic_content=has_dynamic_content,
            form_action_url=url_for(Endpoint.BOOKSTORE_EDIT.value, bookstore_id=bookstore_id),
            return_url=url_for(Endpoint.BOOKSTORE_INDEX.value))

        if not view_model.is_valid():
            return render_template(BookStoreTemplate.EDIT.value, view_model=view_model)

        try:
            bookstore_service.update(
                bookstore_id=int(view_model.id),
                name=view_model.name,
                url=view_model.url,
                search_url=view_model.search_url,
                search_result_css=view_model.search_result_css,
                image_css=view_model.image_css,
                isbn_css=view_model.isbn_css,
                price_css=view_model.price_css,
                price_format=view_model.price_format,
                has_dynamic_content=view_model.has_dynamic_content)

            return redirect(url_for(Endpoint.BOOKSTORE_INDEX.value))

        except Exception as ex:
            logger.error(f"Failed to update bookstore: {ex}")
            view_model.add_error(BookStoreEditViewModel.name_field_name, str(ex))



    view_model = map_bookstore_edit_view_model(bookstore)
    return render_template(BookStoreTemplate.EDIT.value, view_model=view_model)
