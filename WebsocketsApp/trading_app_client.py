from WebsocketsAppLibrary.app_client import *

from trading_types import *


class TradingAppClient(WebsocketAppClient):
    def __init__(self):
        WebsocketAppClient.__init__(self)

        self.add_message_handler("order_status", self.order_status_handler_async)

    async def order_status_handler_async(self, msg: WebsocketAppMessage):
        # Get the Order object from the message JSON data
        order_dict = jsonpickle.decode(msg.JsonData)
        order = Order(**order_dict)

        print('Order Id:' + order.Id + ', Order Status: ' + order.OrderStatus)

    async def place_order_async(self, place_order_request: PlaceOrderRequest):
        msg: WebsocketAppMessage = await self.execute_obj_async("place_order", place_order_request)

        # Get the Order object from the message JSON data
        order_dict = jsonpickle.decode(msg.JsonData)
        order = Order(**order_dict)

        print('Order Id:' + order.Id + ', Order Status: ' + order.OrderStatus)

    async def on_connection_closed_async(self):
        print('server connection closed')
