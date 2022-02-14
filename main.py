from wordle_solver import WordleSolver
from tweeter import Tweeter
import os


if __name__ == '__main__':

    debug = os.getenv("DEBUG")
    if debug.lower() == "true":
        debug = True
    else:
        debug = False

    w = WordleSolver()
    t = Tweeter(debug)

    try:
        w.solve_wordle()
        t.tweet_results()
    finally:
        w.exit_handler()
