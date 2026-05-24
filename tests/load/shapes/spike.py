# pylint: disable=unused-import
from locust import LoadTestShape

from tests.load.locustfile import SpikeLoadUser  # noqa: F401


class SpikeLoadShape(LoadTestShape):
    """
    Prueba 2 – Pico de Carga (15 min total):
      0-5 min   : 10 users  (baseline)
      5-10 min  : ramp up to 200 users (spike)
      10-15 min : ramp down to 10 users (recovery)
    """

    stages = [
        {"duration": 300, "users": 10, "spawn_rate": 5},    # 0-5 min
        {"duration": 600, "users": 200, "spawn_rate": 40},  # 5-10 min
        {"duration": 900, "users": 10, "spawn_rate": 40},   # 10-15 min
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        return None
