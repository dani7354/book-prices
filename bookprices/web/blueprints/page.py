import bookprices.shared.db.database as database
import bookprices.web.mapper.book as bookmapper
from bookprices.web.cache.memcahed import cache
from bookprices.web.cache.key_generator import get_book_key, get_book_in_book_store_key, get_book_latest_prices_key
from flask import render_template, request, abort, Blueprint
from bookprices.web.settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    AUTHOR_URL_PARAMETER,
    SEARCH_URL_PARAMETER,
    PAGE_URL_PARAMETER,
    BOOK_PAGESIZE)

NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

page_blueprint = Blueprint("page", __name__)

db = database.Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)


@page_blueprint.route("/")
@cache.cached(query_string=True)
def index() -> str:
    author = request.args.get(AUTHOR_URL_PARAMETER, type=str)
    search_phrase = request.args.get(SEARCH_URL_PARAMETER, type=str, default="")
    page = request.args.get(PAGE_URL_PARAMETER, type=int, default=1)
    page = page if page > 0 else 1

    authors = db.book_db.get_authors()
    books_current = db.book_db.search_books(search_phrase, author, page, BOOK_PAGESIZE)
    books_next = db.book_db.search_books(search_phrase, author, page + 1, BOOK_PAGESIZE)
    next_page = page + 1 if len(books_next) > 0 else None
    previous_page = page - 1 if page >= 2 else None

    vm = bookmapper.map_index_vm(books_current,
                                 authors,
                                 search_phrase,
                                 page,
                                 author,
                                 previous_page,
                                 next_page)

    return render_template("index.html", view_model=vm)


@page_blueprint.route("/book/<int:book_id>")
def book(book_id: int) -> str:
    cache_key = get_book_key(book_id)
    if not (book := cache.get(cache_key)):
        if not book and not (book := db.book_db.get_book(book_id)):
            abort(NOT_FOUND)
        cache.set(cache_key, book)

    page = request.args.get(PAGE_URL_PARAMETER, type=int)
    search_phrase = request.args.get(SEARCH_URL_PARAMETER, type=str)
    author = request.args.get(AUTHOR_URL_PARAMETER, type=str)

    if not (latest_prices := cache.get(get_book_latest_prices_key(book_id))):
        latest_prices = db.bookprice_db.get_latest_prices(book.id)
        cache.set(get_book_latest_prices_key(book_id), latest_prices)

    book_details = bookmapper.map_book_details(book,
                                               latest_prices,
                                               page,
                                               author,
                                               search_phrase)

    return render_template("book.html", view_model=book_details)


@page_blueprint.route("/book/<int:book_id>/store/<int:store_id>")
def price_history(book_id: int, store_id: int) -> str:
    if not (book := cache.get(get_book_key(book_id))):
        if not book and not (book := db.book_db.get_book(book_id)):
            abort(NOT_FOUND)
        cache.set(get_book_key(book_id), book)

    if not (book_in_bookstore := cache.get(get_book_in_book_store_key(book_id, store_id))):
        if not book_in_bookstore and not (book_in_bookstore := db.bookstore_db.get_book_store_for_book(book, store_id)):
            abort(NOT_FOUND)
        cache.set(get_book_in_book_store_key(book_id, store_id), book_in_bookstore)

    page = request.args.get(PAGE_URL_PARAMETER, type=int)
    search_phrase = request.args.get(SEARCH_URL_PARAMETER, type=str)
    author = request.args.get(AUTHOR_URL_PARAMETER, type=str)

    price_history_view_model = bookmapper.map_price_history(book_in_bookstore,
                                                            page,
                                                            search_phrase,
                                                            author)

    return render_template("price_history.html", view_model=price_history_view_model)


@page_blueprint.errorhandler(NOT_FOUND)
def not_found(error):
    return render_template("404.html"), NOT_FOUND


@page_blueprint.errorhandler(INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    return render_template("500.html"), INTERNAL_SERVER_ERROR
