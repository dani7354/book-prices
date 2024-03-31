import flask_login
import bookprices.shared.db.database as database
import bookprices.web.mapper.book as bookmapper
from bookprices.web.blueprints.error_handler import not_found_html, internal_server_error_html
from bookprices.web.cache.redis import cache
from bookprices.web.blueprints.urlhelper import format_url_for_redirection
from flask import render_template, request, Blueprint, redirect, Response, url_for
from flask_login import current_user
from bookprices.web.service.auth_service import AuthService
from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.shared.enum import HttpMethod, HttpStatusCode
from bookprices.web.viewmodels.page import AboutViewModel
from bookprices.web.cache.key_generator import (
    get_bookstores_key,
    get_index_latest_books_key,
    get_index_latest_prices_books_key)
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


@page_blueprint.context_processor
def include_csrf_token() -> dict[str, str]:
    return get_csrf_token()


@page_blueprint.route("/", methods=[HttpMethod.GET.value])
def index() -> str:
    if not (newest_books := cache.get(get_index_latest_books_key())):
        newest_books = db.book_db.get_newest_books(limit=8)
        cache.set(get_index_latest_books_key(), newest_books)
    if not (newest_prices_books := cache.get(get_index_latest_prices_books_key())):
        newest_prices_books = db.book_db.get_books_with_newest_prices(limit=8)
        cache.set(get_index_latest_prices_books_key(), newest_prices_books)
    view_model = bookmapper.map_index_vm(newest_books=newest_books, latest_updated_books=newest_prices_books)

    return render_template("index.html", view_model=view_model)


@page_blueprint.route("/about", methods=[HttpMethod.GET.value])
def about() -> str:
    bookstores_cache_key = get_bookstores_key()
    if not (bookstores := cache.get(bookstores_cache_key)):
        bookstores = db.bookstore_db.get_bookstores()
        cache.set(bookstores_cache_key, bookstores)
    view_model = AboutViewModel(bookstores)

    return render_template("about.html", view_model=view_model)


@page_blueprint.route("/login", methods=[HttpMethod.GET.value])
def login() -> Response | str:
    redirect_url = redirect_url if (redirect_url := format_url_for_redirection(request.args.get("next"))) \
        else url_for("page.index")
    if current_user.is_authenticated:
        return redirect(redirect_url)

    return render_template("login.html", redirect_url=redirect_url)


@page_blueprint.route("/admin", methods=[HttpMethod.GET.value])
@flask_login.login_required
def admin() -> str:
    return render_template("admin.html")
