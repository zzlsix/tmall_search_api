import random
import time

from Message import Message
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException


class SliderHandler:
    @staticmethod
    def slider_handler_iframe(driver):
        # 获取滑块
        frame_element = driver.find_element(By.XPATH, "//iframe[@id='baxia-dialog-content']")
        driver.switch_to.frame(frame_element)
        SliderHandler.drag_slider(driver)
        driver.switch_to.default_content()

    @staticmethod
    def drag_slider(driver):
        print("drag slider")
        slider_disappear = False
        while not slider_disappear:

            # 获取滑块
            slider = driver.find_element(By.XPATH, "//div[contains(@class,'nc')]/span")
            actions = ActionChains(driver)
            actions.move_to_element_with_offset(slider, -1, 0).click_and_hold().perform()

            distance = driver.find_element(By.XPATH, "//div[@class='nc_scale']//span[@data-nc-lang='SLIDE']").size[
                'width']

            # 执行移动滑块
            SliderHandler.finish_drag_slider(actions, distance)

            # 释放滑块
            actions.release().perform()

            try:
                # 遇到失败重试
                WebDriverWait(driver, 5).until(
                    expected_conditions.presence_of_element_located(
                        (By.XPATH, "//div[@class='errloading']"))
                )
                div_body = driver.find_element(By.XPATH, "//div[@class='errloading']")
                div_body.click()
                SliderHandler.drag_slider(driver)
            except TimeoutException:
                slider_disappear = True

    @staticmethod
    def finish_drag_slider(actions, distance):
        # 定义速度参数
        pullback = random.randint(15, 25)  # 回拉距离
        current_offset = 0  # 当前位移
        speed = 0
        while current_offset < distance:
            # 计算当前速度
            if current_offset < distance-60:
                speed = random.randint(120, 140)
            if current_offset >= distance-60:
                speed = random.randint(20, 60)
            # 移动滑块
            current_offset += speed
            actions.move_by_offset(speed, 0).perform()
            time.sleep(0.1)  # 等待一小段时间

            # 到达目标位置时进行微小的回拉动作
            if current_offset >= 300 - pullback:
                actions.move_by_offset(-pullback, 0).perform()
                time.sleep(0.1)
                actions.move_by_offset(pullback, 0).perform()

    @staticmethod
    def check_slider(driver, log):
        try:
            # 检查是否为 iframe类型滑块
            WebDriverWait(driver, 5).until(expected_conditions.visibility_of_element_located(
                (By.XPATH, "//iframe[@id='baxia-dialog-content']")))
            print(log)
            SliderHandler.slider_handler_iframe(driver)

        except TimeoutException:

            try:
                WebDriverWait(driver, 5).until(
                    expected_conditions.visibility_of_element_located(
                        (By.XPATH, "//div[contains(@class,'nc')]/span"))
                )
                print(log)
                SliderHandler.drag_slider(driver)

            except TimeoutException:

                print(Message.UNKNOWN_ERROR)

