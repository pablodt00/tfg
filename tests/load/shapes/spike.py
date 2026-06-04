# pylint: disable=unused-import
from locust import LoadTestShape

from tests.load.locustfile import SpikeLoadUser  # noqa: F401


class SpikeLoadShape(LoadTestShape):
    """
    Prueba 2 – Pico de Carga (5 min total):
      0-1 min  : 10 users  (baseline)
      1-3 min  : ramp up to 80 users (spike)
      3-5 min  : ramp down to 10 users (recovery)
    """

    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 5},    # 0-1 min baseline
        {"duration": 180, "users": 80, "spawn_rate": 35},  # 1-3 min spike
        {"duration": 300, "users": 10, "spawn_rate": 35},  # 3-5 min recovery
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        return None
