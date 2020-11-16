from .database import InfluxDB
from prometheus_client import start_http_server, Summary
import json
from jsonschema import validate

REQUEST_TIME = Summary("request_processing_seconds", "Time it took to insert the accepted request into the db")

SCHEMA = {
    "type": "object",
    "properties": {
        "device": {"type": "string"},
        "rps": {"type": "number"},
        "errors": {"type": "number"},
        "time_taken": {"type": "number"},
    },
    "required": ["device", "rps", "time_taken"],
}


class Upserter:
    def __init__(
        self,
        influx_host,
        influx_port,
        influx_username,
        influx_password,
        influx_database,
    ):

        self._influx_host = influx_host
        self._influx_port = influx_port
        self._influx_username = influx_username
        self._influx_password = influx_password
        self._influx_database = influx_database

    @REQUEST_TIME.time()
    def process_payload(self, payload):
        try:
            payload = json.loads(payload)
            self.validate_schema(payload)
            measurement = {
                "measurement": "device_stats",
                "tags": {"device": payload["device"]},
                "fields": {
                    "rps": payload["rps"],
                    "errors": payload["errors"],
                    "time_taken": payload["time_taken"],
                },
            }
            self._write_payload(measurement)
        except Exception as e:
            raise Exception(f"An error occurred, whilst processing the payload: {e}")

    def _write_payload(self, processed_payload):
        try:
            influx_client = InfluxDB(
                self._influx_username,
                self._influx_password,
                host=self._influx_host,
                port=int(self._influx_port),
                database=self._influx_database,
            )
            successful = influx_client.write(
                processed_payload,
                max_retries=2,
                retry_delay=3,
            )
        except Exception as e:
            raise Exception(f"An error: {e} occurred whilst inserting the following payload to the db{processed_payload}")

        influx_client.close()
        return successful

    @staticmethod
    def validate_schema(payload):
        try:
            # Convert to dict due to jsonschema validation requiring an object.
            validate(instance=dict(payload), schema=SCHEMA)
            return True
        except Exception as e:
            raise Exception(f"Invalid json schema, error: {e}")
