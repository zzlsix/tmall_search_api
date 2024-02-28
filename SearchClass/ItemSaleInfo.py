import json
import random
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from VO.ItemSaleInfoVO import ItemSaleInfoVO, SalesInfo


class ItemSaleInfo:
    def __init__(self, driver, vars):
        self.driver = driver
        self.vars = vars

    def item_sale_info(self, num_iid):
        print("item sale info")

        time.sleep(random.randint(1, 5))

        # 打开商品详情页
        self.driver.get("https://item.taobao.com/item.htm?id=" + str(num_iid))
        time.sleep(random.randint(1, 5))

        # 价格
        WebDriverWait(self.driver, 30).until(expected_conditions.visibility_of_element_located(
            (By.XPATH, "//div[contains(@class,'Price--root')]//span[contains(@class,'Price--priceText')]")))
        self.vars["price"] = self.driver.find_element(By.XPATH,
                                                      "//div[contains(@class,'Price--root')]//span[contains(@class,'Price--priceText')]").text

        # 销售量
        WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'ItemHeader--subTitle')]/span")))
        sale_string = self.driver.find_element(By.XPATH,
                                               "//div[contains(@class,'ItemHeader--subTitle')]/span").text
        self.vars["sold_count"] = self.driver.execute_script("return arguments[0].split(' ')[1]", sale_string)

        # 记录本次爬取时间
        self.vars["current_date"] = datetime.now().date()

        sales_info = SalesInfo(self.vars["sold_count"], self.vars["current_date"])
        item_sale_info_vo = ItemSaleInfoVO(num_iid, self.vars["price"], sales_info)

        return json.dumps(item_sale_info_vo.to_dict(), ensure_ascii=False, indent=2)
