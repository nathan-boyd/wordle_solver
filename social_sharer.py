import re

import twitter

import twitter_config
from logger import Logger

logger = Logger.get_logger(__name__)


class SocialSharer:

    def tweet_results(self, solved, time_to_solve_ms):
        solve_time_seconds = round((time_to_solve_ms * .001), 4)
        summary_file = f"{self.output_dir}/game_summary.txt"

        with open(summary_file, 'r') as file:
            data = file.read().rstrip()

        regex = r".*Wordle\ (\d{3})"
        game_number = match.group(1) if (match := re.search(regex, data)) else ''

        if solved:
            message = f"My #wordle solver completed #wordle{game_number} in {solve_time_seconds} seconds."
        else:
            message = f"My #wordle solver couldn't quite figure out #wordle{game_number}."

        game_summary = message + "\n" + data

        if self.debug:
            logger.info("not sending tweet in debug mode")
            logger.info(game_summary)
        else:
            logger.info("tweeting summary")
            logger.info(game_summary)
            tweet_res = self.twitter_api.PostUpdate(game_summary)
            logger.info(tweet_res)

    def __init__(self, debug, output_dir):
        self.output_dir = output_dir
        self.debug = debug
        self.logs_dir = output_dir
        self.twitter_api = twitter.Api(consumer_key=twitter_config.consumer_key,
                                       consumer_secret=twitter_config.consumer_secret,
                                       access_token_key=twitter_config.access_token,
                                       access_token_secret=twitter_config.access_token_secret)
