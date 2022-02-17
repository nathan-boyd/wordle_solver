from wordlesolver import WordleSolver
from socialsharer import SocialSharer
import os
from datetime import date
from pathlib import Path
from distutils import util

import queue
import logging
from logging.handlers import QueueHandler


def get_bool_from_env(env_name, i_logger):
    i_logger.info(f"Getting bool from env var {env_name}")
    env_val = os.getenv(env_name)

    i_logger.info(f"{env_name} value {env_val}")
    if env_val is None:
        raise KeyError(f"ENV var not set {env_name}")

    env_bool = bool(util.strtobool(env_val))
    i_logger.info(f"{env_name} bool value {env_bool}")
    return env_bool


def setup_logging(i_formatter):
    que = queue.Queue(-1)
    queue_handler = QueueHandler(que)

    i_logger = logging.getLogger()
    logging.getLogger()
    i_logger.addHandler(queue_handler)

    i_logger.setLevel("INFO")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(i_formatter)
    i_logger.addHandler(console_handler)

    return i_logger


if __name__ == '__main__':
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)4.4s] %(message)s")
    logger = setup_logging(log_formatter)
    logger.info("Initializing main")

    debug = get_bool_from_env("DEBUG", logger)
    in_container = get_bool_from_env("RUNNING_IN_CONTAINER", logger)

    app_dir = os.path.dirname(os.path.realpath(__file__))
    logger.info(f"App dir {app_dir}")

    if in_container:
        output_dir = f"/logs/{date.today().strftime('%Y-%m-%d')}"
    else:
        output_dir = f"{app_dir}/logs/{date.today().strftime('%Y-%m-%d')}"

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    logger.info(f"Logs output dir {output_dir}")

    file_handler = logging.FileHandler(f"{output_dir}/wordle.log")
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    logger.info("Added file handler to logger")

    try:
        solver = WordleSolver(in_container, output_dir, logger)
        social_sharer = SocialSharer(debug, output_dir, logger)
        time_to_solve_ms = solver.solve_wordle()
        social_sharer.tweet_results(time_to_solve_ms)
    finally:
        solver.exit_handler()
