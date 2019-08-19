import logging
from os.path import isfile

LOG_PATH = "./logs/home_security.log"
class Logger:
    __instance = None

    @staticmethod
    def get_instance():
        if Logger.__instance == None:
            Logger()
        return Logger.__instance

    def __init__(self):
        if Logger.__instance == None:
            Logger.__instance = self
            self.logger = self._create_logger()

    def get_logger(self):
        if not isfile(LOG_PATH):
            self.logger = self._create_logger()
        return self.logger

    def _create_logger(self):
        logger = logging.getLogger("Home Security Log")
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(LOG_PATH)
        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(fmt)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger