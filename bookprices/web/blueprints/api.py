from typing import Union
from flask import Blueprint, Response, jsonify
from bookprices.shared.db.database import Database
from bookprices.web.mapper.price import map_prices_for_book_in_store
from bookprices.web.settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE)


api_blueprint = Blueprint("api", __name__)

db = Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)


@api_blueprint.route("/book/<int:book_id>/store/<int:store_id>")
def prices(book_id: int, store_id: int) -> Union[Response, tuple[Response, int]]:
    book = db.book_db.get_book(book_id)
    if not book:
        return jsonify({"message": f"Book with id {book_id} not found"}), 404

    book_in_book_store = db.bookstore_db.get_book_store_for_book(book, store_id)
    if not book_in_book_store:
        return jsonify({"message": f"Book store with id {store_id} not found"}), 404

    book_prices_for_store = db.bookprice_db.get_book_prices_for_store(book, book_in_book_store.book_store)
    prices_response = map_prices_for_book_in_store(book_prices_for_store)

    return jsonify(prices_response)
