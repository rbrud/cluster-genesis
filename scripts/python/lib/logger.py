import sys
import os.path
import logging


class Logger():
    def __init__(self, file):
        DEFAULT_LOG_LEVEL = getattr(logging, 'WARNING')
        LOG_FILE = 'log.txt'
        LOGGER_PATH = os.path.abspath(
            os.path.dirname(os.path.abspath(__file__)) +
            os.path.sep +
            '..' +
            os.path.sep +
            '..' +
            os.path.sep +
            '..' +
            os.path.sep +
            LOG_FILE)

        self.logger = logging.getLogger(os.path.basename(file))
        self.logger.setLevel(DEFAULT_LOG_LEVEL)
        self.handler = logging.FileHandler(LOGGER_PATH)
        self.handler.setLevel(DEFAULT_LOG_LEVEL)
        self.handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(self.handler)

    def set_level(self, log_level_str):
        log_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_level_str = log_level_str.upper()
        if log_level_str not in log_levels:
            try:
                raise Exception()
            except:
                self.logger.error('Invalid log level: ' + log_level_str)
                sys.exit(1)

        log_level = getattr(logging, log_level_str)
        self.logger.setLevel(log_level)
        self.handler.setLevel(log_level)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)
