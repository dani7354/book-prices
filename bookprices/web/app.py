import os
from typing import Optional
from flask import Flask, request, jsonify, Response
from flask_login import LoginManager
from bookprices.shared.db.database import Database
from bookprices.web.blueprints.api import api_blueprint
from bookprices.web.blueprints.auth import auth_blueprint
from bookprices.web.blueprints.status import status_blueprint
from bookprices.web.blueprints.user import user_blueprint
from bookprices.web.blueprints.page import page_blueprint, not_found, internal_server_error
from bookprices.web.service import csrf
from bookprices.web.service.auth_service import AuthService, WebUser
from bookprices.web.cache.redis import cache
from bookprices.web.service.csrf import CSRFService
from bookprices.web.settings import (
    DEBUG_MODE, FLASK_APP_PORT, FLASK_SECRET_KEY, SITE_HOSTNAME, MYSQL_HOST, MYSQL_PORT,
    MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)

static_folder = "static"
static_url_path = None
if DEBUG_MODE:
    static_folder = "assets"
    static_url_path = "/static/assets"

    # This is needed for testing Google OAuth2 locally, since the redirect url is using http
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

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

app.register_blueprint(api_blueprint, url_prefix="/api")
app.register_blueprint(page_blueprint)
app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(status_blueprint, url_prefix="/status")

app.register_error_handler(404, not_found)
app.register_error_handler(500, internal_server_error)
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
