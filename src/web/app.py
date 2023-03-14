import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from flask import Flask, render_template, request, abort
from data import bookprice_db, model
from viewmodels.book_mapper import BookMapper

NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

db = bookprice_db.BookPriceDb(
    os.environ["MYSQL_SERVER"],
    os.environ["MYSQL_SERVER_PORT"],
    os.environ["MYSQL_USER"],
    os.environ["MYSQL_PASSWORD"],
    os.environ["MYSQL_DATABASE"])

app = Flask(__name__)


@app.route("/")
def index() -> str:
    search_phrase = request.args.get("search")
    books = db.get_books() if search_phrase is None else db.search_books(search_phrase)
    book_view_models = BookMapper.map_book_list(books)

    return render_template("index.html", books=book_view_models)


@app.route("/book/<int:book_id>")
def book(book_id: int) -> str:
    book = db.get_book(book_id)
    if book is None:
        abort(NOT_FOUND)

    book_prices = db.get_latest_prices(book.id)
    book_details = BookMapper.map_book_details(book, book_prices)

    return render_template("book.html", details=book_details)


@app.route("/book/<int:book_id>/store/<int:store_id>")
def price_history(book_id: int, store_id: int) -> str:
    book = db.get_book(book_id)
    if book is None:
        abort(NOT_FOUND)

    book_in_book_store = db.get_book_store_for_book(book, store_id)
    if book_in_book_store is None:
        abort(NOT_FOUND)

    book_prices = db.get_book_prices_for_store(book, book_in_book_store.book_store)
    price_history_view_model = BookMapper.map_price_history(book_in_book_store, book_prices)

    return render_template("price_history.html", view_model=price_history_view_model)


@app.errorhandler(NOT_FOUND)
def not_found(error):
    return render_template("404.html"), NOT_FOUND


@app.errorhandler(INTERNAL_SERVER_ERROR)
def not_found(error):
    return render_template("500.html"), INTERNAL_SERVER_ERROR


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")