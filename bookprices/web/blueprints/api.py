from flask import Blueprint, Response, jsonify, request, current_app, abort
from bookprices.shared.db.database import Database
from bookprices.web.blueprints.error_handler import not_found_api, internal_server_error_api
from bookprices.web.mapper.price import map_prices_history, map_price_history_for_stores
from bookprices.web.cache.redis import cache
from bookprices.web.blueprints.urlhelper import parse_args_for_search
from werkzeug.local import LocalProxy
from bookprices.web.settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    AUTHOR_URL_PARAMETER,
    SEARCH_URL_PARAMETER)
from bookprices.web.shared.enum import HttpStatusCode

RESPONSE_CACHE_TIMEOUT = 600

api_blueprint = Blueprint("api", __name__)
api_blueprint.register_error_handler(HttpStatusCode.NOT_FOUND, not_found_api)
api_blueprint.register_error_handler(HttpStatusCode.INTERNAL_SERVER_ERROR, internal_server_error_api)

logger = LocalProxy(lambda: current_app.logger)
db = Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)


@api_blueprint.route("/book/<int:book_id>")
@cache.cached(timeout=RESPONSE_CACHE_TIMEOUT)
def book(book_id: int) -> tuple[Response, int]:
    if not (book := db.book_db.get_book(book_id)):
        abort(HttpStatusCode.NOT_FOUND, "Bogen blev ikke fundet")

    book_prices = db.bookprice_db.get_all_book_prices(book)
    price_history_response = map_price_history_for_stores(book_prices)

    return jsonify(price_history_response), HttpStatusCode.OK


@api_blueprint.route("/book/<int:book_id>/store/<int:store_id>")
@cache.cached(timeout=RESPONSE_CACHE_TIMEOUT)
def prices(book_id: int, store_id: int) -> tuple[Response, int]:
    if not (book := db.book_db.get_book(book_id)):
        abort(HttpStatusCode.NOT_FOUND, "Bogen blev ikke fundet")

    if not (book_in_book_store := db.bookstore_db.get_bookstore_for_book(book, store_id)):
        abort(HttpStatusCode.NOT_FOUND, "Bogen er ikke tilknyttet den valgte boghandel")

    book_prices_for_store = db.bookprice_db.get_book_prices_for_store(book, book_in_book_store.book_store)
    price_history_response = map_prices_history(book_prices_for_store)

    return jsonify(price_history_response), HttpStatusCode.OK


@api_blueprint.route("/book/search_suggestions")
def search_suggestions() -> tuple[Response, int]:
    args = parse_args_for_search(request.args)
    search_phrase = args.get(SEARCH_URL_PARAMETER)
    author = args.get(AUTHOR_URL_PARAMETER)
    if not search_phrase:
        return jsonify([]), HttpStatusCode.OK

    if author:
        suggestions = db.book_db.get_search_suggestions_for_author(search_phrase, author)
    else:
        suggestions = db.book_db.get_search_suggestions(search_phrase)

    return jsonify(suggestions), HttpStatusCode.OK
