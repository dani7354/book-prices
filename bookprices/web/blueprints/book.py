import flask_login
from werkzeug.local import LocalProxy
import bookprices.web.mapper.book as bookmapper
from flask import Blueprint, abort, request, render_template, Response, redirect, url_for, current_app
from bookprices.shared.db import database
from bookprices.shared.model.book import Book
from bookprices.web.blueprints.urlhelper import parse_args_for_search
from bookprices.web.cache.key_generator import (
    get_book_key, get_book_latest_prices_key, get_book_in_book_store_key)
from bookprices.web.service.book_service import BookService
from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.settings import (
    PAGE_URL_PARAMETER, SEARCH_URL_PARAMETER, AUTHOR_URL_PARAMETER, ORDER_BY_URL_PARAMETER, DESCENDING_URL_PARAMETER,
    MYSQL_USER, MYSQL_PORT, MYSQL_HOST, MYSQL_DATABASE, MYSQL_PASSWORD, BOOK_PAGESIZE)
from bookprices.web.cache.redis import cache
from bookprices.web.shared.enum import HttpStatusCode, HttpMethod, BookTemplate
from bookprices.web.viewmodels.book import CreateBookViewModel


logger = LocalProxy(lambda: current_app.logger)
book_blueprint = Blueprint("book", __name__)
db = database.Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
service = BookService(db, cache)


@book_blueprint.context_processor
def include_csrf_token() -> dict[str, str]:
    return get_csrf_token()


@book_blueprint.route("/search", methods=[HttpMethod.GET.value])
def search() -> str:
    args = parse_args_for_search(request.args)
    author = args.get(AUTHOR_URL_PARAMETER)
    search_phrase = args.get(SEARCH_URL_PARAMETER)
    order_by = args.get(ORDER_BY_URL_PARAMETER)
    descending = args.get(DESCENDING_URL_PARAMETER)
    page = args.get(PAGE_URL_PARAMETER)

    authors = service.get_authors()
    current_books = service.search(search_phrase, author, page, BOOK_PAGESIZE, order_by, descending)
    next_books = service.search(search_phrase, author, page + 1, BOOK_PAGESIZE, order_by, descending)

    next_page = page + 1 if len(next_books) > 0 else None
    previous_page = page - 1 if page >= 2 else None

    vm = bookmapper.map_search_vm(current_books,
                                  authors,
                                  search_phrase,
                                  page,
                                  author,
                                  previous_page,
                                  next_page,
                                  order_by,
                                  descending)

    return render_template(BookTemplate.SEARCH.value, view_model=vm)


@book_blueprint.route("/book/<int:book_id>", methods=[HttpMethod.GET.value])
def book(book_id: int) -> str:
    cache_key = get_book_key(book_id)
    if not (book := cache.get(cache_key)):
        if not book and not (book := db.book_db.get_book(book_id)):
            abort(HttpStatusCode.NOT_FOUND, "Bogen findes ikke")
        cache.set(cache_key, book)

    args = parse_args_for_search(request.args)
    page = args.get(PAGE_URL_PARAMETER)
    search_phrase = args.get(SEARCH_URL_PARAMETER)
    author = args.get(AUTHOR_URL_PARAMETER)
    order_by = args.get(ORDER_BY_URL_PARAMETER)
    descending = args.get(DESCENDING_URL_PARAMETER)

    if not (latest_prices := cache.get(get_book_latest_prices_key(book_id))):
        latest_prices = db.bookprice_db.get_latest_prices(book.id)
        cache.set(get_book_latest_prices_key(book_id), latest_prices)

    book_details = bookmapper.map_book_details(book,
                                               latest_prices,
                                               page,
                                               author,
                                               search_phrase,
                                               order_by,
                                               descending)

    return render_template(BookTemplate.BOOK.value, view_model=book_details)


@book_blueprint.route("/book/create", methods=[HttpMethod.GET.value, HttpMethod.POST.value])
@flask_login.login_required
def create() -> str | Response:
    if request.method == "POST":
        isbn = request.form.get(CreateBookViewModel.isbn_field_name) or ""
        title = request.form.get(CreateBookViewModel.title_field_name) or ""
        author = request.form.get(CreateBookViewModel.author_field_name) or ""
        book_format = request.form.get(CreateBookViewModel.format_field_name) or ""

        view_model = CreateBookViewModel(
            isbn=isbn.strip(),
            title=title.strip(),
            author=author.strip(),
            format=book_format.strip())

        if not view_model.is_valid():
            return render_template(BookTemplate.CREATE.value, view_model=view_model)
        if db.book_db.get_book_by_isbn(view_model.isbn):
            view_model.add_error(view_model.isbn_field_name, "Bogen findes allerede")
            return render_template(BookTemplate.CREATE.value, view_model=view_model)

        book_id = db.book_db.create_book(
            Book(id=0,
                 isbn=view_model.isbn,
                 title=view_model.title,
                 author=view_model.author,
                 format=view_model.format))

        return redirect(url_for("book.book", book_id=book_id))

    return render_template(BookTemplate.CREATE.value, view_model=CreateBookViewModel.empty())


@book_blueprint.route("/book/<int:book_id>/store/<int:store_id>", methods=[HttpMethod.GET.value])
def price_history(book_id: int, store_id: int) -> str:
    book_cache_key = get_book_key(book_id)
    if not (book := cache.get(book_cache_key)):
        if not book and not (book := db.book_db.get_book(book_id)):
            abort(HttpStatusCode.NOT_FOUND, "Bogen findes ikke")
        cache.set(book_cache_key, book)

    book_bookstore_cache_key = get_book_in_book_store_key(book_id, store_id)
    if not (book_in_bookstore := cache.get(book_bookstore_cache_key)):
        if not book_in_bookstore and not (book_in_bookstore := db.bookstore_db.get_bookstore_for_book(book, store_id)):
            abort(HttpStatusCode.NOT_FOUND, "Bogen er ikke tilknyttet den valgte boghandel")
        cache.set(book_bookstore_cache_key, book_in_bookstore)

    args = parse_args_for_search(request.args)
    page = args.get(PAGE_URL_PARAMETER)
    search_phrase = args.get(SEARCH_URL_PARAMETER)
    author = args.get(AUTHOR_URL_PARAMETER)
    order_by = args.get(ORDER_BY_URL_PARAMETER)
    descending = args.get(DESCENDING_URL_PARAMETER)

    price_history_view_model = bookmapper.map_price_history(book_in_bookstore,
                                                            page,
                                                            search_phrase,
                                                            author,
                                                            order_by,
                                                            descending)

    return render_template(BookTemplate.PRICE_HISTORY.value, view_model=price_history_view_model)
