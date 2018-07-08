from asyncio import get_event_loop

from .client import DiscordClientAsync
from .dynamic import GuildUnit
from typing import Iterable, Tuple


def init_guild(token: str, guild_id: str):
    loop = get_event_loop()
    client = DiscordClientAsync(token, use_socket=False)
    guild_unit = GuildUnit(client, guild_id, loop)
    client.start_socket()
    return guild_unit

def general_init(
        token: str, guild_ids: Iterable[str], channel_ids: Iterable[str], message_ids: Iterable[Tuple[str, str]]):
    pass