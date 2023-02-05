import sys, os
sys.path.append("..")
from flask import Flask, render_template, request, redirect, url_for, session
from data import bookprice_db, model
from configuration import config
from viewmodels.book_mapper import BookMapper


config = config.ConfigLoader.load("config.json")
db = bookprice_db.BookPriceDb(
    config.database.db_host,
    config.database.db_port,
    config.database.db_user,
    config.database.db_password,
    config.database.db_name)
app = Flask(__name__)


@app.route("/")
def index():
    books = db.get_books()
    book_view_models = BookMapper.map_book_list(books)

    return render_template("index.html", books=book_view_models)


@app.route("/book/<int:book_id>")
def book(book_id):
    book = db.get_book(book_id)
    if book is None:
        return "<h1>404 Not Found</h1>", 404
    book_prices = db.get_latest_prices(book.id)
    book_details = BookMapper.map_book_details(book, book_prices)

    return render_template("book.html", details=book_details)


@app.route("/book/<int:book_id>/store/<int:store_id>")
def price_history(book_id, store_id):
    book = db.get_book(book_id)
    book_store = db.get_book_store(store_id)

    if book is None or book_store is None:
        return "<h1>404 Not Found</h1>", 404

    prices_for_store = db.get_book_prices_for_store(book, book_store)
    price_history_view_model = BookMapper.map_price_history(book, book_store, prices_for_store)

    return render_template("price_history.html", price_history=price_history_view_model)


if __name__ == "__main__":
    app.run(debug=True)