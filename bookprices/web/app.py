import logging
import os
from logging.config import dictConfig
from flask.logging import default_handler
from typing import Optional
from flask import Flask, request, jsonify, Response
from flask_login import LoginManager
from bookprices.shared.db.database import Database
from bookprices.web.blueprints.api import api_blueprint
from bookprices.web.blueprints.auth import auth_blueprint
from bookprices.web.blueprints.book import book_blueprint
from bookprices.web.blueprints.error_handler import not_found_html, internal_server_error_html
from bookprices.web.blueprints.logging_configuration import RequestFormatter
from bookprices.web.blueprints.status import status_blueprint
from bookprices.web.blueprints.user import user_blueprint
from bookprices.web.blueprints.page import page_blueprint
from bookprices.web.service.auth_service import AuthService, WebUser
from bookprices.web.cache.redis import cache
from bookprices.web.service.csrf import CSRFService
from bookprices.web.settings import (
    DEBUG_MODE, FLASK_APP_PORT, FLASK_SECRET_KEY, SITE_HOSTNAME, MYSQL_HOST, MYSQL_PORT,
    MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
from bookprices.web.shared.enum import HttpStatusCode

static_folder = "static"
static_url_path = None
if DEBUG_MODE:
    static_folder = "assets"
    static_url_path = "/static/assets"

    # This is needed for testing Google OAuth2 locally, since the redirect url is using http
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


# logging
dictConfig({
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        },
    },
    "handlers": {"wsgi": {
        "class": 'logging.StreamHandler',
        "formatter": "default"
    }},
    "root": {
        "level": "DEBUG",
        "handlers": ["wsgi"]
    }
})

# app
app = Flask(__name__, static_url_path=static_url_path, static_folder=static_folder)
app.debug = DEBUG_MODE
app.config.update(
    TESTING=DEBUG_MODE,
    SECRET_KEY=FLASK_SECRET_KEY,
    SESSION_COOKIE_DOMAIN=SITE_HOSTNAME,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=not DEBUG_MODE,
    SESSION_COOKIE_SAMESITE="Lax",
)
default_handler.setLevel(logging.INFO)
default_handler.setFormatter(RequestFormatter.get_formatter())
app.logger.addHandler(default_handler)


# blueprints
app.register_blueprint(page_blueprint)
app.register_blueprint(book_blueprint)
app.register_blueprint(api_blueprint, url_prefix="/api")
app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(status_blueprint, url_prefix="/status")
app.register_error_handler(HttpStatusCode.NOT_FOUND, not_found_html)
app.register_error_handler(HttpStatusCode.INTERNAL_SERVER_ERROR, internal_server_error_html)

cache.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "page.login"


@app.before_request
def validate_csrf_token() -> None | tuple[Response, int]:
    if request.method == "POST":
        if not (csrf_token := request.form.get("csrf_token")):
            return jsonify({"Error": "CSRF token not present in request payload"}), 400
        if not CSRFService().is_token_valid(csrf_token):
            return jsonify({"Error": "CSRF token invalid"}), 400

    return None  # token is valid or HTTP method is not POST


@login_manager.user_loader
def load_user(user_id: str) -> Optional[WebUser]:
    auth_service = AuthService(
        Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE),
        cache)

    return auth_service.get_user(user_id)


if __name__ == "__main__":
    app.run(host=SITE_HOSTNAME, port=FLASK_APP_PORT)
