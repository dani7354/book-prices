from flask import Flask
from bookprices.web.blueprints.api import api_blueprint
from bookprices.web.blueprints.page import page_blueprint
from bookprices.web.settings import DEBUG_MODE, FLASK_APP_PORT

app = Flask(__name__)
app.debug = DEBUG_MODE
app.register_blueprint(api_blueprint, url_prefix="/api")
app.register_blueprint(page_blueprint)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_APP_PORT)
