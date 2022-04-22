import uuid

from WebsocketsAppLibrary.app_server import *

from trading_types import *


class TradingAppServer(WebsocketAppServer):
    def __init__(self, port):
        WebsocketAppServer.__init__(self, port)

        # Add message handlers here
        self.add_message_handler("place_order", self.place_order_handler_async)

    # Function to simulate order execution and sending order status
    # back to the client
    async def execute_order_async(self, client: WebsocketAppClientHandler,
                                  place_order_request: PlaceOrderRequest,
                                  new_order: Order):
        # Sleep for a few seconds
        await asyncio.sleep(5)

        if not client.Closed:
            # Change the order status to completed
            new_order.OrderStatus = "Completed"

            # Send the order status to the client (one-way message)
            await client.send_obj_async("order_status", new_order)
        else:
            print('client connection not available for ' + str(hash(client)))

    # Handler function to handle place order requests
    async def place_order_handler_async(self, client: WebsocketAppClientHandler, msg: WebsocketAppMessage):
        # Get the PlaceOrderRequest object from the message JSON data
        place_order_request_dict = jsonpickle.decode(msg.JsonData)
        place_order_request = PlaceOrderRequest(**place_order_request_dict)

        # Create a new order object with Pending status
        new_order = Order()
        new_order.Id = uuid.uuid4().hex
        new_order.Symbol = place_order_request.Symbol
        new_order.Market = place_order_request.Market
        new_order.Quantity = place_order_request.Quantity
        new_order.AveragePrice = place_order_request.Price * 90/100

        # Send response back to the client, saying the order is now pending
        await client.send_response_obj_async(msg, new_order)

        # Invoke the order execution
        asyncio.create_task(self.execute_order_async(client, place_order_request, new_order))

    async def on_connection_closed_async(self, client):
        print('client closed ' + str(hash(client)))

    async def on_new_connection_async(self, client):
        print('new client connected ' + str(hash(client)))
