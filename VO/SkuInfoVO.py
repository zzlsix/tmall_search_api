class SkuInfoVO:
    def __init__(self,
                 shop_id,
                 shop_name,
                 item,
                 sku_base,
                 skus,
                 crawling_time):
        self.shop_id = shop_id
        self.shop_name = shop_name
        self.item = item
        self.sku_base = sku_base
        self.skus = skus
        self.crawling_time = crawling_time

    def to_dict(self):
        return {
            'shop_id': self.shop_id,
            'shop_name': self.shop_name,
            'item': self.item,
            'sku_base': self.sku_base,
            'skus': self.skus,
            'crawling_time': self.crawling_time
        }


class Item:
    def __init__(self, item_id, images, title, detail):
        self.item_id = item_id
        self.images = images
        self.title = title
        self.detail = detail


class SkuBase:
    def __init__(self, props):
        self.props = props


class Skus:
    def __init__(self, skus):
        self.skus = skus

