from flask import Blueprint, Response, jsonify
from bookprices.shared.db.database import Database
from bookprices.web.mapper.price import map_prices_history, map_price_history_for_stores
from bookprices.web.cache.memcached import cache
from bookprices.web.settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE)

RESPONSE_TIMEOUT = 600

api_blueprint = Blueprint("api", __name__)

db = Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)


@api_blueprint.route("/book/<int:book_id>")
@cache.cached(timeout=RESPONSE_TIMEOUT)
def book(book_id: int) -> tuple[Response, int]:
    if not (book := db.book_db.get_book(book_id)):
        return jsonify({"message": f"Book with id {book_id} not found"}), 404

    book_prices = db.bookprice_db.get_all_book_prices(book)
    price_history_response = map_price_history_for_stores(book_prices)

    return jsonify(price_history_response), 200


@api_blueprint.route("/book/<int:book_id>/store/<int:store_id>")
@cache.cached(timeout=RESPONSE_TIMEOUT)
def prices(book_id: int, store_id: int) -> tuple[Response, int]:
    if not (book := db.book_db.get_book(book_id)):
        return jsonify({"message": f"Book with id {book_id} not found"}), 404

    if not (book_in_book_store := db.bookstore_db.get_book_store_for_book(book, store_id)):
        return jsonify({"message": f"Book store with id {store_id} not found"}), 404

    book_prices_for_store = db.bookprice_db.get_book_prices_for_store(book, book_in_book_store.book_store)
    price_history_response = map_prices_history(book_prices_for_store)

    return jsonify(price_history_response), 200
