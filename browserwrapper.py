import logging
from selenium.webdriver.common.by import By
import pyperclip
from pynput.keyboard import Key, Controller
import time

from browserbuilder import BrowserBuilder

WORDLE_URL = "https://www.nytimes.com/games/wordle/index.html"


class BrowserWrapper:

    @staticmethod
    def tile_is_idle(tile):
        return tile.get_attribute("data-animation") == "idle"

    @staticmethod
    def tile_is_not_idle(tile):
        return tile.get_attribute("data-animation") != "idle"

    def check_wait_iter(self, waited_ms, max_waited_ms):
        if waited_ms > max_waited_ms:
            self.shoot_screen("timeout")
            raise TimeoutError("Timed out waiting for results")

    def submit_word(self, word, attempt):
        self.keyboard.type(word)
        self.keyboard.press(Key.enter)

        # get letter rows
        rows = self.game_board.find_elements(By.TAG_NAME, 'game-row')
        row = self.webdriver.execute_script('return arguments[0].shadowRoot', rows[attempt])

        # get tiles from row
        tiles = row.find_elements(By.CSS_SELECTOR, "game-tile")

        # wait for last tile animation to stop
        last_tile = self.get_element_from_shadow_with_query(tiles[4], "div")

        waited_ms = self.wait_for_condition_end(self.tile_is_idle, last_tile)
        self.logger.info(f"Waited {waited_ms}ms for tile animation to start")

        waited_ms = self.wait_for_condition_end(self.tile_is_not_idle, last_tile)
        self.logger.info(f"Waited {waited_ms}ms for tile animation to stop")

        self.shoot_screen(f"attempt_{attempt}")

        letter_results = []
        for tile in tiles:
            letter_results.append([tile.get_attribute("evaluation")][0])

        return letter_results

    def wait_for_condition_end(self, condition, *args):
        wait_ms = 0
        max_wait_ms = 5000
        wait_duration_ms = 50

        # wait for animation to start after submitting
        while condition(*args) and wait_ms < max_wait_ms:
            self.wait(wait_duration_ms)
            wait_ms += wait_duration_ms

        self.check_wait_iter(wait_ms, max_wait_ms)
        return wait_ms

    def wait(self, ms):
        self.time_waiting_ms += ms
        time.sleep(self.util.secs_from_ms(ms))

    def shoot_screen(self, file_name):
        self.webdriver.save_screenshot(f"{self.output_dir}/{file_name}.png")

    def save_game_summary(self):
        # get a screenshot before stats appear
        self.shoot_screen("completed_game")

        # wait for game stats to appear
        while self.get_element_from_shadow_with_query(self.game_app, "#game > game-modal > game-stats") is None:
            self.wait(500)

        # get a screenshot before stats appear
        self.shoot_screen("stats")

        stats_panel = self.get_element_from_shadow_with_query(self.game_app, "#game > game-modal > game-stats")
        share_button = self.get_element_from_shadow_with_query(stats_panel, "#share-button")
        share_button.click()
        self.webdriver.find_element(By.TAG_NAME, 'html').click()

        # get text summary
        game_summary = pyperclip.paste()

        # the linux chromium driver uses white squares instead of black for absent letters
        white_square = "⬜"
        black_square = "⬛"
        game_summary = game_summary.replace(white_square, black_square)

        with open(f"{self.output_dir}/game_summary.txt", 'w') as g:
            g.write(game_summary)

    def get_element_from_shadow_by_id(self, shadow, element_id):
        tpl = f"return arguments[0].shadowRoot.getElementById('{element_id}')"
        return self.webdriver.execute_script(tpl, shadow)

    def get_element_from_shadow_with_query(self, shadow, query):
        tpl = f"return arguments[0].shadowRoot.querySelector('{query}')"
        return self.webdriver.execute_script(tpl, shadow)

    def exit_handler(self):
        self.logger.info("Shutting down webdriver")
        self.webdriver.close()
        self.logger.info("Webdriver is shut down")

    def __init__(self, in_container, output_dir, util):

        self.time_waiting_ms = 0
        self.logger = logging.getLogger("browser")
        self.output_dir = output_dir
        self.util = util

        browser_builder = BrowserBuilder(in_container)
        self.webdriver = browser_builder.build_browser()

        self.logger.info('Opening Wordle URL')
        self.webdriver.get(WORDLE_URL)

        self.logger.info('Accessed %s', WORDLE_URL)
        self.logger.info('Page title: %s', self.webdriver.title)
        self.shoot_screen("init")

        # click to close welcome screen
        self.webdriver.find_element(By.TAG_NAME, 'html').click()

        # the main game div
        self.game_app = self.webdriver.find_element(By.TAG_NAME, 'game-app')
        self.game_board = self.get_element_from_shadow_by_id(self.game_app, "board")

        # keyboard init needs to happen after creation of virtual display
        self.keyboard = Controller()
