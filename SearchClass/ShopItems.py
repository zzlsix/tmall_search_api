import time
import random

from VO.ShopItemVO import ShopItemVO
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException


class ShopItems:

    def __init__(self, driver, vars):
        self.driver = driver
        self.vars = vars

    def shop_items(self, shop_url):

        print("shop items")
        time.sleep(random.randint(3, 6))

        # 进入店铺页面 准备检查页面布局
        self.driver.get(shop_url + "/search.htm?orderType=newOn_desc")
        print("the connection is accessed now is : " + shop_url)

        # 打开新页面时判断滑块
        time.sleep(random.randint(2, 3))
        try:
            WebDriverWait(self.driver, 15).until(expected_conditions.visibility_of_element_located(
                (By.XPATH, "//p[contains(@class,'ui-page')]/b[contains(@class,'len')]")))
        except TimeoutException:
            try:
                WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "//iframe[@id='baxia-dialog-content']")))
                print("***slider appears : access shop link ***")
                self.slider_handler_items()
            except TimeoutException:
                print("!!! unknown error : access shop link !!!")

        shop_items = []

        # 正常布局
        shop_items = self.normal_shop(shop_url, shop_items)

        # 存入json文件时返回值
        return ShopItemVO(shop_items).items

    # 正常店铺布局
    def normal_shop(self, shop_url, shop_items):
        # 确认是正常店铺布局
        WebDriverWait(self.driver, 15).until(expected_conditions.visibility_of_element_located(
            (By.XPATH, "//p[contains(@class,'ui-page')]/b[contains(@class,'len')]")))
        self.vars["totalPageString"] = self.driver.find_element(By.XPATH,
                                                                "//p[contains(@class,'ui-page')]/b[contains(@class,'len')]").text
        self.vars["totalPage"] = self.driver.execute_script("return arguments[0].split('/')[1].trim()",
                                                            self.vars["totalPageString"])
        print("number of all pages->{}".format(self.vars["totalPage"]))

        time.sleep(random.randint(2, 3))

        # 爬取商品
        for i in range(1, int(self.vars["totalPage"]) + 1):
            # 打开指定page
            self.driver.get(shop_url + "/search.htm?orderType=newOn_desc&pageNo=" + str(i))
            print("the current page is : " + str(i) + " / " + self.vars["totalPage"])

            # 打开新页面时判断滑块
            try:
                WebDriverWait(self.driver, 15).until(expected_conditions.visibility_of_element_located((By.XPATH,
                                                                                                        "//div[@class='J_TItems']/div[contains(@class,'pagination')]/preceding-sibling::div/dl"))
                                                     )
            except TimeoutException:
                try:
                    WebDriverWait(self.driver, 5).until(expected_conditions.visibility_of_element_located(
                        (By.XPATH, "//iframe[@id='baxia-dialog-content']")))
                    print("***slider appears : access shop page link ***")
                    self.slider_handler_items()
                    self.driver.get(shop_url + "/search.htm?orderType=newOn_desc&pageNo=" + str(i))
                except TimeoutException:
                    print("!!! unknown error : access shop page link !!!")

            time.sleep(random.randint(5, 7))

            # 爬取items
            self.vars["items"] = self.driver.execute_script('''
                       var results = [];
                       var elements = document.evaluate("//div[@class='J_TItems']/div[contains(@class,'pagination')]/preceding-sibling::div/dl", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
                       for (var i = 0; i < elements.snapshotLength; i++) {
                           var dlElement = elements.snapshotItem(i);
                           var dataId = dlElement.getAttribute("data-id");
                           var href = dlElement.querySelector("dt a").getAttribute("href");
                           var alt = dlElement.querySelector("dt a img").getAttribute("alt");
                           var imgElement = dlElement.querySelector("dt a img");
                           var img_url = imgElement.getAttribute("data-ks-lazyload");
                           if (!img_url) {
                               img_url = imgElement.getAttribute("src");
                           }
                           results.push({
                               num_iid: dataId,
                               item_href: href,
                               item_name: alt,
                               img_url: img_url
                           });
                       }
                       return results;
                   ''')

            shop_items.extend(self.vars["items"])

            return shop_items
