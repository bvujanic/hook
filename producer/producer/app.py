from .rate_mock import RedGenerator


class Producer:
    @staticmethod
    def run():
        for d in ["c_dev1", "c_dev2", "b_dev1", "b_dev2"]:
            RedGenerator(d, "hunter2").run()

        while True:
            pass
