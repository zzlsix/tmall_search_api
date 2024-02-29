import hashlib
import json
import time
import urllib.parse
import urllib.parse
import requests


from datetime import datetime
from VO.SkuInfoVO import SkuInfoVO


class SkuInfo:
    def __init__(self, driver):
        self.driver = driver

    def get_response(self, item_id):
        # 打开页面
        self.driver.get("https://detail.tmall.com/item.htm?id=770182924262")
        # 获取页面cookie
        cookies = self.driver.get_cookies()
        # 设置user agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        cookie_str = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        # 算法参数 ck_token
        _m_h5_tk = cookies_dict['_m_h5_tk']
        _m_h5_tk_enc = cookies_dict['_m_h5_tk_enc']
        ck_token = _m_h5_tk.split('_')[0]
        # 算法参数 t
        t = str(int(time.time() * 1000))
        # 算法参数 app_key
        app_key = str(12574478)
        # 算法参数 data
        data = {"id": item_id, "detail_v": "3.3.2",
                "exParams": "{\"abbucket\":\"4\",\"id\":\""
                            + item_id + "\",\"queryParams\":\"abbucket=4&id="
                            + item_id + "\",\"domain\":\"https://detail.tmall.com\",\"path_name\":\"/item.htm\"}"}
        data_uri = urllib.parse.quote(json.dumps(data))
        # a 即用于转化 sign 签名
        a = ck_token + "&" + t + "&" + app_key + "&" + json.dumps(data)
        asign = hashlib.md5(a.encode('utf-8')).hexdigest()
        # request请求网址
        api_url = ("https://h5api.m.tmall.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.6.1&appKey=12574478&t=" + t +
                   "&sign=" + asign +
                   "&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&preventFallback=true&type=jsonp&dataType=jsonp&callback=mtopjsonp1" +
                   "&data=" + data_uri)
        # 设置请求头
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
        # 发送请求获得reponse
        response = requests.get(api_url, headers=headers)
        mtop_jsonp = response.text.split('(', 1)[1].rstrip(')')
        return json.loads(mtop_jsonp)

    def get_skus(self, response):

        data = response.get("data")
        seller = data.get("seller")
        # 获取店铺id
        shop_id = seller.get("shopId")
        # 获取店铺名称
        shop_name = seller.get("shopName")
        # 获取当前商品item相关信息
        unprocessed_item = data.get("item")
        item = {
            "item_id": unprocessed_item.get("itemId"),  # 商品id
            "images": unprocessed_item.get("images"),  # 商品图片
            "title": unprocessed_item.get("title"),  # 商品标题
            "detail": data.get("componentsVO").get("extensionInfoVO").get("infos")  # 商品详细介绍
        }
        # 获取sku property
        unprocessed_sku_base = data.get("skuBase")
        sku_base = {
            "props": unprocessed_sku_base.get("props")
        }
        # 单独封装 pid 和 vid
        sku_props_pid = {}
        sku_props_vid = {}
        for p in sku_base.get("props"):
            sku_props_pid[p.get("pid")] = p.get("name")
            for v in p.get("values"):
                sku_props_vid[v.get("vid")] = v.get("name")
        # 获取经过处理skus
        unprocessed_skus = unprocessed_sku_base.get("skus")
        skus = []  # 用于存放skus
        sku2_info = data.get("skuCore").get("sku2info")
        # 本次循环为单独的skuid的商品为单位
        for sku_single in unprocessed_skus:
            sku_id = sku_single.get("skuId")  # 获取skuid
            get_sku_by_id = sku2_info.get(sku_id)
            price = get_sku_by_id.get("price").get("priceText")  # 获取price
            discount_price = get_sku_by_id.get("subPrice", "")
            if discount_price:
                discount_price = discount_price.get("priceText")  # 如果有优惠价格则获取优惠的discount price
            prop_path = sku_single.get("propPath")
            description = ""
            for path in prop_path.split(";"):
                decompose_path = path.split(":")  # 获取prop path进行处理
                pid = decompose_path[0]
                vid = decompose_path[1]
                description += sku_props_pid.get(pid) + ":" + sku_props_vid.get(vid) + ";"  # 拼接处理的description
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
        return sku_info_vo.to_dict()

