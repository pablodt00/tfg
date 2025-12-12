from typing import Optional

from common.client.endpoints.base_endpoint import (
    BaseEndpoint,
    HTTPMethod,
    QueryParamsModel,
    ResponseModel,
    SnakeCaseModel,
)


class CoinPrice(SnakeCaseModel):
    eur: float


class CoinPriceByIdResponse(ResponseModel):
    btc: Optional[CoinPrice] = None
    eth: Optional[CoinPrice] = None
    usdt: Optional[CoinPrice] = None
    xrp: Optional[CoinPrice] = None
    bnb: Optional[CoinPrice] = None
    usdc: Optional[CoinPrice] = None
    sol: Optional[CoinPrice] = None
    doge: Optional[CoinPrice] = None
    ada: Optional[CoinPrice] = None
    dot: Optional[CoinPrice] = None


class CoinPriceByIdParams(QueryParamsModel):
    vs_currencies: str
    symbols: str
    precision: int


class CoinPriceByIdEndpoint(BaseEndpoint):
    def __init__(self):
        super().__init__(
            path="/simple/price",
            method=HTTPMethod.GET,
            request_model=None,
            response_model=CoinPriceByIdResponse,
            query_params=CoinPriceByIdParams,
        )

    def build_query_params(self, data: CoinPriceByIdParams) -> str:
        return (
            f"vs_currencies={data.vs_currencies}"
            f"&symbols={data.symbols}"
            f"&precision={data.precision}"
        )

    @staticmethod
    def get_default_request():
        return CoinPriceByIdParams(
            vs_currencies="eur",
            symbols="btc,eth,usdt,bnb,xrp,sol,usdc,doge,ada,dot",
            precision=2,
        )
