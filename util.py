import time
import os
import logging
from datetime import date
from distutils.util import strtobool


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

    def get_bool_from_env(self, env_name):
        env_val = os.getenv(env_name)

        if env_val is None:
            raise KeyError(f"ENV var not set {env_name}")

        env_bool = bool(strtobool(env_val))
        return env_bool

    def get_app_dir(self):
        return os.path.dirname(os.path.realpath(__file__))

    def get_output_directory(self):
        in_container = self.get_bool_from_env("RUNNING_IN_CONTAINER")

        if in_container:
            output_dir = f"/logs/{date.today().strftime('%Y-%m-%d')}"
        else:
            app_dir = self.get_app_dir()
            output_dir = f"{app_dir}/logs/{date.today().strftime('%Y-%m-%d')}"

        return output_dir

    def __init__(self):
        self.logger = logging.getLogger()
