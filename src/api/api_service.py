from common.config.settings import Settings


class APIService:
    def __init__(
        self,
        settings: Settings,
    ):
        self.settings = settings
