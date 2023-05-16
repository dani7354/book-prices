import os
from flask import Flask, render_template, request, abort

import bookprices.shared.db.database as database
from bookprices.web.mapper.book import BookMapper

NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

BOOK_PAGESIZE = 12
BOOK_IMAGES_PATH = "/static/images/books/"
BOOK_FALLBACK_IMAGE_NAME = "default.png"

db = database.Database(
    os.environ["MYSQL_SERVER"],
    os.environ["MYSQL_SERVER_PORT"],
    os.environ["MYSQL_USER"],
    os.environ["MYSQL_PASSWORD"],
    os.environ["MYSQL_DATABASE"])

app = Flask(__name__)


@app.route("/")
def index() -> str:
    search_phrase = request.args.get("search", type=str, default="")
    page = request.args.get("page", type=int, default=1)
    page = page if page > 0 else 1

    books_current = db.book_db.search_books(search_phrase, page, BOOK_PAGESIZE)
    books_next = db.book_db.search_books(search_phrase, page + 1, BOOK_PAGESIZE)
    next_page = page + 1 if len(books_next) > 0 else None
    previous_page = page - 1 if page >= 2 else None

    vm = BookMapper.map_index_vm(books_current,
                                 search_phrase,
                                 BOOK_IMAGES_PATH,
                                 BOOK_FALLBACK_IMAGE_NAME,
                                 page,
                                 previous_page,
                                 next_page)

    return render_template("index.html", view_model=vm)


@app.route("/book/<int:book_id>")
def book(book_id: int) -> str:
    book = db.book_db.get_book(book_id)
    if book is None:
        abort(NOT_FOUND)

    book_prices = db.bookprice_db.get_latest_prices(book.id)
    book_details = BookMapper.map_book_details(book,
                                               book_prices,
                                               BOOK_IMAGES_PATH,
                                               BOOK_FALLBACK_IMAGE_NAME)

    return render_template("book.html", details=book_details)


@app.route("/book/<int:book_id>/store/<int:store_id>")
def price_history(book_id: int, store_id: int) -> str:
    book = db.book_db.get_book(book_id)
    if book is None:
        abort(NOT_FOUND)

    book_in_book_store = db.bookstore_db.get_book_store_for_book(book, store_id)
    if book_in_book_store is None:
        abort(NOT_FOUND)

    book_prices = db.bookprice_db.get_book_prices_for_store(book, book_in_book_store.book_store)
    price_history_view_model = BookMapper.map_price_history(book_in_book_store, book_prices)

    return render_template("price_history.html", view_model=price_history_view_model)


@app.errorhandler(NOT_FOUND)
def not_found(error):
    return render_template("404.html"), NOT_FOUND


@app.errorhandler(INTERNAL_SERVER_ERROR)
def not_found(error):
    return render_template("500.html"), INTERNAL_SERVER_ERROR


if __name__ == "__main__":
    debug = os.environ.get("DEBUG", False)
    app.run(debug=debug, host="0.0.0.0")