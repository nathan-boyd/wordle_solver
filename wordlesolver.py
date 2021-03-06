import logging
import operator
import os
import string
from collections import Counter
from datetime import date
from itertools import chain
from pathlib import Path
from result import Result

MAX_ATTEMPTS = 6
MAX_WORD_LENGTH = 5

ALLOWED_STRINGS_FILE = f"{os.path.dirname(os.path.realpath(__file__))}/allowed_strings.txt"
VALID_CHARS = set(string.ascii_letters)

# set comprehension to generate a set of valid wordle words
WORDS = {
    word.split(',')[1].lower()
    for word in Path(ALLOWED_STRINGS_FILE).read_text().splitlines()
}

# a list of words marked as common, sourced from the google 10000 list
COMMON_WORDS = {
    word.split(',')[1].lower()
    for word in Path(ALLOWED_STRINGS_FILE).read_text().splitlines()
    if word.split(',')[0] == '1'
}

# a count of letter occurrences in the words list
CHAR_COUNT = Counter(chain.from_iterable(WORDS))

# a set of all characters and their frequencies in WORDS
CHAR_FREQUENCY = {
    char: value / sum(CHAR_COUNT.values())
    for char, value in CHAR_COUNT.items()
}


class WordleSolver:
    # word scoring function that determines how common the letters are in a given word.
    # adds preference for common words in attempts > 2
    def get_commonality(self, word, attempt):
        score = 0.0
        for char in word:
            score += CHAR_FREQUENCY[char]
        if attempt > 3 and word in COMMON_WORDS:
            score += 1
            self.logger.info(f"added common word preference to {word}")
        return score / (MAX_WORD_LENGTH - len(set(word)) + 1)

    # sort words by character frequency
    def sort_by_commonality(self, words, attempt):
        sort_by = operator.itemgetter(1)
        return sorted(
            [(word, self.get_commonality(word, attempt)) for word in words],
            key=sort_by,
            reverse=True,
        )

    # prints the commonality of the supplied list of words
    def print_frequency(self, word_commonalities):
        for (word, freq) in word_commonalities:
            template = f"{word.upper():<5} | {freq:<5.4}"
            self.logger.info(template)

    def apply_vector(self, word, word_vector):
        for letter, v_letter in zip(word, word_vector):
            if letter not in v_letter:
                return False
        return True

    def filter(self, word_vector, possible_words):
        return [word for word in possible_words if self.apply_vector(word, word_vector)]

    def get_most_likely_word(self, possible_words, attempt):
        if len(possible_words) <= 0:
            self.logger.error("all words eliminated")

        idx = 0
        sorted_words = self.sort_by_commonality(possible_words, attempt)
        word_options_with_same_commonality = [sorted_words[idx]]

        # make a list of words with same commonality as selected word
        while len(sorted_words) > 1 and sorted_words[0][1] == sorted_words[idx + 1][1]:
            word_options_with_same_commonality.append(sorted_words[idx + 1])
            idx += 1

        # alpha sort words with same commonality them for idempotency
        word_options_with_same_commonality.sort(key=lambda y: y[0])

        selected_word = word_options_with_same_commonality[0][0]
        possible_words.remove(selected_word)
        return selected_word, sorted_words[:5]

    def solve_wordle(self):
        start_time_ms = self.util.current_milli_time()
        self.logger.info(f"solving wordle {date.today()}")
        solved, word = self.solve()

        end_time_ms = self.util.current_milli_time()
        total_time = end_time_ms - start_time_ms
        self.time_to_solve = total_time - self.time_waiting_ms
        self.logger.info(f"time waiting {self.time_waiting_ms} ms")
        self.logger.info(f"calculated time to solve {self.time_to_solve} ms")

        if solved:
            self.logger.info(f"solution word is: {word.upper()}")
        self.browser_wrapper.save_game_summary()
        return solved, self.time_to_solve

    def solve(self):
        possible_words = WORDS.copy()
        word_vector = [set(string.ascii_lowercase) for _ in range(MAX_WORD_LENGTH)]

        for attempt_count in range(0, MAX_ATTEMPTS):
            self.logger.info(f"beginning attempt {attempt_count}/{MAX_ATTEMPTS}")
            self.logger.info(f"{len(possible_words)} possible words")

            word, top_candidates = self.get_most_likely_word(possible_words, attempt_count)
            self.print_frequency(top_candidates)
            self.logger.info(f"{word.upper()} is the most likely answer")

            letter_results = self.browser_wrapper.submit_word(word, attempt_count)
            self.logger.info(f"results of {word.upper()}")

            self.evaluate_results(letter_results, word, word_vector)
            if letter_results.count(Result.CORRECT) == MAX_WORD_LENGTH:
                return True, word

            possible_words = self.filter(word_vector, possible_words)
        return False, ""

    def evaluate_results(self, letter_results, word, word_vector):
        for idx, status in enumerate(letter_results):
            message_template = f"letter {word[idx].upper()} {status}"
            match status:
                case Result.CORRECT:
                    self.logger.info(message_template)
                    word_vector[idx] = {word[idx]}
                case Result.PRESENT:
                    self.logger.info(message_template)
                    word_vector[idx].discard(word[idx])
                case Result.ABSENT:
                    self.logger.info(message_template)
                    for vector in word_vector:
                        if len(vector) != 1:
                            vector.discard(word[idx])

    def __init__(self, output_dir, browser_wrapper, util):
        self.logger = logging.getLogger("solver")
        self.logger.info('initializing wordleSolver')

        self.util = util

        # directory for screenshot, logs, and results for twitter
        self.output_dir = output_dir
        self.browser_wrapper = browser_wrapper

        # time spent waiting on wordle to return results or animation tiles
        self.time_waiting_ms = 0

        # time taken to solve the puzzle
        self.time_to_solve = 0
