import time
import random
import json
import os
import subprocess
import requests
import urllib.parse
import hashlib

from VO.SkuInfoVO import SkuInfoVO
from datetime import datetime
from VO.ShopInfoVO import DynamicRatings
from VO.ShopInfoVO import ShopInfoVO, serialize_shop_info
from VO.ShopItemVO import ShopItemVO
from VO.ItemBaseInfoVO import ItemBaseInfoVO, ItemInfo, SkuInfo
from VO.ItemSaleInfoVO import ItemSaleInfoVO, SalesInfo
from VO.ItemCommentVO import ItemCommentVO
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from FileHandler import read_file, write_file


# 命令行启动：
# chrome.exe -remote-debugging-port=9222 -user-data-dir="C:\Users\zzlsix\Desktop\atmP"
# chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\Users\zzlsix\Desktop\atmP" --headless
# taskkill /F /IM chrome.exe
class SearchAPI:

    # 启动webdriver
    def __init__(self):
        self.vars = None
        self.driver = None

    def setup_webdriver(self):
        print("webdriver : set up and start")
        # work = r'chrome.exe -remote-debugging-port=9222 -user-data-dir="C:\Users\zzlsix\Desktop\atmP"'
        # work = r'chrome.exe  --headless --remote-debugging-port=9222 --user-data-dir="C:\Users\zzlsix\Desktop\atmP"'  # 无头配置
        # os.popen(work)

        # 无头模式
        # command = [
        #     "chrome",
        #     "--headless",
        #     "--remote-debugging-port=9222",
        #     "--user-data-dir=C:\\Users\\zzlsix\\Desktop\\atmP",
        #     "https://www.baidu.com"
        # ]

        # # 有头模式
        # command = [
        #     "chrome",
        #     "--remote-debugging-port=9222",
        #     "--user-data-dir=C:\\Users\\zzlsix\\Desktop\\atmP"
        # ]
        #
        # subprocess.Popen(command)
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.driver = webdriver.Chrome(options=options)
        self.vars = {}

    # 退出webdriver
    def teardown_method(self):
        print("webdriver : kill and end")
        self.driver.quit()
        # work = r'taskkill /F /IM chrome.exe'
        # os.popen(work)
        print("program over")

    # 滑块处理--爬取items时
    def slider_handler_items(self):
        # 获取滑块
        frame_element = self.driver.find_element(By.XPATH, "//iframe[@id='baxia-dialog-content']")
        self.driver.switch_to.frame(frame_element)
        self.drag_slider()
        self.driver.switch_to.default_content()

    # 拖动滑块动作
    def drag_slider(self):
        print("drag slider")
        slider = self.driver.find_element(By.XPATH, "//div[contains(@class,'nc')]/span")
        # 获取滑块
        actions = ActionChains(self.driver)
        actions.click_and_hold(slider).perform()

        # 生成轨迹
        track = []
        distance = 300
        a = 0
        while distance > 0:
            span = random.randint(30, 40)
            a += span
            track.append(a)
            distance -= span
            if sum(track[:-1]) > 300:
                break
        total_track = sum(track[:-1])
        if total_track > 300:
            track[-1] -= total_track - 300

        # 拖动滑块
        for i in track:
            actions.move_by_offset(xoffset=i, yoffset=0).perform()
        time.sleep(0.1)

        # 释放滑块
        actions.release().perform()

    # 登录淘宝账号,
    # **前提** 账号密码已经在浏览器保存，否则修改
    def login(self, username, password):
        print("log in")
        self.driver.get("https://login.taobao.com/member/login.jhtml")

        # 切换登录样式
        try:
            WebDriverWait(self.driver, 5).until(
                expected_conditions.visibility_of_element_located(
                    (By.XPATH, "//div[contains(@class,'qrcode-bottom-links')]/a[@target='_self']"))
            )
            self.driver.find_element(By.XPATH,
                                     "//div[contains(@class,'qrcode-bottom-links')]/a[@target='_self']").click()
        except TimeoutException:
            print("no qrcode")

        # username and password
        username = username
        password = password
        username_input = self.driver.find_element(By.XPATH, "//input[@id='fm-login-id']")
        password_input = self.driver.find_element(By.XPATH, "//input[@id='fm-login-password']")
        username_input.send_keys(username)
        time.sleep(1)
        password_input.send_keys(password)
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//div[@class='fm-btn']/button").click()
        # TODO 登录时滑块
        try:
            WebDriverWait(self.driver, 5).until(
                expected_conditions.visibility_of_element_located(
                    (By.XPATH, "//iframe[@id='baxia-dialog-content']"))
            )
            print("***slider appears : before log in ***")
            time.sleep(5)
            self.slider_handler_items()
            time.sleep(random.randint(2, 3))
            self.driver.find_element(By.XPATH, "//div[@class='fm-btn']/button").click()
        except TimeoutException:
            print("before log in : no slider")

        # 登录后滑块
        try:
            WebDriverWait(self.driver, 5).until(
                expected_conditions.visibility_of_element_located(
                    (By.XPATH, "//div[contains(@class,'nc')]/span"))
            )
            print("***slider appears : after log in ***")
            self.drag_slider()
        except TimeoutException:
            print("after log in : no slider")

    # 输入：店铺id
    # 输出：店铺基本信息（店铺名称、开店时长、所在地、动态评分等）
    # -------------------------------------------------------------------------------------------------
    # 访问模式：https://shop店铺ID.taobao.com
    # 李宁官方旗舰店： shop_id=57299736
    # 店铺商品品目入口页面：https://shop57299736.taobao.com
    # 分页情况：无

    def shop_info(self, shop_id):
        print("shop info")
        self.driver.get("https://shop" + str(shop_id) + ".taobao.com")
        time.sleep(random.randint(1, 3))
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

    # 输入：店铺URL
    # 输出：店铺所有商品的num_iid
    # -------------------------------------------------------------------------------------------------
    # 访问模式：店铺URL/search.htm?orderType=newOn_desc
    # 李宁官方旗舰店：    https://lining.tmall.com
    # 店铺商品品目入口页面： https://lining.tmall.com/search.htm?orderType=newOn_desc
    # 分页页面链接：https://lining.tmall.com/search.htm?orderType=newOn_desc&pageNo=1

    def shop_item(self, shop_url):
        print("shop item")
        time.sleep(random.randint(3, 6))
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

        shop_item_vo = []

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
            shop_item_vo.extend(self.vars["items"])

        # 存入json文件时返回值
        return ShopItemVO(shop_item_vo).items
        # 返回json格式时返回值
        # return json.dumps(ShopItemVO(shop_item_vo).items, ensure_ascii=False, indent=2)

    # 输入：商品的num_iid
    # 输出：商品基本信息（包括品名、价格、型号、颜色、商品图片等）
    # -------------------------------------------------------------------------------------------------
    # 访问模式：https://item.taobao.com/item.htm?id=商品ID
    # 李宁赤兔6：id=744593438840
    # 商品页面：https://item.taobao.com/item.htm?id=744593438840
    # 分页情况：无

    def item_base_info(self, num_iid):
        print("item base info")
        time.sleep(random.randint(1, 5))
        self.driver.get("https://item.taobao.com/item.htm?id=" + str(num_iid))
        time.sleep(random.randint(1, 5))
        WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              "//h1[contains(@class, 'ItemHeader--mainTitle')]"))
                                             )
        self.vars["item_name"] = self.driver.find_element(By.XPATH,
                                                          "//h1[contains(@class, 'ItemHeader--mainTitle')]").text
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
        WebDriverWait(self.driver, 30).until(expected_conditions.visibility_of_element_located((By.XPATH,
                                                                                                "//div[contains(@class,'Promotion--arrow')]"))
                                             )
        self.driver.find_element(By.XPATH, "//div[contains(@class,'Promotion--arrow')]").click()
        WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                              "//div[contains(@class, 'Promotion--leftPanel')]//span[contains(@class, 'Promotion--caption')][1]"))
                                             )
        self.vars["discount"] = self.driver.find_element(By.XPATH,
                                                         "//div[contains(@class, 'Promotion--leftPanel')]//span[contains(@class, 'Promotion--caption')][1]").text
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

    # 输入：商品的num_iid（同2.1）
    # 输出：商品价格和销售信息（包括品名、型号、颜色、商品图片等）
    # -------------------------------------------------------------------------------------------------
    # 访问模式：http://item.taobao.com/item.htm?id=商品ID
    # 李宁赤兔6：id=744593438840
    # 商品页面：http://item.taobao.com/item.htm?id=744593438840
    # 分页情况：无

    def item_sale_info(self, num_iid):
        print("item sale info")
        time.sleep(random.randint(1, 5))
        self.driver.get("https://item.taobao.com/item.htm?id=" + str(num_iid))
        time.sleep(random.randint(1, 5))
        WebDriverWait(self.driver, 30).until(expected_conditions.visibility_of_element_located(
            (By.XPATH, "//div[contains(@class,'Price--root')]//span[contains(@class,'Price--priceText')]")))
        self.vars["price"] = self.driver.find_element(By.XPATH,
                                                      "//div[contains(@class,'Price--root')]//span[contains(@class,'Price--priceText')]").text

        WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'ItemHeader--subTitle')]/span")))
        sale_string = self.driver.find_element(By.XPATH,
                                               "//div[contains(@class,'ItemHeader--subTitle')]/span").text
        self.vars["sold_count"] = self.driver.execute_script("return arguments[0].split(' ')[1]", sale_string)
        self.vars["current_date"] = datetime.now().date()
        sales_info = SalesInfo(self.vars["sold_count"], self.vars["current_date"])
        item_sale_info_vo = ItemSaleInfoVO(num_iid, self.vars["price"], sales_info)
        return json.dumps(item_sale_info_vo.to_dict(), ensure_ascii=False, indent=2)

    # 输入：商品的num_iid（同2.1和2.2）
    # 输出：商品价格和销售信息（包括品名、型号、颜色、商品图片等）
    # -------------------------------------------------------------------------------------------------
    # 访问模式：http://item.taobao.com/item.htm?id=商品ID
    # 李宁赤兔6：id=744593438840
    # 商品页面：http://item.taobao.com/item.htm?id=744593438840
    # http://item.taobao.com/item.htm?id=717491796120

    # 分页情况：商品详情页面内动态加载分页，无独立链接

    def item_comment(self, num_iid):
        # print("item comment")
        # time.sleep(random.randint(1, 5))
        # self.driver.get("https://item.taobao.com/item.htm?id=" + str(num_iid))
        # time.sleep(random.randint(1, 5))
        WebDriverWait(self.driver, 30).until(expected_conditions.visibility_of_element_located(
            (By.XPATH, "//div[contains(@class,'Tabs--title')][2]/span")))
        self.driver.find_element(By.XPATH, "//div[contains(@class,'Tabs--title')][2]/span").click()
        try:
            WebDriverWait(self.driver, 5).until(expected_conditions.visibility_of_element_located(
                (By.XPATH, "//div[contains(@class,'Comments--sortBy')]/button")))
            self.driver.find_element(By.XPATH, "//div[contains(@class,'Comments--sortBy')]/button").click()
            WebDriverWait(self.driver, 5).until(expected_conditions.visibility_of_element_located(
                (By.XPATH, "//div[contains(@class,'Comments--sortList')]/div[2]")))
            self.driver.find_element(By.XPATH, "//div[contains(@class,'Comments--sortList')]/div[2]").click()
        except TimeoutException:
            print("no button comments are sorted by time")
        is_next_page = True
        comments = []
        while is_next_page:
            WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located(
                (By.XPATH,
                 "//div[contains(@class,'Comment--root')]/div[contains(@class,'Comment--header')]//div[contains(@class,'Comment--userName')]")))
            self.vars["comment"] = self.driver.execute_script('''
                var result=[];
                var xpathExpression="//div[contains(@class,'Comments--comments')]/div"
                var divElements=document.evaluate(xpathExpression, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                for (var i = 0; i < divElements.snapshotLength; i++) {
                    var divElement = divElements.snapshotItem(i);
                    var comment = {};
                    var commentContentNode = document.evaluate(
                        ".//div[contains(@class,'Comment--root')]/div[contains(@class,'Comment--content')]", 
                        divElement, null, XPathResult.STRING_TYPE, null);
                    comment.comment_content =commentContentNode.stringValue;
                    var buyerNameNode = document.evaluate(
                        ".//div[contains(@class,'Comment--root')]/div[contains(@class,'Comment--header')]//div[contains(@class,'Comment--userName')]",
                        divElement, null, XPathResult.STRING_TYPE, null);
                    comment.buyer_name =buyerNameNode.stringValue;
                    var metaNode = document.evaluate(
                        ".//div[contains(@class,'Comment--root')]/div[contains(@class,'Comment--header')]//div[contains(@class,'Comment--meta')]", 
                        divElement, null, XPathResult.STRING_TYPE, null);
                    meta = metaNode.stringValue;
                    var comment_date_string=meta.split('\xa0')[0];
                    var date_number = comment_date_string.match(/\d+/);
                    var current_time=new Date();
                    if(comment_date_string.includes('天')){
                        var comment_date_time=current_time.getTime()-(date_number*24*60*60*1000);
                        var comment_date=new Date(comment_date_time);
                        comment.comment_time = comment_date.getFullYear()+'-'+(comment_date.getMonth()+1).toString().padStart(2,'0')+'-'+comment_date.getDate().toString().padStart(2,'0');
                    }else if(comment_date_string.includes('月')){
                        //月份粗略计算
                        var comment_date_time=current_time.getTime()-(date_number*30*24*60*60*1000);
                        var comment_date=new Date(comment_date_time);
                        console.log(comment_date);
                        comment.comment_time = comment_date.getFullYear()+'-'+(comment_date.getMonth()+1).toString().padStart(2,'0')+'-'+comment_date.getDate().toString().padStart(2,'0');
                    }else if(comment_date_string.includes('小时')){
                        var comment_date_time=current_time.getTime()-(date_number*60*60*1000);
                        var comment_date=new Date(comment_date_time);
                        console.log(comment_date);
                        comment.comment_time = comment_date.getFullYear()+'-'+(comment_date.getMonth()+1).toString().padStart(2,'0')+'-'+comment_date.getDate().toString().padStart(2,'0');
                    }
                    //时间排序+评论时间处理
                    comment.comment_object = meta.split('\xa0')[1];
                    result.push(comment);
                }
                return result;
            ''')
            comments.extend(self.vars["comment"])
            self.vars["comments"] = comments
            time.sleep(random.randint(1, 5))
            try:
                WebDriverWait(self.driver, 5).until(expected_conditions.visibility_of_element_located(
                    (By.XPATH,
                     "//button[contains(@class,'Comments--nextBtn')]")))
                self.driver.find_element(By.XPATH, "//button[contains(@class,'Comments--nextBtn')]").click()
            except TimeoutException:
                try:
                    WebDriverWait(self.driver, 5).until(expected_conditions.visibility_of_element_located(
                        (By.XPATH,
                         "//div[contains(@class,'Comments--guideToPhone')]")))
                    is_next_page = False

                except TimeoutException:
                    print("error")
        return json.dumps(ItemCommentVO(self.vars["comments"]).comments, ensure_ascii=False, indent=2)

    def get_taobao_product_details(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            # 替换为你的浏览器 User-Agent
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response
        else:
            print("Failed to retrieve data. Status code:", response.status_code)
            return None

    def get_source(self, id):
        self.driver.get("https://detail.tmall.com/item.htm?id=770182924262")
        cookies = self.driver.get_cookies()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        cookie_str = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        _m_h5_tk = cookies_dict['_m_h5_tk']
        _m_h5_tk_enc = cookies_dict['_m_h5_tk_enc']
        ck_token = _m_h5_tk.split('_')[0]
        t = str(int(time.time() * 1000))
        app_key = str(12574478)
        data = {"id": id, "detail_v": "3.3.2",
                "exParams": "{\"abbucket\":\"4\",\"id\":\"" + id + "\",\"queryParams\":\"abbucket=4&id=" + id + "\",\"domain\":\"https://detail.tmall.com\",\"path_name\":\"/item.htm\"}"}
        data_uri = urllib.parse.quote(json.dumps(data))
        a = ck_token + "&" + t + "&" + app_key + "&" + json.dumps(data)
        asign = hashlib.md5(a.encode('utf-8')).hexdigest()
        api_url = ("https://h5api.m.tmall.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.6.1&appKey=12574478&t=" + t +
                   "&sign=" + asign +
                   "&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&preventFallback=true&type=jsonp&dataType=jsonp&callback=mtopjsonp1" +
                   "&data=" + data_uri)
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://detail.tmall.com/',
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'script',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': user_agent,
            'Cookie': cookie_str
        }
        response = requests.get(api_url, headers=headers)
        mtop_jsonp = response.text.split('(', 1)[1].rstrip(')')
        return json.loads(mtop_jsonp)


