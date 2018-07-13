from asyncio import get_event_loop, wait

from .client import DiscordClientAsync
from .dynamic import GuildUnit
from typing import Iterable, Tuple


def init_guild(token: str, guild_id: str):
    loop = get_event_loop()
    client = DiscordClientAsync(token, use_socket=False)
    guild_unit = GuildUnit(client, guild_id, loop)
    client.start_socket()
    loop.run_until_complete(guild_unit)
    return guild_unit


def init_multiple_guilds(token: str, *args: str) -> Tuple[GuildUnit, ...]:
    loop = get_event_loop()
    client = DiscordClientAsync(token, use_socket=False)
    guilds = tuple((GuildUnit(client, x, loop) for x in args))
    client.start_socket()
    loop.run_until_complete(wait(fs=guilds, loop=loop))
    return guilds
