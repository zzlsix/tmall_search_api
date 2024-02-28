from SearchClass.WebDriver import *
from SearchClass.Login import *

if __name__ == '__main__':

    webdriver_instance = WebDriver()
    driver, vars = webdriver_instance.setup_webdriver()

    login_instance = Login(driver, vars)
    login_instance.login("18772332256", "zzl112203")



