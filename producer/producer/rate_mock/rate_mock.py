import random
import threading
import queue
import requests
import json
import time

RANDOM_STATES = 50
POST_URL = "http://localhost:8080/api/v1/red"


class RedGenerator:
    def __init__(self, uuid, auth_token=None):
        self._uuid = uuid
        self._token = auth_token

        self.headers = {"Content-type": "application/json", "Accept": "text/plain"}
        if self._token is not None:
            self.headers["Authorization"] = self._token

        self._mq = queue.Queue()
        self._url = POST_URL

    def _generator(self):
        while True:
            req = random.randint(0, RANDOM_STATES)
            errors = req * random.uniform(0, 0.3) * random.random()
            time_taken = (req * random.random()) / 10

            d = {"device": self._uuid, "rps": req, "errors": errors, "time_taken": time_taken}

            self._mq.put(d)

            time.sleep(random.randint(0, 10))

    def _worker(self):
        while True:
            m = self._mq.get()
            self._post_payload(m)
            self._mq.task_done()

    def _post_payload(self, payload):
        try:

            data = json.dumps(payload)
            r = requests.post(self._url, headers=self.headers, json=data)
            if r.status_code // 100 != 2:
                print(f"error occurred whilst posting to the webhook, resp: {r.json()}")

        except Exception as e:
            print(f"An error occurred whilst posting to the webhook, error :{e} {payload}")

    def run(self):
        threading.Thread(target=self._generator, daemon=True).start()
        threading.Thread(target=self._worker, daemon=True).start()
