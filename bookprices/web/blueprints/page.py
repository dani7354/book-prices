import bookprices.shared.db.database as database
import bookprices.web.mapper.book as bookmapper
from bookprices.shared.db.book import BookSearchSortOption
from bookprices.web.blueprints.error_handler import not_found_html, internal_server_error_html
from bookprices.web.cache.redis import cache
from bookprices.web.blueprints.urlhelper import format_url_for_redirection
from flask import render_template, request, Blueprint, redirect, Response, url_for
from flask_login import current_user
from bookprices.web.service.auth_service import AuthService
from bookprices.web.service.book_service import BookService
from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.shared.enum import HttpMethod, HttpStatusCode, PageTemplate, Endpoint
from bookprices.web.viewmodels.page import AboutViewModel
from bookprices.shared.cache.key_generator import get_bookstores_key
from bookprices.web.settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE)


page_blueprint = Blueprint("page", __name__)
page_blueprint.register_error_handler(HttpStatusCode.NOT_FOUND, not_found_html)
page_blueprint.register_error_handler(HttpStatusCode.INTERNAL_SERVER_ERROR, internal_server_error_html)

db = database.Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
auth_service = AuthService(db, cache)
book_service = BookService(db, cache)


@page_blueprint.context_processor
def include_csrf_token() -> dict[str, str]:
    return get_csrf_token()


@page_blueprint.route("/", methods=[HttpMethod.GET.value])
def index() -> str:
    newest_books = book_service.search(
        search_phrase="",
        author=None,
        page=1,
        page_size=8,
        sort_option=BookSearchSortOption.Created,
        descending=True)

    newest_prices_books = book_service.search(
        search_phrase="",
        author=None,
        page=1,
        page_size=8,
        sort_option=BookSearchSortOption.PriceUpdated,
        descending=True)

    view_model = bookmapper.map_index_vm(newest_books=newest_books, latest_updated_books=newest_prices_books)

    return render_template(PageTemplate.INDEX.value, view_model=view_model)


@page_blueprint.route("/about", methods=[HttpMethod.GET.value])
def about() -> str:
    bookstores_cache_key = get_bookstores_key()
    if not (bookstores := cache.get(bookstores_cache_key)):
        bookstores = db.bookstore_db.get_bookstores()
        cache.set(bookstores_cache_key, bookstores)
    view_model = AboutViewModel(bookstores)

    return render_template(PageTemplate.ABOUT.value, view_model=view_model)


@page_blueprint.route("/login", methods=[HttpMethod.GET.value])
def login() -> Response | str:
    redirect_url = redirect_url if (redirect_url := format_url_for_redirection(request.args.get("next"))) \
        else url_for(Endpoint.PAGE_INDEX.value)
    if current_user.is_authenticated:
        return redirect(redirect_url)

    return render_template(PageTemplate.LOGIN.value, redirect_url=redirect_url)
