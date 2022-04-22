import websockets
import jsonpickle
from websockets.exceptions import WebSocketException

from .app_types import *


class WebsocketAppClient(object):
    """
    Class representing the websocket app client. This class object is also available on the websocket app server side
    to represent the remove websocket connection.
    Inherit from this class to build your websocket app client.
    """
    def __init__(self):
        self.MessageHandlerMap = {}
        self.CorIdMessageMap = {}
        self.CorIdCounter = ThreadSafeCounter()
        self.Websocket = None
        self.Url = None
        self.ProcessMessageTask = None
        self.Closed = False

    async def process_messages_async(self):
        """
        Process the websocket messages

        :return: Void
        """
        while True:
            try:
                message = await self.Websocket.recv()
                await self.handle_message_async(message)
            except WebSocketException:
                self.Closed = True
                await self.on_connection_closed_async()
                break

    async def on_connection_closed_async(self):
        """
        Override for handling connection close

        :return: Void
        """
        pass

    async def connect_async(self, url: str):
        """
        Connect to a websocket app server

        :param url: Url of the websocket app server to connect
        :return: Void
        """
        self.Url = url
        self.Websocket = await websockets.connect(self.Url)
        self.ProcessMessageTask = asyncio.create_task(self.process_messages_async())

    async def attach_async(self, websocket):
        """
        Attach the underlying remote client socket to the connection.
        Used by websocket app server.

        :param websocket: Websocket object
        :return: Void
        """
        self.Websocket = websocket
        await self.process_messages_async()

    async def execute_async(self,
                            websocket_message: WebsocketAppMessage) -> \
            WebsocketAppMessage:
        """
        Sends a request websocket app message to the remote party and waits for and returns the response message.
        This is an awaitable method that takes in a WebsocketAppMessage
        with Request message type, sends the message to the other party of the websocket connection.
        This method waits until the other party responds with a response message to the request.
        This method handles the correlation between the request and the response message and also throw an exception,
        if other party responds with an error message.

        :param websocket_message: WebsocketAppMessage object that will be sent as request message
        :return: Response WebsocketAppMessage object
        """
        async_waiter = AsyncWaiter()
        self.CorIdMessageMap[websocket_message.CorId] = async_waiter
        await self.Websocket.send(jsonpickle.encode(websocket_message, False))
        await async_waiter.WaiterEvent.wait()

        if async_waiter.Message.MessageType == WebsocketAppMessageType.ErrorResponse:
            raise Exception(async_waiter.Message.Error)

        return async_waiter.Message

    async def handle_message_async(self, message):
        """
        This method reads Websocket app messages and hand over them to user supplied message handlers for processing

        :param message: WebsocketAppMessage object in a JSON string format
        :return: Void
        """
        print('Client Side: ' + message)

        msg_dict = jsonpickle.decode(message)
        msg = WebsocketAppMessage(**msg_dict)

        if msg.Name in self.MessageHandlerMap:
            handler = self.MessageHandlerMap[msg.Name]
        else:
            handler = None

        if handler is None:
            if msg.MessageType == WebsocketAppMessageType.Request:
                msg.MessageType = WebsocketAppMessageType.Response
                msg.JsonData = ""
                await self.Websocket.send(jsonpickle.encode(msg, False))
            else:
                if msg.MessageType == WebsocketAppMessageType.Response or \
                        msg.MessageType == WebsocketAppMessageType.ErrorResponse:
                    if msg.CorId in self.CorIdMessageMap:
                        async_waiter = self.CorIdMessageMap[msg.CorId]
                        async_waiter.Message = msg
                        del self.CorIdMessageMap[msg.CorId]
                        async_waiter.WaiterEvent.set()
        else:
            await handler(msg)

    async def send_async(self, websocket_message: WebsocketAppMessage):
        """
        Sends a websocket app message to the remote party.
        This is an awaitable method that takes in WebsocketAppMessage as input and sends the message to the other party
        of the websocket connection, and returns immediately to the calling program

        :param websocket_message: WebsocketAppMessage
        :return: Void
        """
        await self.Websocket.send(jsonpickle.encode(websocket_message, False))

    async def send_obj_async(self, msg_name, obj):
        """
        Sends a custom object to the remote party along with a message name.
        This is an awaitable method that takes in message name and a custom python object as inputs, packages the object
        inside a WebsocketAppMessage, sends the message to the other party of the websocket connection,
        and returns immediately to the calling program

        :param msg_name: Message name string
        :param obj: Custom object to send to remote party
        :return: Void
        """
        await self.send_async(WebsocketAppMessage(
            msg_name,
            WebsocketAppMessageType.Oneway,
            await self.CorIdCounter.increment_async(),
            jsonpickle.encode(obj, False),
            None
        ))

    async def execute_obj_async(self, msg_name, obj) -> WebsocketAppMessage:
        """
        Sends a request object to the remote party along with message name and waits for and
        returns the response message.
        This is an awaitable method that takes in a WebsocketAppMessage
        with Request message type, sends the message to the other party of the websocket connection.
        This method waits until the other party responds with a response message to the request.
        This method handles the correlation between the request and the response message and also throw an exception,
        if other party responds with an error message.

        :param msg_name: Message name string
        :param obj: Custom object to send to remote party
        :return: Response WebsocketAppMessage object
        """
        return await self.execute_async(WebsocketAppMessage(
            msg_name,
            WebsocketAppMessageType.Request,
            await self.CorIdCounter.increment_async(),
            jsonpickle.encode(obj, False),
            None
        ))

    async def send_response_obj_async(self, websocket_message, obj):
        """
        Sends a response websocket app message to the remote party.
        This is an awaitable method that takes in request message and a custom python object as inputs,
        packages the object inside a WebsocketAppMessage, sends the response message to the other party of the
        websocket connection, and returns immediately to the calling program

        :param websocket_message: Request WebsocketAppMessage object
        :param obj: Custom object to send as response
        :return: Void
        """
        await self.send_async(WebsocketAppMessage(
            websocket_message.Name,
            WebsocketAppMessageType.Response,
            websocket_message.CorId,
            jsonpickle.encode(obj, False),
            None
        ))

    async def send_error_response_async(self, websocket_message: WebsocketAppMessage, error_message):
        """
        Sends a error response websocket app message to the remote party.
        This is an awaitable method that takes in request message and a error message string as inputs,
        creates a WebsocketAppMessage, sends the error response message to the other party of the websocket connection,
        and returns immediately to the calling program

        :param websocket_message:  WebsocketAppMessage object of the request
        :param error_message: Error message string
        :return: Void
        """
        await self.send_async(WebsocketAppMessage(
            websocket_message.Name,
            WebsocketAppMessageType.ErrorResponse,
            websocket_message.CorId,
            "",
            error_message
        ))

    def add_message_handler(self, name, handler):
        """
        Add a message handler method/function to a message name

        :param name: Message name string
        :param handler: Handler function/method to handle this message
        :return: Void
        """
        self.MessageHandlerMap[name] = handler

    async def disconnect(self, reason: str):
        """
        Disconnect the websocket connection

        :param reason: Disconnect reason string
        :return:
        """
        await self.Websocket.close(1000, reason)
