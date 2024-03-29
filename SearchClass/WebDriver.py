import subprocess

from selenium.webdriver.chrome.options import Options
from selenium import webdriver


class WebDriver:
    def __init__(self):
        self.vars = None
        self.driver = None

    def setup_webdriver(self):
        print("webdriver : set up and start")
        options = Options()
        options.add_argument("--autoplay-policy=no-user-gesture-required")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.driver = webdriver.Chrome(options=options)
        self.vars = {}
        self.driver.maximize_window()
        return self.driver, self.vars

    # 退出webdriver
    def end_webdriver(self):
        print("webdriver : end up")
        self.driver.quit()

