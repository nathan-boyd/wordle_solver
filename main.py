from wordlesolver import WordleSolver
from socialsharer import SocialSharer
import os
from datetime import date
from pathlib import Path
from distutils import util
import logging
from logger import CustomFormatter
from browserwrapper import BrowserWrapper



def get_bool_from_env(env_name, i_logger):
    i_logger.info(f"Getting bool from env var {env_name}")
    env_val = os.getenv(env_name)

    i_logger.info(f"{env_name} value {env_val}")
    if env_val is None:
        raise KeyError(f"ENV var not set {env_name}")

    env_bool = bool(util.strtobool(env_val))
    i_logger.info(f"{env_name} bool value {env_bool}")
    return env_bool


if __name__ == '__main__':

    app_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = f"{app_dir}/logs/{date.today().strftime('%Y-%m-%d')}"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)

    debug = get_bool_from_env("DEBUG", logger)
    in_container = get_bool_from_env("RUNNING_IN_CONTAINER", logger)

    app_dir = os.path.dirname(os.path.realpath(__file__))

    browser_wrapper = BrowserWrapper()
    solver = WordleSolver(in_container, output_dir, browser_wrapper, logger)
    social_sharer = SocialSharer(debug, output_dir, logger)

    try:
        time_to_solve_ms = solver.solve_wordle()
        social_sharer.tweet_results(time_to_solve_ms)
    except Exception as e:
        logger.error(e)
    finally:
        solver.exit_handler()


