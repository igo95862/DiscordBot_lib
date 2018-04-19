import asyncio
import logging
import typing
from collections import deque as Deque

from . import socket_events_names
from .discordclient import DiscordClient
from .discordobjects import *
from .util import QueueDispenser

__all__ = ['LiveGuildMembers', 'LiveGuildRoles', 'InviteStack', 'AuditStackKicks']


class LiveGuildRoles:

    def __init__(self, client_bind: DiscordClient, guild_id: str,
                 event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
        self.client_bind = client_bind
        self.guild_id = guild_id

        self.role_dicts = {x['id']: x for x in self.client_bind.guild_role_list(self.guild_id)}

        self.queue_dispenser = QueueDispenser(('CREATE', 'UPDATE', 'DELETE'))
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

    async def on_guild_member_joined(self) -> typing.AsyncGenerator[typing.Tuple['GuildMember', 'GuildInvite'], None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'ADD')
        while True:
            yield (await queue.get())[0]

    async def on_guild_member_self_leave(self) -> typing.AsyncGenerator['GuildMember', None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'SELF-LEAVE')
        while True:
            yield (await queue.get())[0]

    async def on_guild_member_update(self) -> typing.AsyncGenerator['GuildMember', None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'UPDATE')
        while True:
            yield (await queue.get())[0]

    async def on_guild_member_kicked(self) -> typing.AsyncGenerator[typing.Tuple['GuildMember', 'AuditKick'], None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'KICK')
        while True:
            yield (await queue.get())[0]

    async def on_guild_member_banned(self) -> typing.AsyncGenerator[typing.Tuple['GuildMember', 'AuditBanAdd'], None]:
        queue = asyncio.Queue()
        self.queue_dispenser.queue_add_single_slot(queue, 'BAN')
        while True:
            yield (await queue.get())[0]

    def get_member_by_id(self, user_id: str) -> GuildMember:
        return GuildMember(self.client_bind, **self.member_dicts[user_id], parent_guild_id=self.guild_id)

    def get_members_by_role(self, role: Role) -> typing.List[GuildMember]:
        return [GuildMember(self.client_bind, **x) for x in self.member_dicts.values() if role.snowflake in x['roles']]


class InviteStack:

    def __init__(self, client_bind: DiscordClient, guild_id: str):
        self.client_bind = client_bind
        self.guild_id = guild_id
        self.uncollected_queue = Deque()
        invites = self.client_bind.guild_invite_list(self.guild_id)
        self.invites_dicts = {x['code']: x for x in invites}

    def refresh(self) -> None:
        new_invites = self.client_bind.guild_invite_list(self.guild_id)
        for invite_dict in new_invites:
            new_invite_code = invite_dict['code']
            if new_invite_code in self.invites_dicts.keys():
                old_uses_value = self.invites_dicts[new_invite_code]['uses']
                new_uses_value = invite_dict['uses']
                difference = new_uses_value - old_uses_value
                if difference != 0:
                    for _ in range(difference):
                        self.uncollected_queue.append(new_invite_code)
            else:
                if invite_dict['uses'] != 0:
                    for _ in range(invite_dict['uses']):
                        self.uncollected_queue.append(new_invite_code)

        self.invites_dicts = {x['code']: x for x in new_invites}

    def checkout(self) -> typing.Union['GuildInvite', None]:
        self.refresh()
        if len(self.uncollected_queue) != 0:
            invite_code = self.uncollected_queue.popleft()
            return self.get_invite(invite_code)
        else:
            return None

    def get_invite(self, invite_code: str):
        return GuildInvite(self.client_bind, **self.invites_dicts[invite_code])


class AuditStack:

    def __init__(self, client_bind: DiscordClient, guild_id: str, audit_id: int):
        self.client_bind = client_bind
        self.guild_id = guild_id
        self.uncollected_queue = []
        self.audit_id = audit_id
        audit_logs, *_ = self.client_bind.audit_log_get(self.guild_id, filter_action_type=self.audit_id, limit=1)
        try:
            self.last_audit_id = audit_logs[0]['id']
        except IndexError:
            self.last_audit_id = None

    def _refresh_gen(self) -> typing.Generator[dict, None, None]:
        most_recent_log_id = None
        for audit_logs_dict, users_dicts, webhook_dicts in self.client_bind.audit_log_iter(
                self.guild_id, filter_action_type=self.audit_id):
            if most_recent_log_id is not None:
                most_recent_log_id = audit_logs_dict[0]['id']

            if audit_logs_dict['id'] == self.last_audit_id:
                self.last_audit_id = most_recent_log_id
                return
            else:
                yield audit_logs_dict

    def refresh(self) -> None:
        raise NotImplementedError

    def checkout(self, *args, **kwargs) -> None:
        self.refresh()
        raise NotImplementedError


class AuditStackKicks(AuditStack):

    def __init__(self, client_bind: DiscordClient, guild_id: str):
        super().__init__(client_bind, guild_id, AuditLog.MEMBER_KICK)
        self.uncollected_queue = typing.cast(typing.List[AuditKick], self.uncollected_queue)

    def refresh(self) -> None:
        for d in self._refresh_gen():
            self.uncollected_queue.append(AuditKick(self.client_bind, **d))

    def checkout(self, search_target: 'User') -> typing.Union['AuditKick', None]:
        self.refresh()
        entry_index = None
        for i, entry in enumerate(self.uncollected_queue):
            if entry.is_target(search_target):
                entry_index = i
                break

        if entry_index is not None:
            return self.uncollected_queue.pop(entry_index)
        else:
            return None


class AuditStackBanAdd(AuditStack):

    def __init__(self, client_bind: DiscordClient, guild_id: str):
        super().__init__(client_bind, guild_id, AuditLog.MEMBER_BAN_ADD)
        self.uncollected_queue = typing.cast(typing.List[AuditBanAdd], self.uncollected_queue)

    def refresh(self) -> None:
        for d in self._refresh_gen():
            self.uncollected_queue.append(AuditBanAdd(self.client_bind, **d))

    def checkout(self, search_target: 'User') -> typing.Union['AuditBanAdd', None]:
        self.refresh()
        entry_index = None
        for i, entry in enumerate(self.uncollected_queue):
            if entry.is_target(search_target):
                entry_index = i
                break

        if entry_index is not None:
            return self.uncollected_queue.pop(entry_index)
        else:
            return None


'''
class AuditKickStack:

    def __init__(self, client_bind: DiscordClient, guild_id: str):
        self.client_bind = client_bind
        self.guild_id = guild_id
        self.uncollected_queue = []
        last_audit_entry_dict = self.client_bind.audit_log_get(self.guild_id, filter_action_type=20, limit=1)
        self.last_audit_entry_id = last_audit_entry_dict['audit_log_entries'][0]['id']

    def refresh_async(self) -> None:
        new_kick_log = self.client_bind.audit_log_get(self.guild_id, filter_action_type=20, limit=100)
        new_kick_list = new_kick_log['audit_log_entries']
        new_slice = None
        for i in range(len(new_kick_list)):
            if new_kick_list[i]['id'] == self.last_audit_entry_id:
                if i != 0:
                    new_slice = new_kick_list[:i]
                break

        if new_slice is not None:
            self.uncollected_queue += new_slice
            self.last_audit_entry_id = new_slice[0]['id']

    def checkout(self, user: User) -> dict:
        self.refresh_async()
        for i in range(len(self.uncollected_queue)):
            if self.uncollected_queue[i]['target_id'] == user.snowflake:
                return self.uncollected_queue.pop(i)
'''
