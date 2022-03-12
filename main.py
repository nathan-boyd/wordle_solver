from wordlesolver import WordleSolver
from socialsharer import SocialSharer
import os
from datetime import date
from pathlib import Path
from distutils import util
from logger import Logger



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
    logwrapper = Logger()
    logger = logwrapper.get_logger()

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
    logwrapper.set_filehandler(output_dir)

    logger.info(f"Configured logging output dir {output_dir}")

    solver = WordleSolver(in_container, output_dir, logger)
    social_sharer = SocialSharer(debug, output_dir, logger)

    try:
        time_to_solve_ms = solver.solve_wordle()
        social_sharer.tweet_results(time_to_solve_ms)
    except Exception as e:
        logger.error(e)
    finally:
        solver.exit_handler()
