import operator
import os
import string
import time
from collections import Counter
from datetime import date
from itertools import chain
from pathlib import Path
from datetime import datetime

import keyboard
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

ALLOWED_STRINGS_FILE = "allowed_words.txt"
VALID_CHARS = set(string.ascii_letters)
MAX_ATTEMPTS = 6
MAX_WORD_LENGTH = 5
WORDLE_URL = "https://www.nytimes.com/games/wordle/index.html"
IMPLICIT_WAIT_SECONDS = 5

# set comprehension to generate a set of valid wordle words
STRINGS = {
    word.lower()
    for word in Path(ALLOWED_STRINGS_FILE).read_text().splitlines()
    if len(word) == MAX_WORD_LENGTH and set(word) < VALID_CHARS
}

# a count of letter occurrences in the words list
CHAR_COUNT = Counter(chain.from_iterable(STRINGS))


class WordleSolver():
    # enumerate each key and value of CHAR_COUNT
    # divide each value by the total count
    CHAR_FREQUENCY = {
        char: value / CHAR_COUNT.total()
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

    @staticmethod
    def print_frequency(word_commonalities):
        for (word, freq) in word_commonalities:
            template = f"{word.upper():<5} | {freq:<5.4}"
            print(template)

    @staticmethod
    def apply_vector(word, word_vector):
        for letter, v_letter in zip(word, word_vector):
            if letter not in v_letter:
                return False
        return True

    def filter(self, word_vector, possible_words):
        return [word for word in possible_words if self.apply_vector(word, word_vector)]

    @staticmethod
    def print_green(skk):
        print("\033[92m{}\033[00m".format(skk))

    @staticmethod
    def print_yellow(skk):
        print("\033[93m{}\033[00m".format(skk))

    @staticmethod
    def print_red(skk):
        print("\033[91m{}\033[00m".format(skk))

    def get_most_likely_word(self, possible_words):
        idx = 0
        sorted_words = self.sort_by_commonality(possible_words)
        options = [sorted_words[idx]]

        # make a list of words with same commonality as selected word
        while len(sorted_words) > 1 and sorted_words[0][1] == sorted_words[idx + 1][1]:
            options.append(sorted_words[idx + 1])
            idx += 1

        # alpha sort words with same commonality them for idempotency
        options.sort(key=lambda y: y[0])
        return options[0][0]

    def submit_word(self, word, attempt, game_board):
        keyboard.write(word, delay=1)
        keyboard.press_and_release('enter')

        rows = game_board.find_elements(By.TAG_NAME, 'game-row')
        row = self.driver.execute_script('return arguments[0].shadowRoot', rows[attempt])
        tiles = row.find_elements(By.CSS_SELECTOR, "game-tile")

        # get last tile from row
        tile_div = self.get_element_from_shadow_with_query(tiles[4], "div")

        # wait for last tile animation to stop
        while tile_div.get_attribute("data-animation") != "idle":
            time.sleep(.5)

        letter_results = []
        for tile in tiles:
            letter_results.append([tile.get_attribute("evaluation")][0])

        return letter_results

    def get_element_from_shadow_by_id(self, element, id):
        tpl = f"return arguments[0].shadowRoot.getElementById('{id}')"
        return self.driver.execute_script(tpl, element)

    def get_element_from_shadow_with_query(self, element, query):
        tpl = f"return arguments[0].shadowRoot.querySelector('{query}')"
        return self.driver.execute_script(tpl, element)

    def solve_wordle(self):

        print("\n\n##################################################")
        print(f"#           Solving Wordle {date.today()}            #")
        print("##################################################")

        # click to close welcome screen
        self.driver.find_element(By.TAG_NAME, 'html').click()

        # the main game div
        game_app = self.driver.find_element(By.TAG_NAME, 'game-app')

        possible_words = STRINGS.copy()
        word_vector = [set(string.ascii_lowercase) for _ in range(MAX_WORD_LENGTH)]

        for attempt in range(0, MAX_ATTEMPTS):
            letter_results, word = self.attempt_solution(attempt, game_app, possible_words, word_vector)
            if 5 == letter_results.count("correct"):
                break
            letter_results.clear()

            # filter possible words with updated
            possible_words = self.filter(word_vector, possible_words)

        print(f"\nWord: {word.upper()}")
        self.report_success(game_app)

    def report_success(self, game_app):
        results_dir = f"{os.curdir}/logs/{datetime.today().strftime('%Y-%m-%d')}"
        os.makedirs(results_dir)

        screen_shot_path = f"{results_dir}/screenshot.png"
        self.driver.save_screenshot(screen_shot_path)

        # wait for game stats to appear
        while self.get_element_from_shadow_with_query(game_app, "#game > game-modal > game-stats") is None:
            time.sleep(.5)

        stats_panel = self.get_element_from_shadow_with_query(game_app, "#game > game-modal > game-stats")
        share_button = self.get_element_from_shadow_with_query(stats_panel, "#share-button")
        share_button.click()
        self.driver.find_element(By.TAG_NAME, 'html').click()

        game_summary = pyperclip.paste()
        print(f"{game_summary}")
        with open(f"{results_dir}/game_summary.txt", 'w') as g:
            g.write(game_summary)

    def attempt_solution(self, attempt, game_app, possible_words, word_vector):
        board = self.get_element_from_shadow_by_id(game_app, "board")

        print(f"\nAttempt {attempt + 1} / {MAX_ATTEMPTS}")
        print(f"{len(possible_words)} Possible words")
        self.print_frequency(self.sort_by_commonality(possible_words)[:5])

        word = self.get_most_likely_word(possible_words)
        print(f"{word.upper()} is the most likely answer")

        possible_words.remove(word)
        letter_results = self.submit_word(word, attempt, board)

        print(f"\nResults of {word.upper()}")
        self.evaluate_results(letter_results, word, word_vector)
        return letter_results, word

    def evaluate_results(self, letter_results, word, word_vector):
        for idx, status in enumerate(letter_results):
            template = f"Letter {word[idx].upper()} {status}"
            match status:
                case "correct":
                    self.print_green(template)
                    word_vector[idx] = {word[idx]}
                case "present":
                    self.print_yellow(template)
                    word_vector[idx].remove(word[idx])
                case "absent":
                    self.print_red(template)
                    for vector in word_vector:
                        vector.remove(word[idx])

    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.implicitly_wait(IMPLICIT_WAIT_SECONDS)
        self.driver.set_window_size(100, 810)
        self.driver.get(WORDLE_URL)

    def exit_handler(self):
        self.driver.close()
