class DynamicRatings:
    def __init__(self, description_match, service_attitude, logistics_service):
        self.description_match = description_match
        self.service_attitude = service_attitude
        self.logistics_service = logistics_service


# class CustomerService:
#     def __init__(self):
#


class ShopInfoVO:
    def __init__(self,
                 shop_id,
                 shop_name,
                 dynamic_ratings,
                 shop_owner,
                 establishment_duration,
                 location
                 ):
        self.shop_id = shop_id
        self.shop_name = shop_name
        self.dynamic_ratings = dynamic_ratings
        self.shop_owner = shop_owner
        self.establishment_duration = establishment_duration
        self.location = location


def serialize_dynamic_ratings(dynamic_ratings):
    return {
        "description_match": dynamic_ratings.description_match,
        "service_attitude": dynamic_ratings.service_attitude,
        "logistics_service": dynamic_ratings.logistics_service
    }


def serialize_shop_info(shop_info):
    return {
        "shop_id": shop_info.shop_id,
        "shop_name": shop_info.shop_name,
        "dynamic_ratings": serialize_dynamic_ratings(shop_info.dynamic_ratings),
        "shop_owner": shop_info.shop_owner,
        "establishment_duration": shop_info.establishment_duration,
        "location": shop_info.location
    }
