from common.client.endpoints.base_endpoint import (
    BaseEndpoint,
    HTTPMethod,
    QueryParamsModel,
)


def test_base_endpoint_attributes():
    endpoint = BaseEndpoint(path="/test", method=HTTPMethod.GET)
    assert endpoint.path == "/test"
    assert endpoint.method == "GET"
    assert endpoint.request_model is None
    assert endpoint.response_model is None


def test_http_methods():
    assert HTTPMethod.GET == "GET"
    assert HTTPMethod.POST == "POST"
    assert HTTPMethod.PUT == "PUT"
    assert HTTPMethod.DELETE == "DELETE"


def test_build_query_params_default():
    endpoint = BaseEndpoint(path="/test", method=HTTPMethod.GET)
    result = endpoint.build_query_params(QueryParamsModel())
    assert result == ""
