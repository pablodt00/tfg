from fastapi import APIRouter


def make_coins_router() -> APIRouter:
    router = APIRouter()

    @router.get(
        "/coins",
        summary="Return a pong health check",
        description="Return a pong health check",
    )
    async def ping():
        return {"ping": "pong"}

    return router
