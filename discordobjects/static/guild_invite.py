from .invite import Invite
from ..discordclient import DiscordClient


class GuildInvite(Invite):
    def __init__(self, client_bind: DiscordClient, code: str, guild: dict, channel: dict, inviter: dict, uses: int,
                 max_uses: int, max_age: int, temporary: bool, created_at: str, revoked: bool = None):
        super().__init__(client_bind, code, guild, channel, inviter)
        self.uses = uses
        self.max_users = max_uses
        self.max_age = max_age
        self.temporary = temporary
        self.created_at_iso8601_timestamp = created_at
        self.revoked = revoked
