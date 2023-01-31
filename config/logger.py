import os
import time
import logging
from logging.handlers import RotatingFileHandler
from .constants import Constants as constants


class Logging:
    """
    Class for Logger
    """

    # Intialize Logger
    logger = None

    def __init__(self, file_name):
        self.logger = logging.getLogger(file_name)
        self.formatter = logging.Formatter(
            constants.LOG_FORMAT, datefmt=constants.LOG_DATE_FORMAT)
        logging.Formatter.converter = time.gmtime
        self.set_file_handler()
        self.set_stream_handler()
        self.set_log_level(constants.LOG_LEVEL)

    def set_file_handler(self):
        # Set Rotating File Handler
        self.check_log_path(constants.LOG_BASE_FOLDER)
        file_handler = RotatingFileHandler(
            constants.LOG_FILE_PATH,
            maxBytes=constants.LOG_MAX_FILE_SIZE,
            backupCount=constants.LOG_BACKUP_COUNT)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def set_stream_handler(self):
        # Set Stream Handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(stream_handler)

    def set_log_level(self, level):
        """
        Convert log level from string object to logging class object

        Args:
            level ([string]): [log level to be set for the application]

        Returns:
            [level]: [log level object of class logging]
        """

        if level.lower() == "debug":
            self.logger.setLevel(logging.DEBUG)
        elif level.lower() == "info":
            self.logger.setLevel(logging.INFO)
        elif level.lower() == "warning":
            self.logger.setLevel(logging.WARNING)
        elif level.lower() == "error":
            self.logger.setLevel(logging.ERROR)
        elif level.lower() == "critical":
            self.logger.setLevel(logging.CRITICAL)
        else:
            self.logger.setLevel(logging.WARNING)

    def check_log_path(self, path):
        if not os.path.isdir(path):
            os.mkdir(path)


def get_logger(file_name):
    log = Logging(file_name)
    return log.logger
