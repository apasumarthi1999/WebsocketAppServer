from .app_client import *


class WebsocketAppServer(object):
    """
    Class representing the websocket app server.
    Inherit from this class to build your websocket app server
    """
    def __init__(self, port: int):
        self.Port = port
        self.MessageHandlerMap = {}

    async def handler_async(self, websocket):
        """
        Handles the new websocket connections

        :param websocket: newly connected websocket
        :return: Void
        """
        client = WebsocketAppClientHandler(websocket, self)
        await self.on_new_connection_async(client)
        await client.initialize_async()

    async def initialize_async(self):
        """
        Starts the websocket app server on a given port (any IP associated with the current system)

        :return: Void
        """
        async with websockets.serve(self.handler_async, "", self.Port):
            await asyncio.Future()  # run forever

    def add_message_handler(self, name, handler):
        """
        Add a message handler method/function to a message name

        :param name: Message name string
        :param handler: Handler function/method to handle this message
        :return: Void
        """
        self.MessageHandlerMap[name] = handler

    async def on_new_connection_async(self, client):
        """
        Override for handling new client connection

        :return: Void
        """
        pass

    async def on_connection_closed_async(self, client):
        """
        Override for handling connection close

        :return: Void
        """
        pass


class WebsocketAppClientHandler(WebsocketAppClient):
    """

    """
    def __init__(self, websocket, server: WebsocketAppServer):
        WebsocketAppClient.__init__(self)
        self.Server = server
        self.Websocket = websocket

    async def initialize_async(self):
        await self.attach_async(self.Websocket)

    async def on_connection_closed_async(self):
        await self.Server.on_connection_closed_async(self)

    async def handle_message_async(self, message):
        print('WebsocketsApp Side: ' + message)

        msg_dict = jsonpickle.decode(message)
        msg = WebsocketAppMessage(**msg_dict)

        if msg.Name in self.Server.MessageHandlerMap:
            handler = self.Server.MessageHandlerMap[msg.Name]
        else:
            handler = None

        if handler is None:
            if msg.MessageType == WebsocketAppMessageType.Request:
                msg.MessageType = WebsocketAppMessageType.Response
                msg.JsonData = ""
                await self.send_async(msg)
            else:
                if msg.MessageType == WebsocketAppMessageType.Response or \
                        msg.MessageType == WebsocketAppMessageType.ErrorResponse:
                    if msg.CorId in self.CorIdMessageMap:
                        async_waiter = self.CorIdMessageMap[msg.CorId]
                        async_waiter.Message = msg
                        del self.CorIdMessageMap[msg.CorId]
                        async_waiter.WaiterEvent.set()
        else:
            await handler(self, msg)
