import logging
import os
from pyvirtualdisplay.display import Display
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

IMPLICIT_WAIT_SECONDS = 5


class BrowserBuilder:

    webdriver = None

    def setup_webdriver(self):
        self.logger.info('setting driver options')
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument("--incognito")
        self.logger.info('initializing driver')
        return webdriver.Chrome(ChromeDriverManager().install(), options=driver_options)

    def setup_headless_webdriver(self):
        self.logger.info('setting chrome options')
        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument('--no-sandbox')
        driver_options.add_argument("--incognito")
        driver_options.add_experimental_option('prefs', {
            'download.default_directory': os.getcwd(),
            'download.prompt_for_download': False,
        })
        self.logger.info('initializing driver')
        return webdriver.Chrome(chrome_options=driver_options)

    def __init__(self, in_container):
        self.logger = logging.getLogger("builder")
        match in_container:
            case True:
                self.logger.info('setting up virtual display')
                self.display = Display(visible=False, size=(800, 600))
                self.display.start()
                self.logger.info('initialized virtual display')
                self.logger.info('configuring browser')
                self.webdriver = self.setup_headless_webdriver()
            case False:
                self.logger.info('configuring browser')
                self.webdriver = self.setup_webdriver()
        self.webdriver.implicitly_wait(IMPLICIT_WAIT_SECONDS)
        self.webdriver.set_window_size(650, 760)
        self.webdriver.set_window_position(0, 0)
