from typing import Optional, Type

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_snake


class SnakeCaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_snake, populate_by_name=True)


class RequestModel(SnakeCaseModel): ...


class ResponseModel(SnakeCaseModel): ...


class QueryParamsModel(SnakeCaseModel): ...


class HTTPMethod:
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
class BaseEndpoint:
    def __init__(
        self,
        path: str,
        method: str,
        request_model: Optional[Type[BaseModel]] = None,
        response_model: Optional[Type[BaseModel]] = None,
        query_params: Optional[Type[BaseModel]] = None,
    ):
        self.path = path
        self.method = method
        self.request_model = request_model
        self.response_model = response_model
        self.query_params = query_params

    def build_request_body(self, data: RequestModel) -> RequestModel:
        pass

    def build_query_params(self, _: QueryParamsModel) -> str:
        return ""
