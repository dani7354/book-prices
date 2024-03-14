import google_auth_oauthlib.flow
from enum import Enum
from flask import Blueprint, request, redirect, url_for, session, Response, jsonify
from bookprices.shared.db.database import Database
from bookprices.web.cache.redis import cache
from bookprices.web.service.auth_service import AuthService
from bookprices.web.service.google_api_service import GoogleApiService
from bookprices.web.blueprints.urlhelper import format_url_for_redirection
from bookprices.web.shared.enum import HttpMethod
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
    GOOGLE_API_SCOPES)

PAGE_INDEX_ENDPOINT = "page.index"

auth_blueprint = Blueprint("auth", __name__)
auth_service = AuthService(
    Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE),
    cache)


class SessionKey(Enum):
    STATE = "state"
    REDIRECT_URL = "redirect_url"


@auth_blueprint.route("/authorize", methods=[HttpMethod.GET.value])
def authorize() -> Response:
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      GOOGLE_CLIENT_SECRETS_FILE, scopes=GOOGLE_API_SCOPES)
    flow.redirect_uri = url_for("auth.oauth2callback", _external=True)
    authorization_url, state = flow.authorization_url(
      access_type="offline",
      include_granted_scopes="true")

    session[SessionKey.STATE.value] = state
    session[SessionKey.REDIRECT_URL.value] = redirect_url if (redirect_url := request.args.get("next")) \
        else url_for(PAGE_INDEX_ENDPOINT)

    return redirect(authorization_url)


@auth_blueprint.route("/oauth2callback", methods=[HttpMethod.GET.value])
def oauth2callback() -> Response | tuple[Response, int]:
    if not (state := session.get(SessionKey.STATE.value)):
        return jsonify({"Error": "State not found in session"}), 400
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE, scopes=GOOGLE_API_SCOPES, state=state)
    flow.redirect_uri = url_for("auth.oauth2callback", _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    flow.fetch_token(authorization_response=request.url)
    google_api_service = GoogleApiService(flow.credentials.token)
    if not (user_info := google_api_service.get_user_info()):
        return jsonify({"Error": "User not found"}), 401

    if not (user := auth_service.get_user(user_info.id)) or not user.is_active:
        return jsonify({"Error": "Access not allowed"}), 403  # User not allowed to access the application

    if user.google_api_token != flow.credentials.token or user.image_url != user_info.picture_url:
        auth_service.update_user_token_and_image_url(
            user_id=user_info.id,
            token=flow.credentials.token,
            image_url=user_info.picture_url)
    login_user(user)
    redirect_url = format_url_for_redirection(session.pop(SessionKey.REDIRECT_URL.value, url_for(PAGE_INDEX_ENDPOINT)))

    return redirect(redirect_url)


@auth_blueprint.route("/logout", methods=[HttpMethod.POST.value])
def logout() -> tuple[Response, int]:
    redirect_url_from_request = request.args.get("redirect_url", url_for(PAGE_INDEX_ENDPOINT))
    logout_user()

    return jsonify({"redirect_url":  format_url_for_redirection(redirect_url_from_request)}), 200
