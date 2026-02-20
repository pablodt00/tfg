from common.client.endpoints.base_endpoint import HTTPMethod
from common.client.endpoints.coin_price_by_id import (
    CoinPrice,
    CoinPriceByIdEndpoint,
    CoinPriceByIdParams,
    CoinPriceByIdResponse,
)


def test_coin_price_by_id_endpoint_attributes():
    endpoint = CoinPriceByIdEndpoint()
    assert endpoint.path == "/simple/price"
    assert endpoint.method == HTTPMethod.GET
    assert endpoint.response_model == CoinPriceByIdResponse


def test_get_default_request():
    params = CoinPriceByIdEndpoint.get_default_request()
    assert params.vs_currencies == "eur"
    assert "btc" in params.symbols
    assert params.precision == 2


def test_build_query_params():
    endpoint = CoinPriceByIdEndpoint()
    params = CoinPriceByIdParams(vs_currencies="eur", symbols="btc,eth", precision=2)
    query = endpoint.build_query_params(params)
    assert "vs_currencies=eur" in query
    assert "symbols=btc,eth" in query
    assert "precision=2" in query


def test_coin_price_by_id_response_optional_fields():
    response = CoinPriceByIdResponse()
    assert response.btc is None
    assert response.eth is None


def test_coin_price():
    price = CoinPrice(eur=50000.0)
    assert price.eur == 50000.0
