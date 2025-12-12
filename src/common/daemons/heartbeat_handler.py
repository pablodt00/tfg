import os

import structlog
from structlog.typing import FilteringBoundLogger

from common.config.settings import Settings

default_logger = structlog.get_logger()


def make_heartbeat_handler(
    settings: Settings,
    logger: FilteringBoundLogger = default_logger,
):
    def handler() -> None:
        try:
            with open(settings.HEARTBEAT_FILE, "w", encoding="utf-8") as f:
                f.write(str(os.getpid()))

        except Exception:  # pylint: disable=W0718
            logger.exception("daemon.heartbeat.error")

    return handler
