import json
import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from VO.ItemBaseInfoVO import ItemBaseInfoVO, ItemInfo, SkuInfo


class ItemDetailInfo:

    def __init__(self, driver, vars):
        self.driver = driver
        self.vars = vars

    def item_base_info(self, num_iid):
        print("item base info")

        time.sleep(random.randint(1, 5))

        # 打开商品详情页
        self.driver.get("https://item.taobao.com/item.htm?id=" + str(num_iid))
        time.sleep(random.randint(1, 5))

        # 商品名称
        WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              "//h1[contains(@class, 'ItemHeader--mainTitle')]"))
                                             )
        self.vars["item_name"] = self.driver.find_element(By.XPATH,
                                                          "//h1[contains(@class, 'ItemHeader--mainTitle')]").text

        # 商品图片
        WebDriverWait(self.driver, 30).until(expected_conditions.visibility_of_element_located((By.XPATH,
                                                                                                "//ul[contains(@class,'PicGallery--thumbnails')]/li/img"))
                                             )
        self.vars["img_url"] = self.driver.execute_script('''
            var imgElements = document.evaluate("//ul[contains(@class,'PicGallery--thumbnails')]/li/img", document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
            var srcValues = [];
            for (var i = 0; i < imgElements.snapshotLength; i++) {
                var img = imgElements.snapshotItem(i);
                srcValues.push(img.src);
            }
            return srcValues;
        ''')

        # 商品折扣
        WebDriverWait(self.driver, 30).until(expected_conditions.visibility_of_element_located((By.XPATH,
                                                                                                "//div[contains(@class,'Promotion--arrow')]"))
                                             )
        self.driver.find_element(By.XPATH, "//div[contains(@class,'Promotion--arrow')]").click()
        WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              "//div[contains(@class, 'Promotion--leftPanel')]//span[contains(@class, 'Promotion--caption')][1]"))
                                             )
        self.vars["discount"] = self.driver.find_element(By.XPATH,
                                                         "//div[contains(@class, 'Promotion--leftPanel')]//span[contains(@class, 'Promotion--caption')][1]").text

        # 商品属性
        WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              "//div[contains(@class,'ItemDetail--attrs')]//span[contains(@class,'Attrs--attr')]"))
                                             )
        self.vars["attributes"] = self.driver.execute_script('''
            var xpathExpression = "//div[contains(@class,'ItemDetail--attrs')]//span[contains(@class,'Attrs--attr')]";
            var xpathResult = document.evaluate(xpathExpression, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
            var detailOfItem = [];      
            for (var i = 0; i < xpathResult.snapshotLength; i++) {         
                var element = xpathResult.snapshotItem(i);         
                detailOfItem.push(element.textContent.trim());     
            }      
            return detailOfItem;
        ''')

        # 商品颜色
        WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              "//div[@class='skuCate'][1]//div[contains(@class, 'skuItem current') or contains(@class, 'skuItem disabled')]/div"))
                                             )
        self.vars["color"] = self.driver.execute_script('''
            var result = [];
            var xpathExpression = "//div[@class='skuCate'][1]//div[contains(@class, 'skuItem current') or contains(@class, 'skuItem disabled')]/div";
            var divElements = document.evaluate(xpathExpression, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
            for (var i = 0; i < divElements.snapshotLength; i++) {
                var divElement = divElements.snapshotItem(i);
                var data = {};
                // 获取div的title属性值
                data.name = divElement.getAttribute('title');
                // 获取div下的img标签的src属性值
                var imgElement = divElement.querySelector('img');
                if (imgElement) {
                    data.image_url = imgElement.src;
                } else {
                    data.image_url = null;
                }
                result.push(data);
            }
            return result;
        ''')

        # 商品尺寸
        WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              "//div[@class='skuCate'][2]/div/div[contains(@class, 'skuItem')]/div"))
                                             )
        self.vars["shoe_size"] = self.driver.execute_script('''
            var result = [];
            var xpathExpression = "//div[@class='skuCate'][2]/div/div[contains(@class, 'skuItem')]/div";
            var divElements = document.evaluate(xpathExpression, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
            for (var i = 0; i < divElements.snapshotLength; i++) {
                var divElement = divElements.snapshotItem(i);
                // 获取div的title属性值
                result.push(divElement.getAttribute('title'));
            }
            return result;
        ''')

        item_info = ItemInfo(self.vars["item_name"], self.vars["img_url"], self.vars["discount"],
                             self.vars["attributes"])
        sku_info = SkuInfo(self.vars["color"], self.vars["shoe_size"])
        item_base_info_vo = ItemBaseInfoVO(item_info, sku_info)

        return json.dumps(item_base_info_vo.to_dict(), ensure_ascii=False, indent=2)