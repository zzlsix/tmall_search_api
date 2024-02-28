import subprocess

from selenium.webdriver.chrome.options import Options
from selenium import webdriver


class WebDriver:
    def __init__(self):
        self.vars = None
        self.driver = None

    def setup_webdriver(self):
        print("webdriver : set up and start")
        # # 无头模式
        # # command = [
        # #     "chrome",
        # #     "--headless",
        # #     "--remote-debugging-port=9222",
        # #     "--user-data-dir=C:\\Users\\zzlsix\\Desktop\\atmP",
        # #     "https://www.baidu.com"
        # # ]
        #
        # # 有头模式
        # command = [
        #     "chrome",
        #     "--remote-debugging-port=9222",
        #     "--user-data-dir=C:\\Users\\zzlsix\\Desktop\\atmP"
        # ]
        #
        # subprocess.Popen(command)
        options = Options()
        # options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
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

