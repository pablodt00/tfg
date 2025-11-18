import signal


class BaseDaemon:
    rerun = True

    logger = None

    def __init__(self):
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def stop(self, signum, _):
        self.logger.info(
            "%s: Stop signal received. Signal: %s.", self.__class__.__name__, signum
        )
        self.rerun = False

    def start(self):
        self.logger.info("%s: Daemon started.", self.__class__.__name__)

        while self.rerun:

            self.execute()

    def execute(self):
        raise NotImplementedError("Method execute not overridden")
