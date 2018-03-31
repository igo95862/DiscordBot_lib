from ..discordclient import DiscordClient


class Invite:

    def __init__(self, client_bind: DiscordClient, code: str, guild: dict, channel: dict, inviter: dict):
        self.client_bind = client_bind
        self.code = code
        self.partial_guild_dict = guild
        self.partial_channel_dict = channel
        self.inviter_user_dict = inviter
