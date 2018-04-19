import typing

from ..client import DiscordClientAsync
from ..static import User
from ..static.auditlog import AuditLog, AuditKick, AuditBanAdd


class AuditStack:

    def __init__(self, client_bind: DiscordClientAsync, guild_id: str, audit_id: int):
        self.client_bind = client_bind
        self.guild_id = guild_id
        self.uncollected_queue = []
        self.audit_id = audit_id
        audit_logs, *_ = self.client_bind.audit_log_get(self.guild_id, filter_action_type=self.audit_id, limit=1)
        try:
            self.last_audit_id = audit_logs[0]['id']
        except IndexError:
            self.last_audit_id = None

    async def _refresh_gen(self) -> typing.Generator[dict, None, None]:
        most_recent_log_id = None
        async for audit_logs_dict, users_dicts, webhook_dicts in self.client_bind.audit_log_iter(
                self.guild_id, filter_action_type=self.audit_id):
            if most_recent_log_id is not None:
                most_recent_log_id = audit_logs_dict[0]['id']

            if audit_logs_dict['id'] == self.last_audit_id:
                self.last_audit_id = most_recent_log_id
                return
            else:
                yield audit_logs_dict

    async def refresh(self) -> None:
        raise NotImplementedError

    async def checkout(self, *args, **kwargs) -> None:
        self.refresh()
        raise NotImplementedError


class AuditStackKicks(AuditStack):

    def __init__(self, client_bind: DiscordClientAsync, guild_id: str):
        super().__init__(client_bind, guild_id, AuditLog.MEMBER_KICK)
        self.uncollected_queue = typing.cast(typing.List[AuditKick], self.uncollected_queue)

    async def refresh(self) -> None:
        async for d in self._refresh_gen():
            self.uncollected_queue.append(AuditKick(self.client_bind, **d))

    async def checkout(self, search_target: User) -> typing.Union[AuditKick, None]:
        await self.refresh()
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

    def __init__(self, client_bind: DiscordClientAsync, guild_id: str):
        super().__init__(client_bind, guild_id, AuditLog.MEMBER_BAN_ADD)
        self.uncollected_queue = typing.cast(typing.List[AuditBanAdd], self.uncollected_queue)

    async def refresh(self) -> None:
        async for d in self._refresh_gen():
            self.uncollected_queue.append(AuditBanAdd(self.client_bind, **d))

    async def checkout(self, search_target: User) -> typing.Union[AuditBanAdd, None]:
        await self.refresh()
        entry_index = None
        for i, entry in enumerate(self.uncollected_queue):
            if entry.is_target(search_target):
                entry_index = i
                break

        if entry_index is not None:
            return self.uncollected_queue.pop(entry_index)
        else:
            return None
