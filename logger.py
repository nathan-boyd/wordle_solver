import queue
import logging
from logging.handlers import QueueHandler


class Logger:

    def get_logger(self):
        return self.logger

    def set_filehandler(self, output_dir):
        file_handler = logging.FileHandler(f"{output_dir}/wordle.log")
        file_handler.setFormatter(self.log_format)
        self.logger.addHandler(file_handler)
        self.logger.info("Added file handler to logger")

    def __init__(self):
        self.log_format = logging.Formatter("[%(asctime)s] [%(levelname)4.4s] [%(filename)s:%(lineno)d] %(message)s")

        que = queue.Queue(-1)
        queue_handler = QueueHandler(que)

        i_logger = logging.getLogger()
        logging.getLogger()
        i_logger.addHandler(queue_handler)

        i_logger.setLevel("INFO")

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.log_format)
        i_logger.addHandler(console_handler)

        self.logger = i_logger
