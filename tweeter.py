import twitter
import config


class Tweeter:

    def tweet_results(self):
        message = "My wordle solver completed today's puzzle."
        summary_file = f"{self.output_dir}/game_summary.txt"

        with open(summary_file, 'r') as file:
            data = file.read().rstrip()
            game_summary = message + "\n" + data

        if self.debug:
            self.logger.info("Not sending tweet in debug mode")
            self.logger.info(game_summary)
        else:
            self.logger.info("Tweeting summary")
            self.logger.info(game_summary)
            tweet_res = self.twitter_api.PostUpdate(game_summary)
            self.logger.info(tweet_res)

    def __init__(self, debug, output_dir, logger):
        self.output_dir = output_dir
        self.logger = logger
        self.debug = debug
        self.logs_dir = output_dir
        self.twitter_api = twitter.Api(consumer_key=config.consumer_key,
                                       consumer_secret=config.consumer_secret,
                                       access_token_key=config.access_token,
                                       access_token_secret=config.access_token_secret)
