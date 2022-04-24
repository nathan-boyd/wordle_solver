import os
from pyvirtualdisplay.display import Display
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import config
from logger import Logger

IMPLICIT_WAIT_SECONDS = config.implicit_wait_seconds

logger = Logger.get_logger(__name__)


class BrowserBuilder:

    def setup_webdriver(self, in_container):
        logger.info('setting chrome options')
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument('--no-sandbox')
        driver_options.add_argument("--incognito")
        driver_options.add_experimental_option('prefs', {
            'download.default_directory': os.getcwd(),
            'download.prompt_for_download': False,
        })
        logger.info('initializing driver')
        if in_container:
            self.initialize_virtual_display()
            return webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=driver_options)
        return webdriver.Chrome(ChromeDriverManager().install(), chrome_options=driver_options)

    def initialize_virtual_display(self):
        logger.info('setting up virtual display')
        display = Display(visible=False, size=(800, 600))
        display.start()
        logger.info('initialized virtual display')

    def __init__(self, in_container):
        self.webdriver = self.setup_webdriver(in_container)
        self.webdriver.implicitly_wait(IMPLICIT_WAIT_SECONDS)
        self.webdriver.set_window_size(650, 760)
        self.webdriver.set_window_position(0, 0)
