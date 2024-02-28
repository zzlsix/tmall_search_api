import json
import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from VO.ShopInfoVO import DynamicRatings
from VO.ShopInfoVO import ShopInfoVO, serialize_shop_info


class ShopInfo:
    def __init__(self, driver, vars):
        self.driver = driver
        self.vars = vars

    def shop_info(self, shop_id):
        print("shop info")

        # 打开店铺首页
        self.driver.get("https://shop" + str(shop_id) + ".taobao.com")

        time.sleep(random.randint(3, 5))

        # 店铺名称
        WebDriverWait(self.driver, 30).until(
            expected_conditions.presence_of_element_located((By.XPATH, "//div[@class='slogo']/a/strong"))
        )
        self.vars["shop_name"] = self.driver.find_element(By.XPATH,
                                                          "//div[@class='slogo']/a/strong").text
        WebDriverWait(self.driver, 30).until(
            expected_conditions.visibility_of_element_located((By.XPATH, "//a[@class='slogo-triangle']/i"))
        )
        self.driver.find_element(By.XPATH, "//a[@class='slogo-triangle']/i").click()

        # 店铺评分
        WebDriverWait(self.driver, 30).until(
            expected_conditions.visibility_of_element_located((By.XPATH, "//div[@class='shop-rate']/ul/li[1]//em"))
        )
        self.vars["description_match"] = self.driver.find_element(By.XPATH,
                                                                  "//div[@class='shop-rate']/ul/li[1]//em[@class='count']").text
        self.vars["service_attitude"] = self.driver.find_element(By.XPATH,
                                                                 "//div[@class='shop-rate']/ul/li[2]//em[@class='count']").text
        self.vars["logistics_service"] = self.driver.find_element(By.XPATH,
                                                                  "//div[@class='shop-rate']/ul/li[3]//em[@class='count']").text

        # 掌柜
        WebDriverWait(self.driver, 30).until(
            expected_conditions.visibility_of_element_located((By.XPATH, "//div[@class='right']/a"))
        )
        self.vars["shop_owner"] = self.driver.find_element(By.XPATH,
                                                           "//div[@class='right']/a").text

        # 开店时长
        WebDriverWait(self.driver, 30).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//div[@class='right tm-shop-age']/span[@class='tm-shop-age-content']"))
        )
        self.vars["establishment_duration"] = self.driver.find_element(By.XPATH,
                                                                       "//div[@class='right tm-shop-age']/span[@class='tm-shop-age-content']").text

        # 所在地
        WebDriverWait(self.driver, 30).until(
            expected_conditions.presence_of_element_located((By.XPATH, "//li[@class='locus']/div[@class='right']"))
        )
        self.vars["location"] = self.driver.find_element(By.XPATH, "//li[@class='locus']/div[@class='right']").text

        # 封装数据
        dynamic_ratings = DynamicRatings(self.vars["description_match"],
                                         self.vars["service_attitude"],
                                         self.vars["logistics_service"])
        shop_info_vo = ShopInfoVO(shop_id,
                                  self.vars["shop_name"],
                                  dynamic_ratings,
                                  self.vars["shop_owner"],
                                  self.vars["establishment_duration"],
                                  self.vars["location"]
                                  )

        # 如要序列化将 ensure_ascii=True
        return json.dumps(shop_info_vo, default=serialize_shop_info, ensure_ascii=False, indent=2)
