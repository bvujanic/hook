import threading
from flask import Flask, jsonify, request, make_response, abort
from waitress import serve
from prometheus_client import start_http_server, Counter, Enum
from .upserter import Upserter
from .config import get_env_vars, get_logger
import sys
import requests

if __name__ == "__main__":
    app = Flask(__name__)

    # Prom client metrics
    c = Counter("requests", "HTTP requests for flask api endpoints", ["method", "endpoint"])
    e = Enum("api_health", "api service health", states=["pass", "sick"])

    required_env_vars = ["AUTH_TOKEN", "INFLUX_HOST", "INFLUX_PORT", "INFLUX_USERNAME", "INFLUX_PASSWORD", "INFLUX_DATABASE"]

    try:
        logger = get_logger()
        env_vars = get_env_vars(required_env_vars)

    except Exception as error:  # pylint: disable=broad-except
        logger.critical(("Required environment variable of '%s' was not found." % error))
        sys.exit(1)

    upserter = Upserter(
        influx_host=env_vars["INFLUX_HOST"],
        influx_port=int(env_vars["INFLUX_PORT"]),
        influx_username=env_vars["INFLUX_USERNAME"],
        influx_password=env_vars["INFLUX_PASSWORD"],
        influx_database=env_vars["INFLUX_DATABASE"],
    )

    is_healthy = False

    @app.before_request
    def auth():
        logger.info(f"{request.method}, {request.full_path}")
        if request.endpoint == "get_health":
            return
        """Authenticate the client's API request."""
        if "authorization" in request.headers:
            token = request.headers.get("authorization")
        elif "Authorization" in request.headers:
            token = request.headers.get("Authorization")
        else:
            return abort(403)
        if token != env_vars["AUTH_TOKEN"]:
            return abort(403)

    @app.route("/api/v1/red", methods=["POST"])
    def get_payload():
        c.labels("post", "/api/v1/red").inc()
        payload = request.get_json()
        if payload is None:
            return make_response(jsonify({"error": "No valid payload."}), 400)
        thread = threading.Thread(target=upserter.process_payload, args=(payload,))
        thread.start()
        return ("", 200)

    @app.route("/api/v1/status", methods=["GET"])
    def get_health():
        c.labels("get", "/api/v1/status").inc()
        try:
            r = requests.get(f"http://localhost:8086/health")
            if r.status_code // 100 == 2:
                is_healthy = True
            else:
                is_healthy = False
        except Exception as e:
            print(f"An errorr occurred whilst reaching the db: {e}")
            is_healthy = False
        health = "pass" if is_healthy else "sick"
        return make_response(jsonify({"status": health}), 200)

    def run():
        try:
            logger.info("Starting up prometheus server")
            start_http_server(9000)
            logger.info("Starting up flask server")
            serve(app, listen="*:8080")
        except Exception as e:
            logger.critical(f"Error occurred whilst starting up servers: {e}")
            sys.exit(1)
