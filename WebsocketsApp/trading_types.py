from datetime import datetime
from WebsocketsAppLibrary.app_types import *


class PlaceOrderRequest(object):
    def __init__(self, **kwargs):
        self.Symbol = None
        self.Price: float = 0.0
        self.Quantity: int = 0
        self.Market = None

        fill_obj(self, **kwargs)


class Order(object):
    def __init__(self, **kwargs):
        self.Id = None
        self.Symbol = None
        self.AveragePrice: float = 0.0
        self.Quantity: int = 0
        self.Market = None
        self.Timestamp: datetime
        self.OrderStatus = "Pending"

        fill_obj(self, **kwargs)
