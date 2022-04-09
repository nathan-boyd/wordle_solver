import time
import logging


class Util:

    def current_milli_time(self):
        return round(self.ms_from_secs(time.time()))

    def secs_from_ms(self, ms):
        return ms / 1000

    def ms_from_secs(self, seconds):
        return seconds * 1000

    def print_green(self, message):
        self.logger.info("\033[92m{}\033[00m".format(message))

    def print_yellow(self, message):
        self.logger.info("\033[93m{}\033[00m".format(message))

    def print_red(self, message):
        self.logger.info("\033[91m{}\033[00m".format(message))

    def __init__(self):
        self.logger = logging.getLogger()
