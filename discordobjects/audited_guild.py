from asyncio import AbstractEventLoop

from discordobjects import DiscordClientAsync
from .guild_unit import GuildUnit
from typing import Dict


class AuditedGuild(GuildUnit):

    async def invite_punch_out(self):
        invites_data = await self.client_bind.guild_invite_list(self.snowflake)
        self._invite_uses = {x['code']: x['uses'] for x in invites_data}

    def __init__(self, client: DiscordClientAsync, guild_id: str, event_loop: AbstractEventLoop):
        super().__init__(client, guild_id, event_loop)
        self._invite_uses: Dict[str, int] = {}
