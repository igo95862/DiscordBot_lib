import asyncio
import logging
import typing

from .. import socket_events_names
from ..discordclient import DiscordClient
from ..static.guild_role import Role
from ..util import QueueDispenser


class LiveGuildRoles:

    def __init__(self, client_bind: DiscordClient, guild_id: str,
                 event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop(),
                 start_immediately: bool = True):
        self.client_bind = client_bind
        self.guild_id = guild_id

        self.role_dicts = {x['id']: x for x in self.client_bind.guild_role_list(self.guild_id)}

        self.queue_dispenser = QueueDispenser(('CREATE', 'UPDATE', 'DELETE'))
        self.auto_update_task: asyncio.Task = None
        if start_immediately:
            self.auto_update_task = event_loop.create_task(self.auto_update())

    async def auto_update(self) -> None:
        async for event_dict, event_name in self.client_bind.event_gen_multiple(
                (socket_events_names.GUILD_ROLE_CREATE,
                 socket_events_names.GUILD_ROLE_UPDATE,
                 socket_events_names.GUILD_ROLE_DELETE)):
            if event_dict['guild_id'] == self.guild_id:
                if event_name == socket_events_names.GUILD_ROLE_CREATE:
                    self._add_role(event_dict)
                elif event_name == socket_events_names.GUILD_ROLE_UPDATE:
                    self._update_role(event_dict)
                elif event_name == socket_events_names.GUILD_ROLE_DELETE:
                    self._delete_role(event_dict)
                else:
                    logging.warning(f"LiveGuildRoles received unpredicted event of the name {event_name}")

    def _add_role(self, event_dict: dict):
        role_dict = event_dict['role']
        role_id = role_dict['id']
        self.role_dicts[role_id] = role_dict

        role = Role(self.client_bind, **role_dict)

        asyncio.ensure_future(self.queue_dispenser.event_put('CREATE', role))

    def _update_role(self, event_dict: dict):
        role_dict = event_dict['role']
        role_id = role_dict['id']
        self.role_dicts[role_id] = role_dict

        role = Role(self.client_bind, **role_dict)

        asyncio.ensure_future(self.queue_dispenser.event_put('UPDATE', role))

    def _delete_role(self, event_dict: dict):
        role_id = event_dict['role_id']
        role_dict = self.role_dicts.pop(role_id)

        role = Role(self.client_bind, **role_dict)

        asyncio.ensure_future(self.queue_dispenser.event_put('DELETE', role))

    async def on_role_created(self) -> typing.AsyncGenerator[Role, None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'CREATE')
        while True:
            yield (await queue.get())[0]

    async def on_role_update(self) -> typing.AsyncGenerator[Role, None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'UPDATE')
        while True:
            yield (await queue.get())[0]

    async def on_role_delete(self) -> typing.AsyncGenerator[Role, None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'DELETE')
        while True:
            yield (await queue.get())[0]

    def get_role_by_name(self, role_name: str) -> typing.Union[Role, None]:
        for d in self.role_dicts.values():
            if role_name == d['name']:
                return Role(self.client_bind, **d)
        return None

    def get_role_by_id(self, role_id: str) -> Role:
        return Role(self.client_bind, **self.role_dicts[role_id])

    def get_role_position_by_id(self, role_id: str) -> int:
        return self.role_dicts[role_id]['position']

    def get_role_id_by_name(self, role_name: str) -> typing.Union[str, None]:
        for d in self.role_dicts.values():
            if role_name == d['name']:
                return d['id']
        return None

    def get_role_name_by_id(self, role_id: str) -> str:
        return self.role_dicts[role_id]['name']

    def __iter__(self) -> typing.Generator[Role, None, None]:
        for d in self.role_dicts.values():
            yield Role(self.client_bind, **d)
