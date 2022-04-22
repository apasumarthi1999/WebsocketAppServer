import asyncio
from collections import namedtuple


def fill_obj(obj, **kwargs):
    """
    Fills a custom object with the properties available in the kwargs
    :param obj: Object to be filled
    :param kwargs: kwargs with the properties
    :return: Void
    """
    for a in kwargs:
        if type(kwargs[a]) is dict:
            obj_inner = namedtuple(a, kwargs[a].keys())(*kwargs[a].values())
            setattr(obj, a, obj_inner)
        else:
            setattr(obj, a, kwargs[a])


class ThreadSafeCounter(object):
    def __init__(self):
        self.value = 0
        self._lock = asyncio.Lock()

    async def increment_async(self):
        async with self._lock:
            self.value += 1
            return str(self.value)


class AsyncWaiter(object):
    def __init__(self):
        self.WaiterEvent = asyncio.Event()
        self.Message = None


class WebsocketAppMessageType:
    Request = 'Request'
    Response = 'Response'
    Oneway = 'Oneway'
    ErrorResponse = 'ErrorResponse'


class WebsocketAppError(object):
    def __init__(self):
        self.ErrorCode: int
        self.ErrorMessage: str
        self.ErrorStackTrace: str


class WebsocketAppMessage(object):
    """
    Object used for communication between websocket app server and client
    """
    def __init__(self, name=None, message_type=None, cor_id=None, json_data=None, error=None, **kwargs):
        """
        Create a new WebsocketAppMessage object
        :param name: Name of the message
        :param message_type: Message type -> WebsocketAppMessageType
        :param cor_id: Correlation id, in case of request or response message type
        :param json_data: JSON data of the message that is being exchanged between app server and client
        :param error: Any error response from remote party, in case of errors while processing a request message
        """
        if name is None:
            fill_obj(self, **kwargs)
        else:
            self.Name = name
            self.MessageType: WebsocketAppMessageType = message_type
            self.CorId = cor_id
            self.JsonData = json_data
            self.Error: WebsocketAppError = error
