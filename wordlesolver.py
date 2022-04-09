import logging
import operator
import os
import string
from collections import Counter
from datetime import date
from itertools import chain
from pathlib import Path
import pytest

MAX_ATTEMPTS = 6
MAX_WORD_LENGTH = 5

ALLOWED_STRINGS_FILE = f"{os.path.dirname(os.path.realpath(__file__))}/allowed_strings.txt"
VALID_CHARS = set(string.ascii_letters)

# set comprehension to generate a set of valid wordle words
STRINGS = {
    word.lower()
    for word in Path(ALLOWED_STRINGS_FILE).read_text().splitlines()
    if len(word) == MAX_WORD_LENGTH and set(word) < VALID_CHARS
}

# a count of letter occurrences in the words list
CHAR_COUNT = Counter(chain.from_iterable(STRINGS))


class FailedSolve(Exception):
    pass


class WordleSolver:
    # a set of all characters and their frequencies
    CHAR_FREQUENCY = {
        char: value / sum(CHAR_COUNT.values())
        for char, value in CHAR_COUNT.items()
    }

    # word scoring function that scores how common the letters are in that word
    def get_commonality(self, word):
        score = 0.0
        for char in word:
            score += self.CHAR_FREQUENCY[char]
        return score / (MAX_WORD_LENGTH - len(set(word)) + 1)

    # sort words by character frequency
    def sort_by_commonality(self, words):
        sort_by = operator.itemgetter(1)
        return sorted(
            [(word, self.get_commonality(word)) for word in words],
            key=sort_by,
            reverse=True,
        )

    def print_frequency(self, word_commonalities):
        for (word, freq) in word_commonalities:
            template = f"{word.upper():<5} | {freq:<5.4}"
            self.logger.info(template)

    @staticmethod
    def apply_vector(word, word_vector):
        for letter, v_letter in zip(word, word_vector):
            if letter not in v_letter:
                return False
        return True

    def filter(self, word_vector, possible_words):
        return [word for word in possible_words if self.apply_vector(word, word_vector)]

    def get_most_likely_word(self, possible_words):
        idx = 0
        sorted_words = self.sort_by_commonality(possible_words)
        word_options_with_same_commonality = [sorted_words[idx]]

        # make a list of words with same commonality as selected word
        while len(sorted_words) > 1 and sorted_words[0][1] == sorted_words[idx + 1][1]:
            word_options_with_same_commonality.append(sorted_words[idx + 1])
            idx += 1

        # alpha sort words with same commonality them for idempotency
        word_options_with_same_commonality.sort(key=lambda y: y[0])

        selected_word = word_options_with_same_commonality[0][0]
        possible_words.remove(selected_word)
        return selected_word

    def solve_wordle(self):

        self.logger.info("##################################################")
        self.logger.info(f"#           Solving Wordle {date.today()}            #")
        self.logger.info("##################################################")

        possible_words = STRINGS.copy()
        word_vector = [set(string.ascii_lowercase) for _ in range(MAX_WORD_LENGTH)]
        start_time_ms = self.util.current_milli_time()

        word = ""
        solved = False
        for attempt_count in range(0, MAX_ATTEMPTS):

            self.logger.info(f"{len(possible_words)} Possible words")
            self.print_frequency(self.sort_by_commonality(possible_words)[:5])

            word = self.get_most_likely_word(possible_words)
            self.logger.info(f"{word.upper()} is the most likely answer")

            letter_results = self.browser_wrapper.submit_word(word, attempt_count)

            self.logger.info(f"Results of {word.upper()}")
            self.evaluate_results(letter_results, word, word_vector)
            if letter_results.count("correct") == MAX_WORD_LENGTH:
                solved = True
                break

            # filter possible words with updated vectors
            possible_words = self.filter(word_vector, possible_words)

        if not solved:
            raise FailedSolve("Failed to solve puzzle")

        end_time_ms = self.util.current_milli_time()
        total_time = end_time_ms - start_time_ms
        self.time_to_solve = total_time - self.time_waiting_ms

        self.logger.info(f"Total time {total_time} ms")
        self.logger.info(f"Time waiting {self.time_waiting_ms} ms")
        self.logger.info(f"Calculated time to solve {self.time_to_solve} ms")
        self.logger.info(f"Solution Word {word.upper()}")

        self.browser_wrapper.save_game_summary()

        return (solved, self.time_to_solve)

    def evaluate_results(self, letter_results, word, word_vector):
        for idx, status in enumerate(letter_results):
            message_template = f"Letter {word[idx].upper()} {status}"
            match status:
                case "correct":
                    self.util.print_green(message_template)
                    word_vector[idx] = {word[idx]}
                case "present":
                    self.util.print_yellow(message_template)
                    word_vector[idx].discard(word[idx])
                case "absent":
                    self.util.print_red(message_template)
                    for vector in word_vector:
                        vector.discard(word[idx])

    def __init__(self, output_dir, browser_wrapper, util):

        self.logger = logging.getLogger("solver")
        self.logger.info('Initializing WordleSolver')

        self.util = util

        # directory for screenshot, logs, and results for twitter
        self.output_dir = output_dir
        self.browser_wrapper = browser_wrapper

        # time spent waiting on wordle to return results or animation tiles
        self.time_waiting_ms = 0

        # time taken to solve the puzzle
        self.time_to_solve = 0

