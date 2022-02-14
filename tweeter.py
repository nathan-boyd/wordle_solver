import config
import twitter
import os
from datetime import datetime


class Tweeter:

    def verify_auth(self):
        try:
            self.api.verify_credentials()
            print("Twitter Authentication OK")
        except Exception as e:
            print("Error Twitter during authentication")
            print(e)

    def tweet_results(self):
        message = "My wordle solver completed today's puzzle."
        results_dir = f"{os.curdir}/logs/{datetime.today().strftime('%Y-%m-%d')}"
        results_file = f"{results_dir}/game_summary.txt"

        with open(results_file, 'r') as file:
            data = file.read().rstrip()
            message = message + "\n" + data

        if self.DEBUG:
            print("Not tweeting in debug mode")
            print(message)
        else:
            print("Tweeting Results")
            print(message)
            tweet_res = self.api.PostUpdate(message)
            print(tweet_res)

    def __init__(self, debug):
        self.DEBUG = debug
        if self.DEBUG:
            return

        self.api = twitter.Api(consumer_key=config.consumer_key,
                               consumer_secret=config.consumer_secret,
                               access_token_key=config.access_token,
                               access_token_secret=config.access_token_secret)
