import os

from common.config.settings import Settings


def make_heartbeat_handler(
    settings: Settings,
):
    def handler() -> None:
        try:
            with open(settings.HEARTBEAT_FILE, "w", encoding="utf-8") as f:
                f.write(str(os.getpid()))

        except Exception:  # pylint: disable=W0718
            # logger.exception("daemon.heartbeat.error")
            pass

    return handler
