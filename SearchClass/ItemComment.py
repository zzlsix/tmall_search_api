import json
import random
import time

from Message import Message
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from VO.ItemCommentVO import ItemCommentVO


class ItemComment:
    def __init__(self, driver, vars):
        self.driver = driver
        self.vars = vars

    def item_comment(self, num_iid):
        print("item comment")

        time.sleep(random.randint(1, 5))

        # 打开商品相信页
        self.driver.get("https://item.taobao.com/item.htm?id=" + str(num_iid))
        time.sleep(random.randint(1, 5))

        # 点击评论按钮
        WebDriverWait(self.driver, 30).until(expected_conditions.visibility_of_element_located(
            (By.XPATH, "//div[contains(@class,'Tabs--title')][2]/span")))
        self.driver.find_element(By.XPATH, "//div[contains(@class,'Tabs--title')][2]/span").click()

        try:
            # 点击按时间按钮
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
            try:
                # 有评论
                WebDriverWait(self.driver, 15).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "//div[contains(@class,'Comment--root')]/div[contains(@class,'Comment--header')]//div[contains(@class,'Comment--userName')]")))
            except TimeoutException:

                # 没有评论 直接返回
                WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located(
                    (By.XPATH,
                     "//div[contains(@class,'Comments--root')]//div[contains(@class,'Comments--empty')]")))
                return json.dumps(ItemCommentVO(comments).comments, ensure_ascii=False, indent=2)

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
                # 点击下一页按钮
                WebDriverWait(self.driver, 5).until(expected_conditions.visibility_of_element_located(
                    (By.XPATH,
                     "//button[contains(@class,'Comments--nextBtn')]")))
                self.driver.find_element(By.XPATH, "//button[contains(@class,'Comments--nextBtn')]").click()
            except TimeoutException:

                try:
                    # 如果出现 在手机上查看二维码 则视为停止
                    WebDriverWait(self.driver, 5).until(expected_conditions.visibility_of_element_located(
                        (By.XPATH,
                         "//div[contains(@class,'Comments--guideToPhone')]")))

                    is_next_page = False

                except TimeoutException:

                    print(Message.UNKNOWN_ERROR)

        return json.dumps(ItemCommentVO(self.vars["comments"]).comments, ensure_ascii=False, indent=2)