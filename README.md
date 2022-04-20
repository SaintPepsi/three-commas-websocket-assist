# three-commas-websocket-assist

### 1. Setting up the listener
First construct an identifier:
```Python
deals_channel_identifier = construct_socket_data(
    api_key=API_KEY,
    api_secret=API_SECRET,
    channel="DealsChannel"
)
```

Pass the identifier to `ThreeCommasWebsocketMaster`:
```Python
st = ThreeCommasWebsocketMaster(
    identifier=deals_channel_identifier
)
```

### 2. Handle event
Pass a custom event handler to  the `ThreeCommasWebsocketMaster` to handle any event based on your deal channel:
Event handler is `Callable[[Dict], None]`
```Python
st = ThreeCommasWebsocketMaster(
    identifier=deals_channel_identifier,
    external_event_handler=sample_event_handler
)
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