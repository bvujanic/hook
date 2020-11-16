import atexit
import time
import datetime
from influxdb import InfluxDBClient, DataFrameClient
from influxdb.exceptions import InfluxDBServerError


class InfluxDB:
    def __init__(
        self,
        username,
        password,
        host="localhost",
        port=8086,
        **kwargs,
    ):
        ssl = kwargs.get("ssl", False)
        verify_ssl = kwargs.get("verify_ssl", False)
        self._database = kwargs.get("database", None)

        self._client = InfluxDBClient(
            host=host,
            port=port,
            username=username,
            password=password,
            ssl=ssl,
            verify_ssl=verify_ssl,
        )
        atexit.register(self.close)

    def read(self, query, **kwargs):
        """Function for reading from InfluxDB.

        Args:
            query          (str) : InfluxQL query string.
            **max_retries  (int) : The maximum number of retry attempts upon failure.
                                   Defaults to 3.
            **retry_delay  (int) : The number of seconds to wait after failures.
                                   Defaults to 1.
            **database     (str) : The database to use.

        Returns:
            list: Returns a list of matching records to your query.

        """
        max_retries = kwargs.get("max_retries", 3)
        retry_delay = kwargs.get("retry_delay", 1)
        database = kwargs.get("database", self._database)
        if not isinstance(database, str):
            raise TypeError(f"Provided database must be of type str not {type(database).__name__}.")
        if not isinstance(query, str):
            raise TypeError(f"Provided query must be of type str not {type(query).__name__}.")
        retry_count = 0
        result = None
        while retry_count < max_retries and result is None:
            try:
                result = self._client.query(query, database=database)
            except InfluxDBServerError:
                retry_count += 1
                time.sleep(retry_delay)
        if result is not None:
            return result
        return result

    def write(self, data, **kwargs):
        """Function for writing to InfluxDB.
        Args:
            data          (list) : List of measurements to write.
            **max_retries  (int) : The maximum number of retry attempts upon failure.
                                   Defaults to 3.
            **retry_delay  (int) : The number of seconds to wait after failures.
                                   Defaults to 1.
            **database     (str) : The database to use.

        Returns:
            bool: Returns True on successful write, and False on failed write.

        """
        max_retries = kwargs.get("max_retries", 3)
        retry_delay = kwargs.get("retry_delay", 1)
        database = kwargs.get("database", self._database)
        data = [data] if not isinstance(data, list) else data
        if not isinstance(database, str):
            raise TypeError(f"Provided database must be of type str not {type(database).__name__}.")
        retry_count = 0
        successful = False
        while retry_count < max_retries and not successful:
            try:
                successful = self._client.write_points(database=database, points=data, batch_size=10000)
            except InfluxDBServerError:
                retry_count += 1
                time.sleep(retry_delay)
        return successful

    def close(self):
        """Close the initialized client."""
        self._client.close()
