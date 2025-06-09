import google_auth_oauthlib.flow
from flask import Blueprint, request, redirect, url_for, session, Response, jsonify, abort, current_app
from werkzeug.local import LocalProxy
from bookprices.shared.db.database import Database
from bookprices.web.blueprints.error_handler import (
    not_found_api, internal_server_error_api, bad_request_api, forbidden_api, unauthorized_api)
from bookprices.web.cache.redis import cache
from bookprices.web.service.auth_service import AuthService
from bookprices.web.service.google_api_service import GoogleApiService
from bookprices.web.blueprints.urlhelper import format_url_for_redirection
from bookprices.web.shared.enum import HttpMethod, HttpStatusCode, SessionKey, Endpoint
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


REDIRECT_URL_PARAMETER = "redirect_url"

logger = LocalProxy(lambda: current_app.logger)

auth_blueprint = Blueprint("auth", __name__)
auth_blueprint.register_error_handler(HttpStatusCode.BAD_REQUEST, bad_request_api)
auth_blueprint.register_error_handler(HttpStatusCode.NOT_FOUND, not_found_api)
auth_blueprint.register_error_handler(HttpStatusCode.INTERNAL_SERVER_ERROR, internal_server_error_api)
auth_blueprint.register_error_handler(HttpStatusCode.UNAUTHORIZED, unauthorized_api)
auth_blueprint.register_error_handler(HttpStatusCode.FORBIDDEN, forbidden_api)

auth_service = AuthService(
    Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE),
    cache)


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
        else url_for(Endpoint.PAGE_INDEX.value)

    logger.info("Redirecting to Google OAuth2 authorization URL...")

    return redirect(authorization_url)


@auth_blueprint.route("/oauth2callback", methods=[HttpMethod.GET.value])
def oauth2callback() -> Response | tuple[Response, int]:
    if not (state := session.get(SessionKey.STATE.value)):
        abort(HttpStatusCode.BAD_REQUEST, "State not found in session")
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE, scopes=GOOGLE_API_SCOPES, state=state)
    flow.redirect_uri = url_for("auth.oauth2callback", _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    flow.fetch_token(authorization_response=request.url)
    google_api_service = GoogleApiService(flow.credentials.token)
    if not (user_info := google_api_service.get_user_info()):
        abort(HttpStatusCode.UNAUTHORIZED, "User not found")

    is_first_time_login = False
    if not (user := auth_service.get_user(user_info.id)):
        logger.info(f"User {user_info.email} does not exist. Creating new user with ID {user_info.id}...")
        auth_service.create_user(
            id_=user_info.id,
            email=user_info.email,
            access_token=flow.credentials.token,
            image_url=user_info.picture_url)
        logger.info(f"New user {user_info.email} created.")
        is_first_time_login = True
        user = auth_service.get_user(user_info.id)
        if not user:
            logger.error(f"User {user_info.email} could not be created.")
            abort(HttpStatusCode.UNAUTHORIZED, "Something went wrong while creating the new user")

    if not user.is_active:
        abort(HttpStatusCode.FORBIDDEN, f"Access not allowed. User {user.email} has been locked out")

    if not is_first_time_login and (user.google_api_token != flow.credentials.token or user.image_url != user_info.picture_url):
        logger.info("Updating token and image URL for user %s", user_info.email)
        auth_service.update_user_token_and_image_url(
            user_id=user_info.id,
            token=flow.credentials.token,
            image_url=user_info.picture_url)

    logger.info("Logging in user %s", user_info.email)
    login_user(user)
    if is_first_time_login:
        redirect_url = url_for(Endpoint.USER_EDIT_CURRENT.value)
    else:
        redirect_url = format_url_for_redirection(
            session.pop(SessionKey.REDIRECT_URL.value, url_for(Endpoint.PAGE_INDEX.value)))

    return redirect(redirect_url)


@auth_blueprint.route("/logout", methods=[HttpMethod.POST.value])
def logout() -> tuple[Response, int]:
    redirect_url_from_request = request.args.get(REDIRECT_URL_PARAMETER, url_for(Endpoint.PAGE_INDEX.value))
    logout_user()

    return jsonify({REDIRECT_URL_PARAMETER:  format_url_for_redirection(redirect_url_from_request)}), HttpStatusCode.OK
