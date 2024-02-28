import random
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from SliderHandler import SliderHandler


class Login:
    def __init__(self, driver, vars):
        self.driver = driver
        self.vars = vars

    def login(self, username, password):
        print("log in")

        # 打开登录页面
        self.driver.get("https://login.taobao.com/member/login.jhtml")

        # 如果是二维码 切换登录样式为账户密码
        try:
            WebDriverWait(self.driver, 5).until(
                expected_conditions.visibility_of_element_located(
                    (By.XPATH, "//div[contains(@class,'qrcode-bottom-links')]/a[@target='_self']"))
            )
            self.driver.find_element(By.XPATH,
                                     "//div[contains(@class,'qrcode-bottom-links')]/a[@target='_self']").click()
        except TimeoutException:
            print("no qrcode")

        # 输入username和password
        username_input = self.driver.find_element(By.XPATH, "//input[@id='fm-login-id']")
        password_input = self.driver.find_element(By.XPATH, "//input[@id='fm-login-password']")
        username_input.send_keys(username)
        time.sleep(random.randint(1, 3))
        password_input.send_keys(password)
        time.sleep(random.randint(1, 3))

        # 先点击登录按钮 1.如果登录成功则不做处理 ；2.如果不成功 这里是为了避免漏掉滑块检测，确保触发滑块
        self.driver.find_element(By.XPATH, "//div[@class='fm-btn']/button").click()

        # 登录时滑块检测
        try:
            WebDriverWait(self.driver, 5).until(
                expected_conditions.visibility_of_element_located(
                    (By.XPATH, "//iframe[@id='baxia-dialog-content']"))
            )
            print("***slider appears : before log in ***")
            time.sleep(5)
            SliderHandler.slider_handler_items(self.driver)
            time.sleep(random.randint(2, 3))

            # 如果有滑块 再次点击登录按钮
            self.driver.find_element(By.XPATH, "//div[@class='fm-btn']/button").click()
        except TimeoutException:
            print("before log in : no slider")

        # 登录后滑块检测
        try:
            WebDriverWait(self.driver, 5).until(
                expected_conditions.visibility_of_element_located(
                    (By.XPATH, "//div[contains(@class,'nc')]/span"))
            )
            print("***slider appears : after log in ***")
            SliderHandler.drag_slider(self.driver)
        except TimeoutException:
            print("after log in : no slider")
