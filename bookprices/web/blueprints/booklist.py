import flask
import flask_login
from flask import render_template, current_app, Blueprint
from flask_login import login_required
from sqlalchemy import create_engine
from werkzeug.local import LocalProxy

from bookprices.web.cache.redis import cache
from bookprices.shared.repository.unit_of_work import UnitOfWork
from bookprices.web.service.auth_service import require_member
from bookprices.web.service.booklist_service import BookListService
from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.shared.db_session import SessionFactory
from bookprices.web.shared.enum import HttpMethod, BookListTemplate

booklist_blueprint = Blueprint("booklist", __name__)
logger = LocalProxy(lambda: current_app.logger)


def _create_booklist_service() -> BookListService:
    return BookListService(UnitOfWork(SessionFactory()), cache)


@booklist_blueprint.context_processor
def include_csrf_token() -> dict[str, str]:
    return get_csrf_token()


@booklist_blueprint.route("", methods=[HttpMethod.GET.value])
@login_required
@require_member
def index():
    booklist_service = _create_booklist_service()
    booklists = booklist_service.get_booklists(flask_login.current_user.id)
    return render_template(BookListTemplate.INDEX.value, view_model=booklists)



@booklist_blueprint.route("<int:booklist_id>", methods=[HttpMethod.GET.value])
@login_required
@require_member
def booklist(booklist_id: int) -> str:
    booklist_service = _create_booklist_service()
    booklist = booklist_service.get_booklist(booklist_id, )


