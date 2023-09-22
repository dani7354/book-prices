from flask import Blueprint, jsonify, request

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/all")
def index():
    return jsonify({"message": "Hello, World!"})
