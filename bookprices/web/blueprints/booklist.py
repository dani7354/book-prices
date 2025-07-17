from flask import render_template, current_app, Blueprint
from flask_login import login_required
from werkzeug.local import LocalProxy

from bookprices.web.service.csrf import get_csrf_token
from bookprices.web.shared.enum import HttpMethod, BookListTemplate

booklist_blueprint = Blueprint("booklist", __name__)
logger = LocalProxy(lambda: current_app.logger)


@booklist_blueprint.context_processor
def include_csrf_token() -> dict[str, str]:
    return get_csrf_token()

@booklist_blueprint.route("", methods=[HttpMethod.GET.value])
@login_required
def index():
    return render_template(BookListTemplate.INDEX.value)