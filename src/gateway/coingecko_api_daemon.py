from common.client.coingecko_client import CoinGeckoClient
from common.config.settings import Settings
from common.daemons.heartbeat_handler import make_heartbeat_handler
from gateway.coingecko_base_daemon import CoinGeckoBaseDaemon
from gateway.coingecko_controller import CoinGeckoAPIController
from gateway.coingecko_service import CoinGeckoAPIService


def execute():
    settings = Settings()

    coingecko_client = CoinGeckoClient(
        settings=settings,
    )

    coingecko_api_service = CoinGeckoAPIService(
        settings=settings,
        coingecko_client=coingecko_client,
    )

    coingecko_api_controller = CoinGeckoAPIController(
        service=coingecko_api_service,
    )

    coingecko_base_daemon = CoinGeckoBaseDaemon(
        controller=coingecko_api_controller,
        heartbeat_handler=make_heartbeat_handler(settings=settings),
    )

    coingecko_base_daemon.start()


if __name__ == "__main__":
    execute()
