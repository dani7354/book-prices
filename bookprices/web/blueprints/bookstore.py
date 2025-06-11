from flask import Blueprint, current_app, render_template
from flask_login import login_required
from werkzeug.local import LocalProxy

from bookprices.shared.model.user import UserAccessLevel
from bookprices.web.service.auth_service import require_admin, AuthService
from bookprices.web.service.bookstore_service import BookStoreService
from bookprices.shared.db.database import Database
from bookprices.web.mapper.bookstore import map_to_bookstore_list
from bookprices.web.cache.redis import cache
from bookprices.web.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from bookprices.web.shared.enum import BookStoreTemplate

logger = LocalProxy(lambda: current_app.logger)

bookstore_blueprint = Blueprint("bookstore", __name__)


db = Database(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
bookstore_service = BookStoreService(db, cache)


@bookstore_blueprint.route("", methods=["GET"])
@login_required
@require_admin
def index() -> str:
    bookstores = bookstore_service.get_bookstores()
    auth_service = AuthService(db, cache)
    is_admin = auth_service.user_can_access(UserAccessLevel.ADMIN)
    view_model = map_to_bookstore_list(bookstores, current_user_is_admin=is_admin)

    return render_template(BookStoreTemplate.INDEX.value, view_model=view_model)


@bookstore_blueprint.route("edit/<int:bookstore_id>", methods=["POST"])
@login_required
@require_admin
def edit(bookstore_id: int) -> str:
    pass