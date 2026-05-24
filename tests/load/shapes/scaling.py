# pylint: disable=unused-import
from locust import LoadTestShape

from tests.load.locustfile import HorizontalScalingUser  # noqa: F401


class HorizontalScalingShape(LoadTestShape):
    """
    Prueba 6 – Escalado Horizontal (45 min total):
      0-30 min : linear ramp 10 → 300 users
      30-45 min: linear ramp 300 → 10 users
    """

    RAMP_UP_DURATION = 1800    # 30 min
    RAMP_DOWN_DURATION = 2700  # 45 min total
    MAX_USERS = 300
    MIN_USERS = 10

    def tick(self):
        run_time = self.get_run_time()

        if run_time < self.RAMP_UP_DURATION:
            progress = run_time / self.RAMP_UP_DURATION
            users = int(self.MIN_USERS + (self.MAX_USERS - self.MIN_USERS) * progress)
            return users, 10

        if run_time < self.RAMP_DOWN_DURATION:
            progress = (run_time - self.RAMP_UP_DURATION) / (
                self.RAMP_DOWN_DURATION - self.RAMP_UP_DURATION
            )
            users = int(self.MAX_USERS - (self.MAX_USERS - self.MIN_USERS) * progress)
            return users, 10

        return None
