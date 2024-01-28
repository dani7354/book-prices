from flask import Flask
from bookprices.web.blueprints.api import api_blueprint
from bookprices.web.blueprints.page import page_blueprint, not_found, internal_server_error
from bookprices.web.settings import DEBUG_MODE, FLASK_APP_PORT
from bookprices.web.cache.redis import cache

static_folder = "static"
static_url_path = None
if DEBUG_MODE:
    static_folder = "assets"
    static_url_path = "/static/assets"

app = Flask(__name__, static_url_path=static_url_path, static_folder=static_folder)
app.debug = DEBUG_MODE
app.register_blueprint(api_blueprint, url_prefix="/api")
app.register_blueprint(page_blueprint)
app.register_error_handler(404, not_found)
app.register_error_handler(500, internal_server_error)
cache.init_app(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_APP_PORT)
