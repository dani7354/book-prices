import google_auth_oauthlib.flow
from enum import Enum
from flask import Blueprint, request, redirect, url_for, session, Response, jsonify
from bookprices.shared.db.database import Database
from bookprices.web.cache.redis import cache
from bookprices.web.service.auth_service import AuthService
from bookprices.web.service.csrf import CSRFService
from bookprices.web.service.google_api_service import GoogleApiService
from bookprices.web.blueprints.urlhelper import format_url_for_redirection
from flask_login import (
    login_user,
    logout_user)
from bookprices.web.settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    GOOGLE_CLIENT_SECRETS_FILE,
    GOOGLE_OAUTH_REDIRECT_URI,
    GOOGLE_API_SCOPES)

PAGE_INDEX_ENDPOINT = "page.index"

auth_blueprint = Blueprint("auth", __name__)
auth_service = AuthService(
    Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE),
    cache)


class SessionKey(Enum):
    STATE = "state"
    REDIRECT_URL = "redirect_url"


@auth_blueprint.before_request  # TODO: move this when POST request methods are added to other BluePrints
def validate_csrf_token() -> None | tuple[Response, int]:
    if request.method == "POST":
        if not (csrf_token := request.form.get("csrf_token")):
            return jsonify({"Error": "CSRF token not present in request payload"}), 400
        if not CSRFService().is_token_valid(csrf_token):
            return jsonify({"Error": "CSRF token invalid"}), 400
    return None


@auth_blueprint.route("/authorize")
def authorize() -> Response:
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      GOOGLE_CLIENT_SECRETS_FILE, scopes=GOOGLE_API_SCOPES)
    flow.redirect_uri = GOOGLE_OAUTH_REDIRECT_URI
    authorization_url, state = flow.authorization_url(
      access_type="offline",
      include_granted_scopes="true")

    session[SessionKey.STATE.value] = state
    session[SessionKey.REDIRECT_URL.value] = redirect_url if (redirect_url := request.args.get("next")) \
        else url_for(PAGE_INDEX_ENDPOINT)

    return redirect(authorization_url)


@auth_blueprint.route("/oauth2callback")
def oauth2callback() -> Response | tuple[Response, int]:
    state = session[SessionKey.STATE.value]
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE, scopes=GOOGLE_API_SCOPES, state=state)
    flow.redirect_uri = url_for("auth.oauth2callback", _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    flow.fetch_token(authorization_response=request.url)
    google_api_service = GoogleApiService(flow.credentials.token)
    if not (user_info := google_api_service.get_user_info()):
        return jsonify({"Error": "Unauthorized"}), 401

    if not (user := auth_service.get_user(user_info.id)):
        return jsonify({"Error": "Forbidden"}), 403  # User not allowed to access the application

    if user.google_api_token != flow.credentials.token:
        auth_service.update_user_token(user_info.id, flow.credentials.token)
    login_user(user)
    redirect_url = format_url_for_redirection(session.pop(SessionKey.REDIRECT_URL.value, url_for(PAGE_INDEX_ENDPOINT)))

    return redirect(redirect_url)


@auth_blueprint.route("/logout", methods=["POST"])
def logout() -> tuple[Response, int]:
    redirect_url_from_request = request.args.get("redirect_url", url_for(PAGE_INDEX_ENDPOINT))
    logout_user()

    return jsonify({"redirect_url":  format_url_for_redirection(redirect_url_from_request)}), 200
