import random
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException


class SliderHandler:
    @staticmethod
    def slider_handler_items(driver):
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

            # 失败重试
            slider = driver.find_element(By.XPATH, "//div[contains(@class,'nc')]/span")
            slider.click()

            # 获取滑块
            actions = ActionChains(driver)
            actions.click_and_hold(slider).perform()

            # 生成轨迹
            track = []
            div_width = driver.find_element(By.XPATH, "//div[@class='nc_scale']//span[@data-nc-lang='SLIDE']").size['width']
            distance = div_width+slider.size["width"]
            while distance > 0:
                span = random.randint(30, 50)
                if span > distance:
                    span = distance
                track.append(span)
                distance -= span

            total_track = sum(track)

            # 拖动滑块
            for i in track:
                actions.move_by_offset(xoffset=i, yoffset=0).perform()
            time.sleep(0.1)

            # 释放滑块
            actions.release().perform()

            try:
                WebDriverWait(driver, 5).until(
                    expected_conditions.visibility_of_element_located(
                        (By.XPATH, "//iframe[@id='baxia-dialog-content']"))
                )
                SliderHandler.slider_handler_items(driver)
            except TimeoutException:
                slider_disappear = True
