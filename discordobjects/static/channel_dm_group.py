import typing

from .channel_dm import DmChannel
from ..client import DiscordClientAsync


class DmGroupChannel(DmChannel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, type: int, last_message_id: str,
                 recipients: typing.List[dict], icon: str, owner_id: str, last_pin_timestamp: str = None,
                 **kwargs):
        super().__init__(client_bind, id, type, last_message_id, recipients, last_pin_timestamp)
        self.icon_hash = icon
        self.owner_id = owner_id

        self.kwargs_handler(**kwargs)
