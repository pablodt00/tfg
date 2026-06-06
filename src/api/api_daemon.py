from api.api_service import APIService
from api.endpoints.app import build_api
from common.config.settings import Settings
from common.database import make_engine, make_session_factory
from common.database.repositories.alert_repository import AlertRepository
from common.database.repositories.coin_repository import CoinRepository


def execute():
    settings = Settings()

    engine = make_engine(
        db_uri=settings.db_uri_as_string,
    )

    session_factory = make_session_factory(
        engine=engine,
    )

    coin_repository = CoinRepository()

    alert_repository = AlertRepository()

    api_service = APIService(
        settings=settings,
        coin_repository=coin_repository,
        alert_repository=alert_repository,
        session_factory=session_factory,
    )

    return build_api(api_service=api_service)


if __name__ == "__main__":
    import os

    import uvicorn

    app_name = os.path.basename(__file__).replace(".py", "")
    uvicorn.run(
        app=f"api.{app_name}:execute",
        host="0.0.0.0",
        port=7654,
        workers=1,
        factory=True,
    )
