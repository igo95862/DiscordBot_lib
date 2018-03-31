import asyncio
import logging
import typing

from .audit_stack import AuditStackBanAdd, AuditStackKicks
from .invite_stack import InviteStack
from .. import socket_events_names
from ..discordclient import DiscordClient
from ..static.auditlog import AuditKick, AuditBanAdd
from ..static.guild_invite import GuildInvite
from ..static.guild_member import GuildMember
from ..static.guild_role import Role
from ..util import QueueDispenser


class LiveGuildMembers:

    def __init__(self, client_bind: DiscordClient, guild_id: str,
                 event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
        self.client_bind = client_bind
        self.guild_id = guild_id
        self.member_dicts = {x['user']['id']: x for x in self.client_bind.guild_member_iter(guild_id)}

        self.queue_dispenser = QueueDispenser(('ADD', 'UPDATE', 'SELF-LEAVE', 'BAN', 'KICK'))

        self.audit_kick_stack = AuditStackKicks(self.client_bind, self.guild_id)
        self.audit_ban_add_stack = AuditStackBanAdd(self.client_bind, self.guild_id)
        self.invite_stack = InviteStack(self.client_bind, self.guild_id)

        self.auto_update_task = event_loop.create_task(self.auto_update())

    async def auto_update(self) -> None:
        async for event_dict, event_name in self.client_bind.event_gen_multiple(
                (socket_events_names.GUILD_MEMBER_ADD,
                 socket_events_names.GUILD_MEMBER_REMOVE,
                 socket_events_names.GUILD_MEMBER_UPDATE)):

            if event_dict['guild_id'] == self.guild_id:
                if event_name == socket_events_names.GUILD_MEMBER_UPDATE:
                    self._update_guild_member(event_dict)
                elif event_name == socket_events_names.GUILD_MEMBER_ADD:
                    self._add_guild_member(event_dict)
                elif event_name == socket_events_names.GUILD_MEMBER_REMOVE:
                    self._remove_guild_member(event_dict)
                else:
                    logging.warning(f"LiveGuildMembers received unpredicted event of the name {event_name}")

    def _add_guild_member(self, event_dict: dict):
        user_id = event_dict['user']['id']
        member_dict = self.client_bind.guild_member_get(self.guild_id, user_id)
        self.member_dicts[user_id] = member_dict

        member = GuildMember(self.client_bind, **member_dict, parent_guild_id=self.guild_id)
        invite = self.invite_stack.checkout()

        asyncio.ensure_future(self.queue_dispenser.event_put('ADD', (member, invite)))

    def _remove_guild_member(self, event_dict: dict):
        user_id = event_dict['user']['id']

        member_dict = self.member_dicts.pop(user_id)
        member = GuildMember(self.client_bind, **member_dict, parent_guild_id=self.guild_id)

        audit_kick_entry = self.audit_kick_stack.checkout(member)
        audit_ban_entry = self.audit_ban_add_stack.checkout(member)

        if audit_kick_entry is None and audit_ban_entry is None:
            asyncio.ensure_future(self.queue_dispenser.event_put('SELF-LEAVE', member))
        elif audit_ban_entry is not None:
            asyncio.ensure_future(self.queue_dispenser.event_put('BAN', (member, audit_ban_entry)))
        elif audit_kick_entry is not None:
            asyncio.ensure_future(self.queue_dispenser.event_put('KICK', (member, audit_kick_entry)))
        else:
            logging.warning('Guild member left, but both got kicked and banned!')

    def _update_guild_member(self, event_dict: dict):
        user_id = event_dict['user']['id']
        self.member_dicts[user_id]['nick'] = event_dict['nick']
        self.member_dicts[user_id]['user'] = event_dict['user']
        self.member_dicts[user_id]['roles'] = event_dict['roles']

        member = GuildMember(self.client_bind, **self.member_dicts[user_id], parent_guild_id=self.guild_id)

        asyncio.ensure_future(self.queue_dispenser.event_put('UPDATE', member))

    async def on_guild_member_joined(self) -> typing.AsyncGenerator[typing.Tuple[GuildMember, GuildInvite], None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'ADD')
        while True:
            yield (await queue.get())[0]

    async def on_guild_member_self_leave(self) -> typing.AsyncGenerator[GuildMember, None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'SELF-LEAVE')
        while True:
            yield (await queue.get())[0]

    async def on_guild_member_update(self) -> typing.AsyncGenerator[GuildMember, None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'UPDATE')
        while True:
            yield (await queue.get())[0]

    async def on_guild_member_kicked(self) -> typing.AsyncGenerator[typing.Tuple[GuildMember, AuditKick], None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'KICK')
        while True:
            yield (await queue.get())[0]

    async def on_guild_member_banned(self) -> typing.AsyncGenerator[typing.Tuple[GuildMember, AuditBanAdd], None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'BAN')
        while True:
            yield (await queue.get())[0]

    def get_member_by_id(self, user_id: str) -> GuildMember:
        return GuildMember(self.client_bind, **self.member_dicts[user_id], parent_guild_id=self.guild_id)

    def get_members_by_role(self, role: Role) -> typing.List[GuildMember]:
        return [GuildMember(self.client_bind, **x) for x in self.member_dicts.values() if role.snowflake in x['roles']]
