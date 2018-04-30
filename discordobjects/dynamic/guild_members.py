import asyncio
import logging
import typing
import weakref

from ..client import DiscordClientAsync
from ..constants import SocketEventNames
from ..static import GuildMember
from ..static import User
from .base_dynamic import BaseDynamic
from ..exceptions import MemberNotInGuild


class LiveGuildMembers(BaseDynamic):

    def __init__(self, client_bind: DiscordClientAsync, guild_id: str,
                 event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
                 start_immediately: bool = True):
        self.guild_id = guild_id
        self.members: typing.Dict[str, GuildMember] = None

        super().__init__(client_bind, ('ADD', 'UPDATE', 'REMOVE'), event_loop, start_immediately)

    async def _auto_update(self) -> None:
        self.members = {x['user']['id']: GuildMember(self.client_bind, **x, guild_id=self.guild_id) async for x in
                        self.client_bind.guild_member_iter(self.guild_id)}

        self.await_init.set_result(True)

        async for event_dict, event_name in self.client_bind.event_gen_multiple(
                (SocketEventNames.GUILD_MEMBER_ADD,
                 SocketEventNames.GUILD_MEMBER_REMOVE,
                 SocketEventNames.GUILD_MEMBER_UPDATE)):

            if event_dict['guild_id'] == self.guild_id:
                if event_name == SocketEventNames.GUILD_MEMBER_UPDATE:
                    self._update_guild_member(event_dict)
                elif event_name == SocketEventNames.GUILD_MEMBER_ADD:
                    self._add_guild_member(event_dict)
                elif event_name == SocketEventNames.GUILD_MEMBER_REMOVE:
                    self._remove_guild_member(event_dict)
                else:
                    logging.error(f"LiveGuildMembers received unpredicted event of the name {event_name}")

    def _add_guild_member(self, event_dict: dict):
        user_id = event_dict['user']['id']

        self.members[user_id] = GuildMember(self.client_bind, **event_dict)

        asyncio.ensure_future(self.queue_dispenser.event_put('ADD', weakref.proxy(self.members[user_id])))

    def _remove_guild_member(self, event_dict: dict):
        user_id = event_dict['user']['id']

        member = self.members.pop(user_id)

        asyncio.ensure_future(self.queue_dispenser.event_put('REMOVE', member))

    def _update_guild_member(self, event_dict: dict):
        user_id = event_dict['user']['id']
        self.members[user_id].nickname = event_dict['nick']
        self.members[user_id].roles_ids = event_dict['roles']

        self.members[user_id].username = event_dict['user']['username']
        self.members[user_id].discriminator = event_dict['user']['discriminator']
        self.members[user_id].avatar_hash = event_dict['user']['avatar']

        asyncio.ensure_future(self.queue_dispenser.event_put('UPDATE', weakref.proxy(self.members[user_id])))

    async def on_guild_member_joined(self) -> typing.AsyncGenerator[GuildMember, None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'ADD')
        while True:
            yield (await queue.get())[0]

    async def on_guild_member_update(self) -> typing.AsyncGenerator[GuildMember, None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'UPDATE')
        while True:
            yield (await queue.get())[0]

    async def on_guild_member_leave(self) -> typing.AsyncGenerator[GuildMember, None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'REMOVE')
        while True:
            yield (await queue.get())[0]

    @typing.overload
    def __getitem__(self, user: User) -> GuildMember:
        ...

    @typing.overload
    def __getitem__(self, user_id: str) -> GuildMember:
        ...

    def __getitem__(self, u) -> GuildMember:
        try:
            if isinstance(u, str):
                return weakref.proxy(self.members[u])
            elif isinstance(u, User):
                return weakref.proxy(self.members[u.snowflake])
        except KeyError:
            raise MemberNotInGuild

        raise NotImplementedError(f"__getitem__ with the type {type(u)} is not supported")

    def __iter__(self) -> typing.Generator[GuildMember, None, None]:
        for gm in self.members:
            yield weakref.proxy(gm)


class GuildMemberLinked(GuildMember):
    pass
