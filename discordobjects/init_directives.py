from asyncio import get_event_loop

from .client import DiscordClientAsync
from .dynamic import GuildUnit


def init_guild(token: str, guild_id: str):
    loop = get_event_loop()
    client = DiscordClientAsync(token, use_socket=False)
    guild_unit = GuildUnit(client, guild_id, loop)
    client.start_socket()
    return guild_unit
