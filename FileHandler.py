import json

import pandas as pd


def read_file(read_file_path, sheet_name):
    exc = pd.read_excel(read_file_path, sheet_name)
    return exc


def write_file(write_file_path, data):
    with open(write_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    read_file_path = r'C:\Users\zzlsix\Desktop\items\项目品牌电商网址清单 -新增部分门店款数.xlsx'
    exc = read_file(read_file_path,'品牌官网')
    cell_id = exc.at[0,'序号']
    cell_href = exc.at[0,'网址']
    write_file_path = r'C:\Users\zzlsix\Desktop\items'+'\\'+str(cell_id)+'.json'
    data = {
        "h": cell_href
    }
    write_file(write_file_path,data)
