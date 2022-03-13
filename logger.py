import logging

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    f1 = "[%(asctime)s] [%(name).4s]"
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
