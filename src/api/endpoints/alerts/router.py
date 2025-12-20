from fastapi import APIRouter


def make_alerts_router() -> APIRouter:
    router = APIRouter()

    @router.get(
        "/alerts",
        summary="Return a pong health check",
        description="Return a pong health check",
    )
    async def ping():
        return {"ping": "pong"}

    return router
