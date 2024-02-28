from SearchClass.WebDriver import *
from SearchClass.Login import *
from SearchClass.ItemComment import *
from SearchClass.ShopItems import *
from FileHandler import *

if __name__ == '__main__':

    webdriver_instance = WebDriver()
    driver, vars = webdriver_instance.setup_webdriver()

    login_instance = Login(driver, vars)
    login_instance.login("18772332256", "zzl112203")

    shop_items_instance = ShopItems(driver, vars)

    # read_file_path = r'C:\Users\zzlsix\Desktop\items\项目品牌电商网址清单 -新增部分门店款数.xlsx'
    # sheet_name = '品牌官网'
    # exc = read_file(read_file_path, sheet_name)
    #
    # for i in range(89, 242):
    #     cell_id = exc.at[i, '序号']
    #     cell_href = exc.at[i, '网址']
    #     write_file_path = r'C:\Users\zzlsix\Desktop\items' + '\\' + str(cell_id) + '.json'
    #     data = shop_items_instance.shop_items(cell_href)
    #     write_file(write_file_path, data)

    shop_items_instance.shop_items("https://semir.tmall.com/")



