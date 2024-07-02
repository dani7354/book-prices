import flask_login
from werkzeug.local import LocalProxy
import bookprices.web.mapper.book as bookmapper
from flask import Blueprint, abort, request, render_template, Response, redirect, url_for, current_app
from bookprices.shared.db import database
from bookprices.shared.model.book import Book
from bookprices.web.blueprints.urlhelper import parse_args_for_search
from bookprices.web.service.book_service import BookService
from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.service.sri import get_sri_attribute_values
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


@book_blueprint.context_processor
def include_sri_attribute_values() -> dict[str, str]:
    return get_sri_attribute_values()


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
    if not (book_result := service.get_book(book_id)):
        abort(HttpStatusCode.NOT_FOUND, "Bogen findes ikke")

    args = parse_args_for_search(request.args)
    page = args.get(PAGE_URL_PARAMETER)
    search_phrase = args.get(SEARCH_URL_PARAMETER)
    author = args.get(AUTHOR_URL_PARAMETER)
    order_by = args.get(ORDER_BY_URL_PARAMETER)
    descending = args.get(DESCENDING_URL_PARAMETER)

    latest_prices = service.get_latest_prices(book_id)
    book_details = bookmapper.map_book_details(book_result,
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
        if service.get_book_by_isbn(view_model.isbn):
            view_model.add_error(view_model.isbn_field_name, "Bogen findes allerede")
            return render_template(BookTemplate.CREATE.value, view_model=view_model)

        book_id = service.create_book(
            Book(id=0,
                 isbn=view_model.isbn,
                 title=view_model.title,
                 author=view_model.author,
                 format=view_model.format))

        return redirect(url_for("book.book", book_id=book_id))

    return render_template(BookTemplate.CREATE.value, view_model=CreateBookViewModel.empty())


@book_blueprint.route("/book/<int:book_id>/store/<int:store_id>", methods=[HttpMethod.GET.value])
def price_history(book_id: int, store_id: int) -> str:
    if not (book_result := service.get_book(book_id)):
        abort(HttpStatusCode.NOT_FOUND, "Bogen findes ikke")

    if not (book_in_bookstore := service.get_book_in_bookstore(book_result, store_id)):
        abort(HttpStatusCode.NOT_FOUND, "Bogen er ikke tilknyttet den valgte boghandel")

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
