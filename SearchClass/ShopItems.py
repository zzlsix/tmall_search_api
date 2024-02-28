import time
import random

from Message import Message
from SliderHandler import SliderHandler
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

        time.sleep(random.randint(2, 3))

        # -1： 初始值
        # 0：正常布局页面
        # 1：蕉下outlet布局页面
        page_type = -1

        try:
            # 如果发现页数则为正常页面
            WebDriverWait(self.driver, 15).until(expected_conditions.visibility_of_element_located(
                (By.XPATH, "//p[contains(@class,'ui-page')]/b[contains(@class,'len')]")))
            page_type = 0

        except TimeoutException:

            try:
                # 如果没有页数， 检查是否符合 蕉下outlet 页面
                WebDriverWait(self.driver, 15).until(expected_conditions.visibility_of_element_located(
                    (By.XPATH, "//div[@class='skin-box-bd']/div[contains(@class,'item3')]")))
                page_type = 1

            except TimeoutException:

                # 检查滑块
                SliderHandler.check_slider(self.driver, Message.SLIDER_HAPPEN_ACCESS_SHOP_LINK)
                # 重新打开页面避免加载失败
                self.driver.get(shop_url + "/search.htm?orderType=newOn_desc")

        shop_items = []

        if page_type == 0:
            # 正常布局页面
            shop_items = self.normal_shop(shop_url, shop_items)
        elif page_type == 1:
            # 蕉下outlet布局页面
            shop_items = self.jiaoxia_outlet_shop(shop_items)

        # 存入json文件时返回值
        return ShopItemVO(shop_items).items

    # 正常店铺布局
    def normal_shop(self, shop_url, shop_items):
        # 确认是正常布局页面
        WebDriverWait(self.driver, 15).until(expected_conditions.visibility_of_element_located(
            (By.XPATH, "//p[contains(@class,'ui-page')]/b[contains(@class,'len')]")))

        # 获取总页数
        self.vars["totalPageString"] = self.driver.find_element(By.XPATH,
                                                                "//p[contains(@class,'ui-page')]/b[contains(@class,'len')]").text
        self.vars["totalPage"] = self.driver.execute_script("return arguments[0].split('/')[1].trim()",
                                                            self.vars["totalPageString"])
        print("number of all pages : " + self.vars["totalPage"])

        time.sleep(random.randint(2, 3))

        # 用于保存商品id 避免页面重复问题
        total_id_set = set()

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

                # 检查滑块 并 重新打开页面
                SliderHandler.check_slider(self.driver, Message.SLIDER_HAPPEN_ACCESS_PAGE_LINK)
                self.driver.get(shop_url + "/search.htm?orderType=newOn_desc&pageNo=" + str(i))

            time.sleep(random.randint(5, 7))

            # 爬取items
            self.vars["items"] = self.driver.execute_script('''
                       var results = [];
                       var idSet = [];
                       var elements = document.evaluate("//div[@class='J_TItems']/div[contains(@class,'pagination')]/preceding-sibling::div/dl", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
                       for (var i = 0; i < elements.snapshotLength; i++) {
                           var dlElement = elements.snapshotItem(i);
                           var id = dlElement.getAttribute("data-id");
                           var href = dlElement.querySelector("dt a").getAttribute("href");
                           var name = dlElement.querySelector("dt a img").getAttribute("alt");
                           var imgElement = dlElement.querySelector("dt a img");
                           var img_url = imgElement.getAttribute("data-ks-lazyload");
                           if (!img_url) {
                               img_url = imgElement.getAttribute("src");
                           }
                           results.push({
                               num_iid: id,
                               item_href: href,
                               item_name: name,
                               img_url: img_url
                           });
                           idSet.push(id);
                       }
                       return {
                           id_set : idSet,
                           results : results
                       };
                   ''')

            id_set = set(self.vars["items"]["id_set"])
            # 如果不重复则更新集合与结果集
            if not total_id_set.issuperset(id_set):
                total_id_set.update(id_set)
                shop_items.extend(self.vars["items"]["results"])

        return shop_items

    def jiaoxia_outlet_shop(self, shop_items):
        # 确认是蕉下outlet布局页面
        WebDriverWait(self.driver, 15).until(expected_conditions.visibility_of_element_located(
            (By.XPATH, "//div[@class='skin-box-bd']/div[contains(@class,'item3')]")))
        self.vars["items"] = self.driver.execute_script('''
                              var results = [];
                              var elements = document.evaluate("//div[@class='skin-box-bd']/div[contains(@class,'item3')]//dl", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
                              for (var i = 0; i < elements.snapshotLength; i++) {
                                  var dlElement = elements.snapshotItem(i);
                                  var dataId = dlElement.getAttribute("data-id");
                                  var href = dlElement.querySelector("dt a").getAttribute("href");
                                  var alt = dlElement.querySelector("dd a").textContent;
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
