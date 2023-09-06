import os
import bookprices.shared.db.database as database
import bookprices.web.mapper.price as price_mapper
import bookprices.web.mapper.book as bookmapper
from flask import Flask, render_template, request, abort
from bookprices.web.plot.price import PriceHistory

NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

BOOK_PAGESIZE = 12
BOOK_IMAGES_PATH = "/static/images/books/"
BOOK_FALLBACK_IMAGE_NAME = "default.png"

AUHTOR_PARAMETER = "author"
SEARCH_PARAMETER = "search"
PAGE_PARAMETER = "page"


db = database.Database(
    os.environ["MYSQL_SERVER"],
    os.environ["MYSQL_SERVER_PORT"],
    os.environ["MYSQL_USER"],
    os.environ["MYSQL_PASSWORD"],
    os.environ["MYSQL_DATABASE"])

app = Flask(__name__)
app.debug = os.environ.get("DEBUG", False)


@app.route("/")
def index() -> str:
    author = request.args.get(AUHTOR_PARAMETER, type=str)
    search_phrase = request.args.get(SEARCH_PARAMETER, type=str, default="")
    page = request.args.get(PAGE_PARAMETER, type=int, default=1)
    page = page if page > 0 else 1

    authors = db.book_db.get_authors()
    books_current = db.book_db.search_books(search_phrase, author, page, BOOK_PAGESIZE)
    books_next = db.book_db.search_books(search_phrase, author, page + 1, BOOK_PAGESIZE)
    next_page = page + 1 if len(books_next) > 0 else None
    previous_page = page - 1 if page >= 2 else None

    vm = bookmapper.map_index_vm(books_current,
                                 authors,
                                 search_phrase,
                                 BOOK_IMAGES_PATH,
                                 BOOK_FALLBACK_IMAGE_NAME,
                                 page,
                                 author,
                                 previous_page,
                                 next_page)

    return render_template("index.html", view_model=vm)


@app.route("/book/<int:book_id>")
def book(book_id: int) -> str:
    book = db.book_db.get_book(book_id)
    if book is None:
        abort(NOT_FOUND)

    page = request.args.get(PAGE_PARAMETER, type=int)
    search_phrase = request.args.get(SEARCH_PARAMETER, type=str)
    author = request.args.get(AUHTOR_PARAMETER, type=str)

    latest_prices = db.bookprice_db.get_latest_prices(book.id)
    all_prices = db.bookprice_db.get_all_book_prices(book)
    linedata = price_mapper.map_to_linedata_list(all_prices)
    price_history_plot = PriceHistory(linedata)
    plot_base64 = price_history_plot.get_plot_base64()

    book_details = bookmapper.map_book_details(book,
                                               latest_prices,
                                               BOOK_IMAGES_PATH,
                                               BOOK_FALLBACK_IMAGE_NAME,
                                               plot_base64,
                                               page,
                                               author,
                                               search_phrase)

    return render_template("book.html", view_model=book_details)


@app.route("/book/<int:book_id>/store/<int:store_id>")
def price_history(book_id: int, store_id: int) -> str:
    book = db.book_db.get_book(book_id)
    if book is None:
        abort(NOT_FOUND)

    book_in_book_store = db.bookstore_db.get_book_store_for_book(book, store_id)
    if book_in_book_store is None:
        abort(NOT_FOUND)

    page = request.args.get(PAGE_PARAMETER, type=int)
    search_phrase = request.args.get(SEARCH_PARAMETER, type=str)
    author = request.args.get(AUHTOR_PARAMETER, type=str)

    book_prices = db.bookprice_db.get_book_prices_for_store(book, book_in_book_store.book_store)
    linedata = price_mapper.map_to_linedata(book_prices, book_in_book_store.book_store.name)
    price_history_plot = PriceHistory([linedata])
    plot_base64 = price_history_plot.get_plot_base64()

    price_history_view_model = bookmapper.map_price_history(book_in_book_store,
                                                            book_prices,
                                                            plot_base64,
                                                            page,
                                                            search_phrase,
                                                            author)

    return render_template("price_history.html", view_model=price_history_view_model)


@app.errorhandler(NOT_FOUND)
def not_found(error):
    return render_template("404.html"), NOT_FOUND


@app.errorhandler(INTERNAL_SERVER_ERROR)
def not_found(error):
    return render_template("500.html"), INTERNAL_SERVER_ERROR


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3031)
