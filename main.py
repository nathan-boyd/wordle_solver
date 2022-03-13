from wordlesolver import WordleSolver
from socialsharer import SocialSharer
import os
from datetime import date
from pathlib import Path
from distutils import util
import logging
from logger import CustomLogger
from browserwrapper import BrowserWrapper
import traceback
from util import Util


def get_bool_from_env(env_name):
    env_val = os.getenv(env_name)

    if env_val is None:
        raise KeyError(f"ENV var not set {env_name}")

    env_bool = bool(util.strtobool(env_val))
    return env_bool


if __name__ == '__main__':

    debug = get_bool_from_env("DEBUG")
    in_container = get_bool_from_env("RUNNING_IN_CONTAINER")
    app_dir = os.path.dirname(os.path.realpath(__file__))

    if in_container:
        output_dir = f"/logs/{date.today().strftime('%Y-%m-%d')}"
    else:
        output_dir = f"{app_dir}/logs/{date.today().strftime('%Y-%m-%d')}"

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    logging.setLoggerClass(CustomLogger)
    logger = logging.getLogger("main")
    logger.info("Initializing main")

    util = Util()
    browser_wrapper = BrowserWrapper(in_container, output_dir, util)
    solver = WordleSolver(output_dir, browser_wrapper, util)
    social_sharer = SocialSharer(debug, output_dir)

    try:
        time_to_solve_ms = solver.solve_wordle()
        social_sharer.tweet_results(time_to_solve_ms)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
