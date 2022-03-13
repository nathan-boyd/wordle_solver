import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pyvirtualdisplay.display import Display
import os

IMPLICIT_WAIT_SECONDS = 5


class BrowserBuilder:

    def setup_webdriver(self):
        self.logger.info('Setting chrome options')
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")

        self.logger.info('Initializing Chrome browser')
        return webdriver.Chrome(chrome_options=chrome_options, service=Service(ChromeDriverManager().install()))

    def setup_headless_webdriver(self):
        self.logger.info('Setting chrome options')
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--incognito")
        chrome_options.add_experimental_option('prefs', {
            'download.default_directory': os.getcwd(),
            'download.prompt_for_download': False,
        })

        self.logger.info('Initializing Chrome browser')
        return webdriver.Chrome(chrome_options=chrome_options)

    def build_browser(self):
        return self.webdriver

    def __init__(self, in_container):
        self.logger = logging.getLogger("builder")

        match in_container:
            case True:
                self.logger.info('Setting up virtual display')
                self.display = Display(visible=False, size=(800, 600))
                self.display.start()
                self.logger.info('Initialized virtual display')
                self.logger.info('Configuring browser')
                self.webdriver = self.setup_headless_webdriver()
            case False:
                self.logger.info('Configuring browser')
                self.webdriver = self.setup_webdriver()

        self.webdriver.implicitly_wait(IMPLICIT_WAIT_SECONDS)
        self.webdriver.set_window_size(650, 760)
        self.webdriver.set_window_position(0, 0)
