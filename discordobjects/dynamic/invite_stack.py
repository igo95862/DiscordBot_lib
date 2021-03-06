import typing
from collections import deque as deque

from ..client import DiscordClientAsync
from ..static.guild_invite import GuildInvite


class InviteStack:

    def __init__(self, client_bind: DiscordClientAsync, guild_id: str):
        self.client_bind = client_bind
        self.guild_id = guild_id
        self.uncollected_queue = deque()
        self.invites_dicts: typing.Dict[str, dict] = []

    async def refresh(self) -> None:
        new_invites: typing.List[dict] = await self.client_bind.guild_invite_list(self.guild_id)
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

    async def checkout(self) -> typing.Union[GuildInvite, None]:
        await self.refresh()
        if len(self.uncollected_queue) != 0:
            invite_code = self.uncollected_queue.popleft()
            return self.get_invite(invite_code)
        else:
            return None

    def get_invite(self, invite_code: str) -> GuildInvite:
        return GuildInvite(self.client_bind, **self.invites_dicts[invite_code])