if __name__ == '__main__':
    search = SearchAPI()
    # 创建webdriver
    search.setup_webdriver()
    response = search.get_source("744593438840")
    data = response.get("data")
    seller = data.get("seller")
    shop_id = seller.get("shopId")
    shop_name = seller.get("shopName")
    unprocessed_item = data.get("item")
    item = {
        "item_id": unprocessed_item.get("itemId"),
        "images": unprocessed_item.get("images"),
        "title": unprocessed_item.get("title"),
        "detail": data.get("componentsVO").get("extensionInfoVO").get("infos")
    }
    unprocessed_sku_base = data.get("skuBase")
    sku_base = {
        "props": unprocessed_sku_base.get("props")
    }
    sku_props_pid = {}
    sku_props_vid = {}
    for p in sku_base.get("props"):
        sku_props_pid[p.get("pid")] = p.get("name")
        for v in p.get("values"):
            sku_props_vid[v.get("vid")] = v.get("name")

    unprocessed_skus = unprocessed_sku_base.get("skus")
    skus = []
    sku2_info = data.get("skuCore").get("sku2info")
    for sku_single in unprocessed_skus:
        sku_id = sku_single.get("skuId")
        get_sku_by_id = sku2_info.get(sku_id)
        price = get_sku_by_id.get("price").get("priceText")
        discount_price = get_sku_by_id.get("subPrice", "")
        if discount_price:
            discount_price = discount_price.get("priceText")
        prop_path = sku_single.get("propPath")
        description = ""
        for path in prop_path.split(";"):
            decompose_path = path.split(":")
            pid = decompose_path[0]
            vid = decompose_path[1]
            description += sku_props_pid.get(pid) + ":" + sku_props_vid.get(vid) + ";"
        skus.append({
            "sku_id": sku_id,
            "description": description,
            "price": price,
            "discount": discount_price,
            "date": datetime.now().strftime("%Y-%m-%d"),
        })
    crawling_time = datetime.now().strftime("%Y-%m-%d")
    sku_info_vo = SkuInfoVO(shop_id, shop_name, item, sku_base, skus, crawling_time)
    print(json.dumps(sku_info_vo.to_dict(), ensure_ascii=False, indent=2))

    print(1)
    # # 店铺信息
    # print(search.shop_info(57299736))
    # 店铺商品
    # print(search.shop_item("https://lining.tmall.com"))
    # # 商品基本信息
    # print(search.item_base_info(744593438840))
    # # 商品销售信息
    # print(search.item_sale_info(744593438840))
    # # 商品评论
    # print(search.item_comment(678997602235))

    # # 商品存json文件代码
    # read_file_path = r'C:\Users\zzlsix\Desktop\items\项目品牌电商网址清单 -新增部分门店款数.xlsx'
    # sheet_name = '品牌官网'
    # exc = read_file(read_file_path, sheet_name)
    #
    # for i in range(83, 242):
    #     cell_id = exc.at[i, '序号']
    #     cell_href = exc.at[i, '网址']
    #     write_file_path = r'C:\Users\zzlsix\Desktop\items' + '\\' + str(cell_id) + '.json'
    #     data = search.shop_item(cell_href)
    #     write_file(write_file_path, data)
