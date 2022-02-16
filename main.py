from wordle_solver import WordleSolver
from socialsharer import SocialSharer
import os
from datetime import date
import logging
from pathlib import Path
from distutils import util


def get_bool_from_env(env_name):
    logging.info(f"Getting bool from env var {env_name}")
    env_val = os.getenv(env_name)

    logging.info(f"{env_name} value {env_val}")
    if env_val is None:
        raise KeyError(f"ENV var not set {env_name}")

    env_bool = bool(util.strtobool(env_val))
    logging.info(f"{env_name}bool value {env_bool}")
    return env_bool


if __name__ == '__main__':

    logging.info("Initializing main")
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)4.4s] %(message)s")
    logger = logging.getLogger()
    logger.setLevel("INFO")

    debug = get_bool_from_env("DEBUG")
    in_container = get_bool_from_env("RUNNING_IN_CONTAINER")

    app_dir = os.path.dirname(os.path.realpath(__file__))
    logger.info(f"App dir {app_dir}")

    if in_container:
        output_dir = f"/logs/{date.today().strftime('%Y-%m-%d')}"
    else:
        output_dir = f"{app_dir}/logs/{date.today().strftime('%Y-%m-%d')}"

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    logger.info(f"Logs dir {output_dir}")

    logger.removeHandler(logging.getLogger().handlers[0])

    file_handler = logging.FileHandler("{0}/{1}.log".format(output_dir, "wordle_log"))
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    logger.info("Added file handler to logger")

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(log_formatter)
    logger.addHandler(consoleHandler)

    logger.info("Added console handler to logger")

    w = None
    try:
        w = WordleSolver(in_container, output_dir, logger)
        t = SocialSharer(debug, output_dir, logger)
        time_to_solve_ms = w.solve_wordle()
        t.tweet_results(time_to_solve_ms)
    finally:
        w.exit_handler()
