from SearchClass.WebDriver import *
from SearchClass.Login import *
from SearchClass.ItemComment import *

if __name__ == '__main__':

    webdriver_instance = WebDriver()
    driver, vars = webdriver_instance.setup_webdriver()

    login_instance = Login(driver, vars)
    login_instance.login("18772332256", "zzl112203")

    comment_instance = ItemComment(driver, vars)
    print(comment_instance.item_comment(766598378662))



