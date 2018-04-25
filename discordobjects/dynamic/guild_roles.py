import asyncio
import logging
import typing
import weakref

from ..constants import SocketEventNames
from ..client import DiscordClientAsync
from ..static.guild_role import Role
from .base_dynamic import BaseDynamic


class LiveGuildRoles(BaseDynamic):

    def __init__(self, client_bind: DiscordClientAsync, guild_id: str,
                 event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
                 start_immediately: bool = True):
        self.guild_id = guild_id
        self.roles: typing.Dict[str, RoleLinked] = None
        super().__init__(client_bind, ('CREATE', 'UPDATE', 'DELETE'), event_loop, start_immediately)

    async def _auto_update(self) -> None:
        self.roles = {x['id']: RoleLinked(self.client_bind, **x) for x in (
            await self.client_bind.guild_role_list(self.guild_id))}

        self.await_init.set_result(True)

        async for event_dict, event_name in self.client_bind.event_gen_multiple(
                (SocketEventNames.GUILD_ROLE_CREATE,
                 SocketEventNames.GUILD_ROLE_UPDATE,
                 SocketEventNames.GUILD_ROLE_DELETE)):
            if event_dict['guild_id'] == self.guild_id:
                if event_name == SocketEventNames.GUILD_ROLE_CREATE:
                    self._add_role(event_dict)
                elif event_name == SocketEventNames.GUILD_ROLE_UPDATE:
                    self._update_role(event_dict)
                elif event_name == SocketEventNames.GUILD_ROLE_DELETE:
                    self._delete_role(event_dict)
                else:
                    logging.warning(f"LiveGuildRoles received unpredicted event of the name {event_name}")

    def _add_role(self, event_dict: dict):
        role_dict = event_dict['role']
        role_id = role_dict['id']
        self.roles[role_id] = RoleLinked(self.client_bind, **role_dict)

        asyncio.ensure_future(self.queue_dispenser.event_put('CREATE', weakref.proxy(self.roles[role_id])))

    def _update_role(self, event_dict: dict):
        role_dict = event_dict['role']
        role_id = role_dict['id']
        self.roles[role_id].refresh(role_dict)

        asyncio.ensure_future(self.queue_dispenser.event_put('UPDATE', weakref.proxy(self.roles[role_id])))

    def _delete_role(self, event_dict: dict):
        role_id = event_dict['role_id']
        role = self.roles.pop(role_id)

        asyncio.ensure_future(self.queue_dispenser.event_put('DELETE', role))

    async def on_role_created(self) -> typing.AsyncGenerator['RoleLinked', None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'CREATE')
        while True:
            yield (await queue.get())[0]

    async def on_role_update(self) -> typing.AsyncGenerator['RoleLinked', None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'UPDATE')
        while True:
            yield (await queue.get())[0]

    async def on_role_delete(self) -> typing.AsyncGenerator['RoleLinked', None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'DELETE')
        while True:
            yield (await queue.get())[0]

    def __getitem__(self, index: str) -> 'RoleLinked':
        return weakref.proxy(self.roles[index])

    def __iter__(self) -> typing.Generator[Role, None, None]:
        for r in self.roles.values():
            yield weakref.proxy(r)


class RoleLinked(Role):

    def refresh(self, new_dict: dict):
        self.__init__(self.client_bind, **new_dict)