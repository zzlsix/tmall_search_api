class ItemBaseInfoVO:
    def __init__(self, item_info, sku_info):
        self.item_info = item_info
        #self.promotion_info = promotion_info
        self.sku_info = sku_info

    def to_dict(self):
        return {
            'item_info': self.item_info.to_dict(),
            'sku_info': self.sku_info.to_dict()
        }


class ItemInfo:
    def __init__(self, item_name, img_url, discount, attributes):
        self.item_name = item_name
        self.img_url = img_url
        self.discount = discount
        self.attributes = attributes

    def to_dict(self):
        return {
            'item_name': self.item_name,
            'img_url': self.img_url,
            'discount': self.discount,
            'attributes': self.attributes
        }


class PromotionInfo:
    def __init__(self, discount_description, activity_description, guarantee):
        self.discount_description = discount_description
        self.activity_description = activity_description
        self.guarantee = guarantee


class SkuInfo:
    def __init__(self, color, shoe_size):
        self.color = color
        self.shoe_size = shoe_size

    def to_dict(self):
        return {
            'color': self.color,
            'shoe_size': self.shoe_size
        }