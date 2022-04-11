import logging
import os
import traceback
from pathlib import Path

from browserwrapper import BrowserWrapper
from logger import CustomLogger
from socialsharer import SocialSharer
from util import Util
from wordlesolver import WordleSolver

if __name__ == '__main__':
    util = Util()
    debug = util.get_bool_from_env("DEBUG")
    in_container = util.get_bool_from_env("RUNNING_IN_CONTAINER")
    app_dir = os.path.dirname(os.path.realpath(__file__))

    output_dir = util.get_output_directory()
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    logging.setLoggerClass(CustomLogger)
    logger = logging.getLogger("main")
    logger.info("Initializing main")

    browser_wrapper = BrowserWrapper(in_container, output_dir, util)
    solver = WordleSolver(output_dir, browser_wrapper, util)
    social_sharer = SocialSharer(debug, output_dir)

    try:
        solved, time_to_solve_ms = solver.solve_wordle()
        social_sharer.tweet_results(solved, time_to_solve_ms)
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
