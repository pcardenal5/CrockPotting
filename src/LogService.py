import logging

class LogService():

    def __init__(self) -> None:
        logging.basicConfig(
            encoding='utf-8',
            level=logging.INFO,
            format='%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y/%m/%d %H:%M:%S',
            handlers=[logging.FileHandler("log.txt", mode = 'a')]
        )
        self.logger = logging.getLogger()

    def sendInfo(self, message):
        self.logger.info(message)

    def sendWarning(self, message):
        self.logger.warning(message)
