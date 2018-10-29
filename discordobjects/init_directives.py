from asyncio import get_event_loop, wait

from .client import DiscordClientAsync
from .guild_unit import GuildUnit
from typing import Type, Tuple


def init_guild(token: str, guild_id: str, guild_class: Type[GuildUnit] = GuildUnit) -> GuildUnit:
    loop = get_event_loop()
    client = DiscordClientAsync(token, use_socket=False)
    guild_unit = guild_class(client, guild_id, loop)
    client.start_socket()
    loop.run_until_complete(guild_unit)
    return guild_unit


def init_multiple_guilds(token: str, *args: str, guild_class: Type[GuildUnit] = GuildUnit) -> Tuple[GuildUnit, ...]:
    loop = get_event_loop()
    client = DiscordClientAsync(token, use_socket=False)
    guilds = tuple((guild_class(client, x, loop) for x in args))
    client.start_socket()
    loop.run_until_complete(wait(fs=guilds, loop=loop))
    return guilds
