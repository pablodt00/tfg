import random

from locust import HttpUser, TaskSet, between, constant, task


COINS = ["btc", "eth", "usdt", "bnb", "xrp", "sol", "usdc", "doge", "ada", "dot"]
CONDITIONS = ["GREATER_THAN_OR_EQUAL", "LESS_THAN_OR_EQUAL"]
ALERT_AMOUNTS = {
    "btc": (20000.0, 80000.0),
    "eth": (1000.0, 5000.0),
    "usdt": (0.9, 1.1),
    "bnb": (100.0, 800.0),
    "xrp": (0.3, 2.0),
    "sol": (10.0, 200.0),
    "usdc": (0.9, 1.1),
    "doge": (0.05, 0.5),
    "ada": (0.2, 1.5),
    "dot": (3.0, 30.0),
}


def _random_alert_payload() -> dict:
    coin = random.choice(COINS)
    low, high = ALERT_AMOUNTS[coin]
    return {
        "coin": coin,
        "amount": round(random.uniform(low, high), 2),
        "email": f"user{random.randint(1, 100)}@test.com",
        "condition": random.choice(CONDITIONS),
    }


class StandardAPIBehavior(TaskSet):
    @task(3)
    def get_coins(self):
        self.client.get("/coins/coins", name="GET /coins/coins")

    @task(1)
    def create_alert(self):
        self.client.post(
            "/alerts/add",
            json=_random_alert_payload(),
            name="POST /alerts/add",
        )

    @task(1)
    def health_check(self):
        self.client.get("/health/ping", name="GET /health/ping")


class ReadHeavyBehavior(TaskSet):

    @task(5)
    def get_coins(self):
        self.client.get("/coins/coins", name="GET /coins/coins")

    @task(1)
    def create_alert(self):
        self.client.post(
            "/alerts/add",
            json=_random_alert_payload(),
            name="POST /alerts/add",
        )

    @task(2)
    def health_check(self):
        self.client.get("/health/ping", name="GET /health/ping")


class AlertHeavyBehavior(TaskSet):
    @task(1)
    def get_coins(self):
        self.client.get("/coins/coins", name="GET /coins/coins")

    @task(4)
    def create_alert(self):
        self.client.post(
            "/alerts/add",
            json=_random_alert_payload(),
            name="POST /alerts/add",
        )

    @task(1)
    def health_check(self):
        self.client.get("/health/ping", name="GET /health/ping")


class SustainedLoadUser(HttpUser):
    """Prueba 1: Carga Sostenida – 50 usuarios concurrentes, 30 minutos."""

    tasks = [StandardAPIBehavior]
    wait_time = between(1, 3)


class SpikeLoadUser(HttpUser):
    """Prueba 2: Pico de Carga – used with tests/load/shapes/spike.py."""

    tasks = [ReadHeavyBehavior]
    wait_time = between(0.5, 2)


class ColdStartUser(HttpUser):
    """Prueba 3: Cold Start – 50 usuarios enviados simultáneamente tras inactividad."""

    tasks = [ReadHeavyBehavior]
    wait_time = constant(0)


class EventProcessingUser(HttpUser):
    """Prueba 4: Procesamiento de Eventos – tráfico
    ligero mientras el pipeline trabaja."""

    tasks = [AlertHeavyBehavior]
    wait_time = between(3, 8)



class ResilienceUser(HttpUser):
    """Prueba 5: Resiliencia – carga sostenida mientras se inyectan fallos."""

    tasks = [StandardAPIBehavior]
    wait_time = between(1, 3)

    def on_start(self):
        self.client.get("/health/ping", name="GET /health/ping (warmup)")


class HorizontalScalingUser(HttpUser):
    """Prueba 6: Escalado Horizontal – used with tests/load/shapes/scaling.py."""

    tasks = [ReadHeavyBehavior]
    wait_time = between(0.5, 2)
