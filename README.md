# three-commas-websocket-assist - No Longer Maintained, Please fork if you want to use it.

GNU General Public License v3.0

`pip install three-commas-websocket-assist`

### Import
```
from three-commas-websocket-assist import ThreeCommasWebsocketHandler
```

Supports seperate threading. pass `seperate_thread=True` to `start_listener()` to run it on a seperate thread (i.e. when running along side flask or mutliple streams)

### 1. Setting up the listener
Pass 3commas api key and secret or selfsigned private key and the channel you desire to `ThreeCommasWebsocketHandler`:
```Python
st = ThreeCommasWebsocketHandler(
    api_key=API_KEY,
    api_secret=API_SECRET,
    api_selfsigned=API_SELFSIGNED,
    channel="DealsChannel",
)
st.start_listener()
```
`ThreeCommasWebsocketHandler` automatically generates the stream identifier and uses that for the stream


### 2. Handle event
Pass a custom event handler to  the `ThreeCommasWebsocketHandler` to handle any event based on your deal channel:
Event handler is `Callable[[Dict], None]`
```Python
st = ThreeCommasWebsocketHandler(
    api_key=API_KEY,
    api_secret=API_SECRET,
    api_selfsigned=API_SELFSIGNED,
    channel="DealsChannel",
    external_event_handler=sample_event_handler
)
st.start_listener()
```

Sample event handler:
```Python
def sample_event_handler(data:Dict) -> None:
    """
    Sample Event Handler for websocket
    """
    _LOGGER.debug("Bot_id: %s", data['bot_id'])

    # Do something with the data here
```

### 3. Run it on seperate thread:
```Python
st = ThreeCommasWebsocketHandler(
    api_key=API_KEY,
    api_secret=API_SECRET,
    api_selfsigned=API_SELFSIGNED,
    channel="DealsChannel",
    external_event_handler=sample_event_handler
)
st.start_listener(seperate_thread=True)
```
