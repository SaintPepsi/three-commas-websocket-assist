#!/usr/bin/env python3
"""
Cyberjunky's 3Commas websocket helper.
Updated by SanCoca
"""
import json
import logging
import hashlib
import hmac
import threading

from typing import Callable, Dict, Literal

import rel
import websocket

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

SocketChannels = Literal["DealsChannel","SmartTradesChannel"]
SocketPaths = Literal['/deals', '/smart_trades']

channel_paths: Dict[SocketChannels, SocketPaths] = {
    "DealsChannel": "/deals",
    "SmartTradesChannel": "/smart_trades"
}

def construct_socket_data(
        api_key:str,
        api_secret:str,
        channel:SocketChannels = "DealsChannel",
    ):
    """
    Construct websocket identifier
    """
    _encoded_key = str.encode(api_secret)
    _message = str.encode(channel_paths[channel])
    _signature = hmac.new(_encoded_key, _message, hashlib.sha256).hexdigest()
    _id_data={
        'api_key': api_key,
        'signature': _signature
    }
    _users=[_id_data]
    _identifier = {
        'channel': channel,
        'users': _users
    }
    return _identifier

#print(json.dumps(identifier))

class ThreeCommasWebsocket:
    """
    Handle 3commas websocket events and data
    """

    is_running = True

    def __init__(self, on_event=None, identifier=None):
        """
        :param on_event: function that get's called on received event
        """
        self.on_event = on_event
        self.websocket = None
        self.websocket_thread = None
        self._url = 'wss://ws.3commas.io/websocket'
        self.identifier = identifier

    def __run_forever_rel_dispatcher(self):
        """
        Run forever websocket using dispatcher rel
        """
        self.websocket.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
        rel.signal(2, rel.abort)  # Keyboard Interrupt
        rel.dispatch()

    def __run_forever_thread_daemon(self):
        """
        Run forever using thread daemon
        """
        self.websocket_thread = threading.Thread(target=self.websocket.run_forever)
        self.websocket_thread.daemon = True
        self.websocket_thread.start()

    def __refresh(self):
        self.websocket = websocket.WebSocketApp(
            self._url,
            on_open=self.__on_open,
            on_error=self.__on_error,
            on_message=self.__on_message,
            on_close=self.__on_close,
        )

        self.__run_forever_rel_dispatcher()

        ### Old code for threading.
        ### if run_forever doesn't work properly
        ### you might need to remove the snippet `Run forever websocket`
        ### and uncomment the code below:
        ### and in the main script add:
        ### while True:
        ###     time.sleep(1)
        # self.__run_forever_thread_daemon()

    def start(self):
        """
        Start websocket client
        """
        _LOGGER.debug("Websocket client start")

        self.__refresh()


    def stop(self):
        """
        close websocket
        """
        self.is_running = False
        self.websocket.close()
        _LOGGER.debug("Websocket client stopped")

    def __on_open(self, ws):
        """
        On websocket open
        """
        _LOGGER.debug("Websocket open")

    def __on_close(self, ws, close_status_code, close_msg):
        """
        On Close Listener
        """
        if self.is_running:
            _LOGGER.debug("Websocket restart after close")

            self.__refresh()


    def __on_message(self, ws, message):
        """
        On message event
        """
        # _LOGGER.debug(f"Websocket data: {message}")
        try:
            message = json.loads(message)
            if "type" not in message:
                if (
                    "identifier" in message
                    and json.loads(message["identifier"])["channel"]
                    == "DealsChannel"
                    # == "SmartTradesChannel"
                ):
                    event = message["message"]
                    self.on_event(event)

                else:
                    _LOGGER.debug("Malformed data received\n%s", message)

            elif message["type"] == "welcome":
                _LOGGER.debug("Subscribing to the %s", self.identifier['channel'])
                self.websocket.send(
                    json.dumps({
                        "command": "subscribe",
                            "identifier": json.dumps(self.identifier),
                    }
                    )
                )
            elif message["type"] == "confirm_subscription":
                _LOGGER.debug("Succesfully subscribed %s", self.identifier['channel'])

            elif message["type"] == "ping":
                pass

            else:
                _LOGGER.debug("Received unknown type: %s", message)

        except Exception as error:
            _LOGGER.exception(error)

    def __on_error(self, ws, error):
        """
        On Error listener
        :param error:
        """
        _LOGGER.debug("Websocket error: %s", error)


class ThreeCommasWebsocketMaster():
    """
    Three commas websocket master handler
    """
    external_event_handler = None
    _data = None
    listener = None
    def __init__(
        self,
        identifier,
        external_event_handler: Callable[[Dict], None] = None
    ):
        self.identifier = identifier
        self.external_event_handler = external_event_handler
        self.start_listener()

    def on_event(self, data):
        """
        On websocket event received
        """
        _LOGGER.debug("3Commas websocket update received: %s", data)
        self._data = data

    def start_listener(self):
        """
        Spawn a new Listener and links it to self.on_trade.
        """
        event_handler = self.external_event_handler \
            if self.external_event_handler \
            else self.on_event

        self.listener = ThreeCommasWebsocket(event_handler, identifier=self.identifier)
        _LOGGER.debug("Starting listener")
        self.listener.start()

def sample_event_handler(data:Dict) -> None:
    """
    Sample Event Handler for websocket
    """
    _LOGGER.debug("Bot_id: %s", data['bot_id'])

    # Do something with the data here


# If script is run directly perform event handling internally. 
# otherwise call `ThreeCommasWebsocketMaster` Externally. to handle event data properly
if __name__ == "__main__":
    # If running locally fill key and secret here
    API_KEY = ""
    API_SECRET = ""

    # External event handler allows you to use different handlers for different streams.
    deals_channel_identifier = construct_socket_data(
        api_key=API_KEY,
        api_secret=API_SECRET,
        channel="DealsChannel"
    )
    st = ThreeCommasWebsocketMaster(
        identifier=deals_channel_identifier,
        external_event_handler=sample_event_handler
    )

    ### Smart trades channel identifier
    # smart_trade_channel_identifier = construct_socket_data(
    #     api_key=API_KEY,
    #     api_secret=API_SECRET,
    #     channel="SmartTradesChannel"
    # )
    # st = ThreeCommasWebsocketMaster(
    #     identifier=smart_trade_channel_identifier,
    #     external_event_handler=sample_event_handler
    # )
