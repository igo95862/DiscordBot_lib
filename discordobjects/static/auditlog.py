from .base_object import DiscordObject
from ..client import DiscordClientAsync


class AuditLog(DiscordObject):
    GUILD_UPDATE = 1
    CHANNEL_CREATE = 10
    CHANNEL_UPDATE = 11
    CHANNEL_DELETE = 12
    CHANNEL_OVERWRITE_CREATE = 13
    CHANNEL_OVERWRITE_UPDATE = 14
    CHANNEL_OVERWRITE_DELETE = 15
    MEMBER_KICK = 20
    MEMBER_PRUNE = 21
    MEMBER_BAN_ADD = 22
    MEMBER_BAN_REMOVE = 23
    MEMBER_UPDATE = 24
    MEMBER_ROLE_UPDATE = 25
    ROLE_CREATE = 30
    ROLE_UPDATE = 31
    ROLE_DELETE = 32
    INVITE_CREATE = 40
    INVITE_UPDATE = 41
    INVITE_DELETE = 42
    WEBHOOK_CREATE = 50
    WEBHOOK_UPDATE = 51
    WEBHOOK_DELETE = 52
    EMOJI_CREATE = 60
    EMOJI_UPDATE = 61
    EMOJI_DELETE = 62
    MESSAGE_DELETE = 72

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, user_id: str, target_id: str, action_type: int,
                 reason: str = None):
        super().__init__(client_bind, id)
        self.author_id = user_id
        self.target_id = target_id
        self.action_type_id = action_type
        self.reason = reason

    def is_target(self, user_in_question: DiscordObject) -> bool:
        return user_in_question.snowflake == self.target_id


class AuditKick(AuditLog):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, user_id: str, target_id: str, action_type: int,
                 reason: str = None):
        assert action_type == self.MEMBER_KICK, 'Attempted to create AuditKick from not a kick_async event'
        super().__init__(client_bind, id, user_id, target_id, action_type, reason)


class AuditBanAdd(AuditLog):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, user_id: str, target_id: str, action_type: int,
                 reason: str = None):
        assert action_type == self.MEMBER_BAN_ADD, 'Attempted to create AuditBanAdd from not a ban add event'
        super().__init__(client_bind, id, user_id, target_id, action_type, reason)
