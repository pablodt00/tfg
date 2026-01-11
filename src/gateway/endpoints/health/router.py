from fastapi import APIRouter


def make_health_router() -> APIRouter:
    router = APIRouter()

    @router.get(
        "/ping",
        summary="Return a pong health check",
        description="Return a pong health check",
    )
    async def ping():
        return {"ping": "pong"}

    return router
