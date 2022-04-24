import logging

from util import Util


class ColorFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    f1 = "[%(asctime)s] [%(name).6s]"
    f2 = " [%(levelname).4s]"
    f3 = " [%(filename)s:%(lineno)d] %(message)s"

    FORMATS = {
        logging.DEBUG: grey + f1 + grey + f2 + reset + f3,
        logging.INFO: grey + f1 + grey + f2 + reset + f3,
        logging.WARNING: grey + f1 + yellow + f2 + reset + f3,
        logging.ERROR: grey + f1 + red + f2 + reset + f3,
        logging.CRITICAL: grey + f1 + bold_red + f2 + reset + f3
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class FileFormatter(logging.Formatter):
    format = "[%(asctime)s] [%(name).6s] [%(levelname).4s] [%(filename)s:%(lineno)d] %(message)s"

    FORMATS = {
        logging.DEBUG: format,
        logging.INFO: format,
        logging.WARNING: format,
        logging.ERROR: format,
        logging.CRITICAL: format
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class CustomLogger(logging.Logger):

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.DEBUG)

        console = logging.StreamHandler()
        console.setFormatter(ColorFormatter())
        self.addHandler(console)

        util = Util()
        output_dir = util.get_output_directory()

        # single process logging is thread safe, if we multiproc we'll need to change this
        file_handler = logging.FileHandler(f"{output_dir}/wordle.log")
        file_handler.setFormatter(FileFormatter())
        self.addHandler(file_handler)

        return


class LogWrapper:

    def get_logger(self):
        pass


class Logger(LogWrapper):

    @staticmethod
    def get_logger(name):
        logging.setLoggerClass(CustomLogger)
        return logging.getLogger(name)
