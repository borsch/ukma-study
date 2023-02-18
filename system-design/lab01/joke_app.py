import datetime as dt
import json
import os

import requests
from flask import Flask, jsonify, request


def get_file_content(file_name):
    file_dir = os.path.dirname(os.path.realpath('__file__'))
    f = open(os.path.join(file_dir, file_name), "r")
    return f.readline().strip('\n')


API_TOKEN = get_file_content('../keys/lab01-api-key.txt')
RSA_API_KEY = get_file_content('../keys/random-api-key.txt')
RAPID_API_APP_KEY = get_file_content('../keys/rapid-api-app-key.txt')

WEATHER_MAIN_HOURS = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"]

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


def format_weather_response(weather_execution_result):
    forecast = weather_execution_result.get("forecast").get("forecastday")[0]
    forecast_hours = forecast.get("hour")
    main_hours = [
        {
            "time": x.get("time").split(' ')[1],
            "temp_c": x.get("temp_c"),
            "chance_of_rain": x.get("chance_of_rain"),
            "chance_of_snow": x.get("chance_of_snow"),
            "cloud": x.get("cloud")
        }
        for x in forecast_hours if x.get("time").split(' ')[1] in WEATHER_MAIN_HOURS
    ]

    return {
        "maxtemp_c": forecast.get("day").get("maxtemp_c"),
        "mintemp_c": forecast.get("day").get("mintemp_c"),
        "by_hours": main_hours
    }


def get_weather_handler(body):
    url = "https://weatherapi-com.p.rapidapi.com/history.json"
    querystring = {"q":body.get("location"),"dt":body.get("date")}
    headers = {
        "X-RapidAPI-Key": RAPID_API_APP_KEY,
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return format_weather_response(json.loads(response.text))


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

@app.route(
    "/api/v1/weather",
    methods=["POST"],
)
def get_weather():
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    if json_data.get("location") is None or json_data.get("date") is None or json_data.get("requester_name") is None:
        raise InvalidUsage("'location', 'date' & 'requester_name' json body params are required", status_code=400)

    weather_result = get_weather_handler(json_data)

    result = {
        "requester_name": json_data.get("requester_name"),
        "location": json_data.get("location"),
        "date": json_data.get("date"),
        "timestamp": dt.datetime.now().isoformat(),
        "weather": weather_result,
    }

    return result
