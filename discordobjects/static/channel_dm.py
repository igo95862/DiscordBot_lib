import typing

from .channel_text import TextChannel
from ..discordclient import DiscordClient


class DmChannel(TextChannel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, type: int, last_message_id: str,
                 recipients: typing.List[dict], last_pin_timestamp: str = None):
        super().__init__(client_bind, id, type, last_message_id, last_pin_timestamp)
        self.recipients_dicts = recipients
