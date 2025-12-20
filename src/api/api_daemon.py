from api.api_service import APIService
from api.endpoints.app import build_api
from common.config.settings import Settings


def execute():
    settings = Settings()

    api_service = APIService(settings=settings)

    return build_api(api_service=api_service)


if __name__ == "__main__":
    import os

    import uvicorn

    app_name = os.path.basename(__file__).replace(".py", "")
    uvicorn.run(
        app=f"daemons.{app_name}:execute",
        host="0.0.0.0",
        port=8000,
        workers=1,
        factory=True,
    )
