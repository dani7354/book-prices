from flask import Blueprint, render_template, Response, jsonify
from bookprices.shared.db import database
from bookprices.web.cache.redis import cache
from bookprices.web.service.failed_update_service import FailedUpdateService
from bookprices.web.mapper.price import map_failed_price_update_counts
from bookprices.web.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


status_blueprint = Blueprint("status", __name__)

db = database.Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
failed_update_service = FailedUpdateService(db, cache)


@status_blueprint.route("/", methods=["GET"])
def index() -> str:
    return render_template("status/index.html")


@status_blueprint.route("/failed_price_updates", methods=["GET"])
def failed_price_updates() -> tuple[Response, int]:
    failed_updates = failed_update_service.get_failed_price_updates_by_bookstore()
    response = map_failed_price_update_counts(failed_updates)

    return jsonify(response), 200



