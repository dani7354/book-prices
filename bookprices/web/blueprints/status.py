from flask import Blueprint, render_template, Response, jsonify, request
from flask_login import login_required
from bookprices.shared.db import database
from bookprices.web.cache.redis import cache
from bookprices.web.service.status_service import StatusService
from bookprices.web.mapper.status import map_failed_price_update_counts, map_book_import_counts
from bookprices.web.shared.enum import HttpMethod
from bookprices.web.viewmodels.status import IndexViewModel
from bookprices.web.blueprints.urlhelper import parse_args_for_status_endpoint
from bookprices.web.settings import (
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, TIMEPERIOD_DAYS_URL_PARAMETER)

status_blueprint = Blueprint("status", __name__)

db = database.Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
status_service = StatusService(db, cache)


@status_blueprint.route("/", methods=[HttpMethod.GET.value])
@login_required
def index() -> str:
    view_model = IndexViewModel(timeperiod_options=status_service.get_timeperiod_options())

    return render_template("status/index.html", view_model=view_model)


@status_blueprint.route("/failed-price-updates", methods=[HttpMethod.GET.value])
@login_required
def failed_price_updates() -> tuple[Response, int]:
    timeperiod_options = status_service.get_timeperiod_options()
    args = parse_args_for_status_endpoint(request.args, timeperiod_options[0].days)
    failed_updates = status_service.get_failed_price_updates_by_bookstore(
        days=args[TIMEPERIOD_DAYS_URL_PARAMETER])
    response = map_failed_price_update_counts(failed_updates)

    return jsonify(response), 200


@status_blueprint.route("/book-import-counts", methods=[HttpMethod.GET.value])
@login_required
def book_import_counts() -> tuple[Response, int]:
    timeperiod_options = status_service.get_timeperiod_options()
    args = parse_args_for_status_endpoint(request.args, timeperiod_options[0].days)
    import_counts = status_service.get_book_import_count_by_bookstore(
        days=args[TIMEPERIOD_DAYS_URL_PARAMETER])
    response = map_book_import_counts(import_counts)

    return jsonify(response), 200
