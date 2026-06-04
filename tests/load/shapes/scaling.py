# pylint: disable=unused-import
from locust import LoadTestShape

from tests.load.locustfile import HorizontalScalingUser  # noqa: F401


class HorizontalScalingShape(LoadTestShape):
    """
    Prueba 6 – Escalado Horizontal (8 min total):
      0-5 min : linear ramp 10 → 100 users
      5-8 min : linear ramp 100 → 10 users
    """

    RAMP_UP_DURATION = 300    # 5 min
    RAMP_DOWN_DURATION = 480  # 8 min total
    MAX_USERS = 100
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
