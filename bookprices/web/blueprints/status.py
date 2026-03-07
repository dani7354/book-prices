from flask import Blueprint, render_template, Response, jsonify, request
from flask_login import login_required
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.web.cache.redis import cache
from bookprices.web.service.auth_service import require_admin
from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.service.status_service import StatusService
from bookprices.web.shared.db_session import WebSessionFactory
from bookprices.web.shared.enum import HttpMethod, HttpStatusCode, StatusTemplate
from bookprices.web.viewmodels.status import IndexViewModel
from bookprices.web.blueprints.urlhelper import parse_args_for_status_endpoint
from bookprices.web.settings import TIMEPERIOD_DAYS_URL_PARAMETER

status_blueprint = Blueprint("status", __name__)


@status_blueprint.context_processor
def include_csrf_token() -> dict[str, str]:
    return get_csrf_token()


@status_blueprint.route("/", methods=[HttpMethod.GET])
@login_required
@require_admin
def index() -> str:
    status_service = _create_status_service()
    view_model = IndexViewModel(timeperiod_options=status_service.get_timeperiod_options())

    return render_template(StatusTemplate.INDEX.value, view_model=view_model)


@status_blueprint.route("/failed-price-updates", methods=[HttpMethod.GET])
@login_required
@require_admin
def failed_price_updates() -> tuple[Response, int]:
    status_service = _create_status_service()
    timeperiod_options = status_service.get_timeperiod_options()
    args = parse_args_for_status_endpoint(request.args, timeperiod_options[0].days)
    failed_updates = status_service.get_failed_price_updates_by_bookstore(
        days=args[TIMEPERIOD_DAYS_URL_PARAMETER])

    return jsonify(failed_updates), HttpStatusCode.OK


@status_blueprint.route("/book-import-counts", methods=[HttpMethod.GET])
@login_required
@require_admin
def book_import_counts() -> tuple[Response, int]:
    status_service = _create_status_service()
    timeperiod_options = status_service.get_timeperiod_options()
    args = parse_args_for_status_endpoint(request.args, timeperiod_options[0].days)
    import_counts = status_service.get_book_import_count_by_bookstore(
        days=args[TIMEPERIOD_DAYS_URL_PARAMETER])

    return jsonify(import_counts), HttpStatusCode.OK


@status_blueprint.route("/price-counts", methods=[HttpMethod.GET])
@login_required
@require_admin
def book_price_counts() -> tuple[Response, int]:
    status_service = _create_status_service()
    timeperiod_options = status_service.get_timeperiod_options()
    args = parse_args_for_status_endpoint(request.args, timeperiod_options[0].days)
    price_counts = status_service.get_price_count_by_bookstore(
        days=args[TIMEPERIOD_DAYS_URL_PARAMETER])

    return jsonify(price_counts), HttpStatusCode.OK


@status_blueprint.route("/updated-prices", methods=[HttpMethod.GET])
@login_required
@require_admin
def updated_prices() -> tuple[Response, int]:
    status_service = _create_status_service()
    timeperiod_options = status_service.get_timeperiod_options()
    args = parse_args_for_status_endpoint(request.args, timeperiod_options[0].days)
    updated_prices_response = status_service.get_updated_prices_for_bookstores(
        days=args[TIMEPERIOD_DAYS_URL_PARAMETER])

    return jsonify(updated_prices_response), HttpStatusCode.OK


def _create_status_service() -> StatusService:
    return StatusService(UnitOfWork(WebSessionFactory()), cache)