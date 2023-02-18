import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = get_file_content('../keys/lab01-api-key.txt')
# you can get API keys for free here - https://api-docs.pgamerx.com/
RSA_API_KEY = get_file_content('../keys/random-api-key.txt')

app = Flask(__name__)


def generate_joke(exclude: str):
    url_base_url = "https://v6.rsa-api.xyz/"
    url_api = "joke"
    url_endpoint = "random"
    url_exclude = ""

    if exclude:
        url_exclude = f"?exclude={exclude}"

    url = f"{url_base_url}/{url_api}/{url_endpoint}{url_exclude}"

    payload = {}
    headers = {"Authorization": RSA_API_KEY}

    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Python Saas.</h2></p>"


@app.route(
    "/api/v1/joke/generate",
    methods=["POST"],
)
def joke_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    exclude = ""
    if json_data.get("exclude"):
        exclude = json_data.get("exclude")

    joke = generate_joke(exclude)

    end_dt = dt.datetime.now()

    result = {
        "event_start_datetime": start_dt.isoformat(),
        "event_finished_datetime": end_dt.isoformat(),
        "event_duration": str(end_dt - start_dt),
        "joke": joke,
    }

    return result


@staticmethod
def get_file_content(file_name):
    f = open(file_name, "r")
    return f.read()