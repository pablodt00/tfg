from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Request

from processor.processor_service import ProcessorService


def make_events_router(processor_service: ProcessorService) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/",
        summary="Processes received CloudEvents from Knative Eventing",
        status_code=HTTPStatus.OK,
    )
    async def process_events(request: Request):
        try:
            data = await request.json()
            await processor_service.process_data(data)

            return {
                "status": "success",
                "message": "Event processed successfully",
            }
        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Failed to process event: {e}",
            ) from e

    return router
