from flask import current_app, render_template, jsonify, Response
from werkzeug.local import LocalProxy
from bookprices.web.shared.enum import HttpStatusCode

logger = LocalProxy(lambda: current_app.logger)


def not_found_html(error) -> tuple[str, int]:
    logger.error(error)
    return render_template("404.html"), HttpStatusCode.NOT_FOUND


def internal_server_error_html(error) -> tuple[str, int]:
    logger.error(error)
    return render_template("500.html"), HttpStatusCode.INTERNAL_SERVER_ERROR


def unauthorized_api(error) -> tuple[Response, int]:
    logger.error(error)
    return jsonify({"error_message": str(error)}), HttpStatusCode.UNAUTHORIZED


def forbidden_api(error) -> tuple[Response, int]:
    logger.error(error)
    return jsonify({"error_message": str(error)}), HttpStatusCode.FORBIDDEN


def bad_request_api(error) -> tuple[Response, int]:
    logger.error(error)
    return jsonify({"error_message": str(error)}), HttpStatusCode.BAD_REQUEST


def not_found_api(error) -> tuple[Response, int]:
    logger.error(error)
    return jsonify({"error_message": str(error)}), HttpStatusCode.NOT_FOUND


def internal_server_error_api(error) -> tuple[Response, int]:
    logger.error(error)
    return jsonify({"error_message": error}), HttpStatusCode.INTERNAL_SERVER_ERROR
