import time
import random
import json
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
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException


# chrome.exe -remote-debugging-port=9222 -user-data-dir="D:\atmP"
class SearchAPI:

    # 启动webdriver
    def setup_webdriver(self):
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.driver = webdriver.Chrome(options=options)
        self.vars = {}

    # 退出webdriver
    def teardown_method(self):
        self.driver.quit()

    # 登录淘宝账号,
    # **前提** 账号密码已经在浏览器保存，否则修改
    def login(self):
        self.driver.get("https://login.taobao.com/member/login.jhtml")
        try:
            WebDriverWait(self.driver, 5).until(
                expected_conditions.visibility_of_element_located(
                    (By.XPATH, "//div[contains(@class,'qrcode-bottom-links')]/a[@target='_self']"))
            )
            self.driver.find_element(By.XPATH,
                                     "//div[contains(@class,'qrcode-bottom-links')]/a[@target='_self']").click()
        except TimeoutException:
            print("no qrcode")
        time.sleep(random.randint(1, 3))
        self.driver.find_element(By.XPATH, "//div[@class='fm-btn']/button").click()
        time.sleep(random.randint(1, 3))

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
        self.driver.get(shop_url + "/search.htm?orderType=newOn_desc")
        WebDriverWait(self.driver, 30).until(expected_conditions.presence_of_element_located(
            (By.XPATH, "//p[contains(@class,'ui-page')]/b[contains(@class,'len')]")))
        self.vars["totalPageString"] = self.driver.find_element(By.XPATH,
                                                                "//p[contains(@class,'ui-page')]/b[contains(@class,'len')]").text
        self.vars["totalPage"] = self.driver.execute_script("return arguments[0].split('/')[1].trim()",
                                                            self.vars["totalPageString"])
        print("number of all pages->{}".format(self.vars["totalPage"]))
        time.sleep(random.randint(1, 5))
        shop_item_vo = []
        for i in range(1, int(self.vars["totalPage"]) + 1):
            time.sleep(random.randint(1, 5))
            self.driver.get(shop_url + "/search.htm?orderType=newOn_desc&pageNo=" + str(i))
            time.sleep(random.randint(1, 5))
            WebDriverWait(self.driver, 30).until(expected_conditions.visibility_of_element_located((By.XPATH,
                                                                                                    "//div[@class='J_TItems']/div[contains(@class,'pagination')]/preceding-sibling::div/dl"))
                                                 )
            self.vars["items"] = self.driver.execute_script('''
                var elements = document.evaluate("//div[@class='J_TItems']/div[contains(@class,'pagination')]/preceding-sibling::div/dl", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
                var results = [];
                for (var i = 0; i < elements.snapshotLength; i++) {
                    var dlElement = elements.snapshotItem(i);
                    var dataId = dlElement.getAttribute("data-id");
                    var href = dlElement.querySelector("dt a").getAttribute("href");
                    var alt = dlElement.querySelector("dt a img").getAttribute("alt");
                    var src = dlElement.querySelector("dt a img").getAttribute("src");
                    results.push({
                        num_iid: dataId,
                        item_href: href,
                        item_name: alt,
                        img_url: src
                    });
                }
                return results;
            ''')
            shop_item_vo.extend(self.vars["items"])
        return json.dumps(ShopItemVO(shop_item_vo).items, ensure_ascii=False, indent=2)

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


if __name__ == '__main__':
    search = SearchAPI()
    # 创建webdriver
    search.setup_webdriver()
    # 登录
    search.login()
    # 店铺信息
    print(search.shop_info(57299736))
    # 店铺商品
    print(search.shop_item("https://lining.tmall.com"))
    # 商品基本信息
    print(search.item_base_info(744593438840))
    # 商品销售信息
    print(search.item_sale_info(744593438840))
    # 商品评论
    print(search.item_comment(678997602235))
