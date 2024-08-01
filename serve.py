from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import HTTPException
import logging
import argparse
import os

RATE_LIMIT = os.getenv("RATE_LIMIT", "3 per minute")
API_KEY = os.getenv("API_KEY", "rekrutacja2024")
LOG_FILE = os.getenv("LOG_FILE", "app.log")
REQUIRED_FORMAT = {
    "num": (int, float),
    "text": str,
}

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app)


def api_key_rate_limit():
    return RATE_LIMIT if request.headers.get("apikey") != API_KEY else None


def validate_item(item):
    if not isinstance(item, dict):
        return False
    for key, correct_types in REQUIRED_FORMAT.items():
        if key not in item or not isinstance(item[key], correct_types):
            return False
    return True


@app.route("/endpoint", methods=["POST"])
@limiter.limit(api_key_rate_limit)
def endpoint():
    if not request.is_json:
        return jsonify({"error": "Invalid input format, expected JSON"}), 400

    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Invalid input format, expected list"}), 400

    n_valid = [validate_item(item) for item in data].count(True)
    n_invalid = len(data) - n_valid
    return jsonify({"valid": n_valid, "invalid": n_invalid})


@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Exception: {e}")
    if isinstance(e, HTTPException):
        return jsonify({"error": e.description}), e.code
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    logging.info("Starting server...")
    app.run(
        host="0.0.0.0",
        debug=True,
        port=args.port,
    )
