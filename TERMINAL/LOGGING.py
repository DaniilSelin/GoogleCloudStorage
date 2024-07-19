import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from dotenv import load_dotenv


class DummyLogger:
    def info(self, msg, *args, **kwargs):
        pass

    def error(self, msg, *args, **kwargs):
        pass


class LOGGING():
    @staticmethod
    def create_log_directory():
        load_dotenv()
        log_dir = os.getenv("PROJECT_LOGGING_PATH")  # Или любой другой путь по вашему усмотрению
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return log_dir

    @staticmethod
    def setup_logging():
        log_dir = LOGGING.create_log_directory()

        # Логгер для информационных сообщений
        logger_info = logging.getLogger('info_logger')
        logger_info.setLevel(logging.INFO)
        handler_info = RotatingFileHandler(f"{log_dir}/info.log", maxBytes=10 * 1024 * 1024, backupCount=5)
        formatter_info = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler_info.setFormatter(formatter_info)
        logger_info.addHandler(handler_info)

        # Логгер для сообщений об ошибках
        logger_error = logging.getLogger('error_logger')
        logger_error.setLevel(logging.ERROR)
        handler_error = RotatingFileHandler(f"{log_dir}/error.log", maxBytes=10 * 1024 * 1024, backupCount=5)
        formatter_error = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s')
        handler_error.setFormatter(formatter_error)
        logger_error.addHandler(handler_error)

        return logger_info, logger_error