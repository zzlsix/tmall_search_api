
class ItemSaleInfoVO:
    def __init__(self, item_id, price, sales_info):
        self.item_id = item_id
        self.price = price
        self.sales_info = sales_info

    def to_dict(self):
        return {
            'item_id': self.item_id,
            'price': self.price,
            'sales_info': self.sales_info.to_dict()
        }


class SalesInfo:
    def __init__(self, sold_count, current_date):
        self.sold_count = sold_count
        self.current_date = current_date

    def to_dict(self):
        return {
            'sold_count': self.sold_count,
            'current_date': self.current_date.strftime('%Y-%m-%d')
        }
