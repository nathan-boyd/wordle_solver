import operator
import os
import string
import time
from collections import Counter
from datetime import date
from itertools import chain
from pathlib import Path

import pyperclip
from pynput.keyboard import Key, Controller
from pyvirtualdisplay.display import Display
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

ALLOWED_STRINGS_FILE = f"{os.path.dirname(os.path.realpath(__file__))}/allowed_words.txt"
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


class WordleSolver:
    # enumerate each key and value of CHAR_COUNT
    # divide each value by the total count
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

    def print_green(self, skk):
        self.logger.info("\033[92m{}\033[00m".format(skk))

    def print_yellow(self, skk):
        self.logger.info("\033[93m{}\033[00m".format(skk))

    def print_red(self, skk):
        self.logger.info("\033[91m{}\033[00m".format(skk))

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
        keyboard = Controller()
        keyboard.type(word)
        keyboard.press(Key.enter)
        time.sleep(1)

        # get letter rows
        rows = game_board.find_elements(By.TAG_NAME, 'game-row')
        row = self.webdriver.execute_script('return arguments[0].shadowRoot', rows[attempt])

        # get tiles from row
        tiles = row.find_elements(By.CSS_SELECTOR, "game-tile")

        # wait for last tile animation to stop
        waited = 0
        last_tile = self.get_element_from_shadow_with_query(tiles[4], "div")
        while last_tile.get_attribute("data-animation") != "idle" and waited < 20:
            time.sleep(.5)
            waited += 1

        self.shoot_screen(f"attempt_{attempt}")
        self.logger.info(f"Waited {waited * .5} seconds for results")

        if waited >= 10:
            self.shoot_screen("timeout")
            raise "Timed out waiting for results"

        letter_results = []
        for tile in tiles:
            letter_results.append([tile.get_attribute("evaluation")][0])

        return letter_results

    def get_element_from_shadow_by_id(self, element, id):
        tpl = f"return arguments[0].shadowRoot.getElementById('{id}')"
        return self.webdriver.execute_script(tpl, element)

    def get_element_from_shadow_with_query(self, element, query):
        tpl = f"return arguments[0].shadowRoot.querySelector('{query}')"
        return self.webdriver.execute_script(tpl, element)

    def solve_wordle(self):

        self.logger.info("##################################################")
        self.logger.info(f"#           Solving Wordle {date.today()}            #")
        self.logger.info("##################################################")

        # click to close welcome screen
        self.webdriver.find_element(By.TAG_NAME, 'html').click()

        # the main game div
        game_app = self.webdriver.find_element(By.TAG_NAME, 'game-app')

        possible_words = STRINGS.copy()
        word_vector = [set(string.ascii_lowercase) for _ in range(MAX_WORD_LENGTH)]

        for attempt_count in range(0, MAX_ATTEMPTS):
            letter_results, word = self.attempt_solution(attempt_count, game_app, possible_words, word_vector)
            if letter_results.count("correct") == MAX_WORD_LENGTH:
                break
            letter_results.clear()

            # filter possible words with updated
            possible_words = self.filter(word_vector, possible_words)

        self.logger.info(f"Word: {word.upper()}")
        self.report_success(game_app)

    def report_success(self, game_app):
        self.shoot_screen("game_summary")

        # wait for game stats to appear
        while self.get_element_from_shadow_with_query(game_app, "#game > game-modal > game-stats") is None:
            time.sleep(.5)

        stats_panel = self.get_element_from_shadow_with_query(game_app, "#game > game-modal > game-stats")
        share_button = self.get_element_from_shadow_with_query(stats_panel, "#share-button")
        share_button.click()
        self.webdriver.find_element(By.TAG_NAME, 'html').click()

        game_summary = pyperclip.paste()
        self.logger.info(f"{game_summary}")
        with open(f"{self.output_dir}/game_summary.txt", 'w') as g:
            g.write(game_summary)

    def attempt_solution(self, attempt_count, game_app, possible_words, word_vector):
        board = self.get_element_from_shadow_by_id(game_app, "board")

        self.logger.info(f"Attempt {attempt_count + 1} of {MAX_ATTEMPTS}")
        self.logger.info(f"{len(possible_words)} Possible words")
        self.print_frequency(self.sort_by_commonality(possible_words)[:5])

        word = self.get_most_likely_word(possible_words)
        self.logger.info(f"{word.upper()} is the most likely answer")

        possible_words.remove(word)
        letter_results = self.submit_word(word, attempt_count, board)

        self.logger.info(f"Results of {word.upper()}")
        self.evaluate_results(letter_results, word, word_vector)
        return letter_results, word

    def evaluate_results(self, letter_results, word, word_vector):
        for idx, status in enumerate(letter_results):
            message_template = f"Letter {word[idx].upper()} {status}"
            match status:
                case "correct":
                    self.print_green(message_template)
                    word_vector[idx] = {word[idx]}
                case "present":
                    self.print_yellow(message_template)
                    word_vector[idx].discard(word[idx])
                case "absent":
                    self.print_red(message_template)
                    for vector in word_vector:
                        vector.discard(word[idx])

    def setup_headless_webdriver(self):
        self.logger.info('Setting chrome options..')
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_experimental_option('prefs', {
            'download.default_directory': os.getcwd(),
            'download.prompt_for_download': False,
        })
        self.logger.info('Set chrome options')

        self.logger.info('Initializing Chrome browser')
        return webdriver.Chrome(chrome_options=chrome_options)

    def shoot_screen(self, file_name):
        self.webdriver.save_screenshot(f"{self.output_dir}/{file_name}.png")

    def __init__(self, in_container, app_dir, output_dir, logger):
        self.logger = logger
        self.logger.info('Initializing WordleSolver')

        self.app_directory = app_dir
        self.output_dir = output_dir

        match in_container:
            case True:
                self.logger.info('Setting up virtual display')
                self.display = Display(visible=0, size=(800, 600))
                self.display.start()
                self.logger.info('Initialized virtual display..')
                self.webdriver = self.setup_headless_webdriver()
            case False:
                self.logger.info('Setting up browser')
                self.webdriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

        self.webdriver.implicitly_wait(IMPLICIT_WAIT_SECONDS)

        self.logger.info('Opening Wordle')
        self.webdriver.get(WORDLE_URL)

        self.logger.info('Accessed %s ..', WORDLE_URL)
        self.logger.info('Page title: %s', self.webdriver.title)
        self.shoot_screen("init")

    def exit_handler(self):
        self.logger.info("Shutting down webdriver")
        self.webdriver.close()
        self.logger.info("Webdriver is shut down")
        try:
            if self.display is not None:
                self.logger.info("Shutting down virtual display")
                self.display.stop()
                self.logger.info("Virtual display is shut down")
        except AttributeError:
            self.logger.info("Virtual display not running, no shutdown required")

