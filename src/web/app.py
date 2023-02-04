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
def details(book_id):
    # Do lookup and return book details!
    return ""


if __name__ == "__main__":
    app.run(debug=True)