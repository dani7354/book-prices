from flask import Blueprint, abort, current_app, render_template, Response, request, url_for, redirect, jsonify
from flask_login import login_required
from werkzeug.local import LocalProxy

from bookprices.shared.model.user import UserAccessLevel
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.shared.service.scraper_service import BookStoreScraperService
from bookprices.web.service.auth_service import require_admin, AuthService
from bookprices.web.service.bookstore_service import BookStoreService
from bookprices.shared.db.database import Database
from bookprices.web.mapper.bookstore import (
    map_to_bookstore_list, map_bookstore_edit_view_model, map_bookstore_edit_view_model_from_form)
from bookprices.web.cache.redis import cache
from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from bookprices.web.shared.db_session import WebSessionFactory
from bookprices.web.shared.enum import BookStoreTemplate, HttpMethod, HttpStatusCode, Endpoint
from bookprices.web.viewmodels.bookstore import BookStoreEditViewModel

logger = LocalProxy(lambda: current_app.logger)

bookstore_blueprint = Blueprint("bookstore", __name__)


db = Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
bookstore_service = BookStoreService(UnitOfWork(WebSessionFactory()), cache)
bookstore_scraper_service = BookStoreScraperService(UnitOfWork(WebSessionFactory()))


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
    scraper_names = bookstore_scraper_service.get_scraper_names()
    if request.method == HttpMethod.POST.value:
        view_model = map_bookstore_edit_view_model_from_form(
            request,
            form_action_url=url_for(Endpoint.BOOKSTORE_CREATE.value),
            return_url=url_for(Endpoint.BOOKSTORE_INDEX.value),
            scraper_names=scraper_names)

        if not view_model.is_valid():
            return render_template(BookStoreTemplate.CREATE.value, view_model=view_model)

        bookstore_service.create(
            name=view_model.name,
            url=view_model.url,
            search_url=view_model.search_url,
            search_result_css=view_model.search_result_css,
            image_css=view_model.image_css,
            isbn_css=view_model.isbn_css,
            price_css=view_model.price_css,
            price_format=view_model.price_format,
            color_hex=view_model.color_hex,
            scraper_id=view_model.scraper_id)

        return redirect(url_for(Endpoint.BOOKSTORE_INDEX.value))

    view_model = BookStoreEditViewModel.empty(
        form_action_url=url_for(Endpoint.BOOKSTORE_CREATE.value),
        return_url=url_for(Endpoint.BOOKSTORE_INDEX.value),
        scraper_names=scraper_names)

    return render_template(BookStoreTemplate.CREATE.value, view_model=view_model)


@bookstore_blueprint.route("edit/<int:bookstore_id>", methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@login_required
@require_admin
def edit(bookstore_id: int) -> str | Response:
    if not (bookstore := bookstore_service.get_bookstore(bookstore_id)):
        return abort(HttpStatusCode.NOT_FOUND, "Boghandlen blev ikke fundet")

    scraper_names = bookstore_scraper_service.get_scraper_names()
    if request.method == HttpMethod.POST.value:
        view_model = map_bookstore_edit_view_model_from_form(
            request,
            form_action_url=url_for(Endpoint.BOOKSTORE_EDIT.value, bookstore_id=bookstore_id),
            return_url=url_for(Endpoint.BOOKSTORE_INDEX.value),
            scraper_names=scraper_names,
            bookstore_id=bookstore_id)

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
                color_hex=view_model.color_hex,
                scraper_id=view_model.scraper_id)

            return redirect(url_for(Endpoint.BOOKSTORE_INDEX.value))

        except Exception as ex:
            logger.error(f"Failed to update bookstore: {ex}")
            view_model.add_error(BookStoreEditViewModel.name_field_name, str(ex))

    view_model = map_bookstore_edit_view_model(bookstore, scraper_names)
    return render_template(BookStoreTemplate.EDIT.value, view_model=view_model)


@bookstore_blueprint.route("delete/<int:bookstore_id>", methods=[HttpMethod.POST.value])
@login_required
@require_admin
def delete(bookstore_id: int) -> tuple[Response, int]:
    if not (bookstore_service.get_bookstore(bookstore_id)):
        return jsonify({"error": f"Boghandlen med id {bookstore_id} blev ikke fundet"}), HttpStatusCode.NOT_FOUND
    try:
        bookstore_service.delete(bookstore_id)
    except Exception as ex:
        logger.error(f"Failed to delete bookstore: {ex}")
        return jsonify({"error": "Noget gik galt under sletning af boghandlen"}), HttpStatusCode.INTERNAL_SERVER_ERROR

    return jsonify({}), HttpStatusCode.OK