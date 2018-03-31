from enum import Enum


class SocketEventNames(Enum):
    READY = 'READY'

    # Channels
    CHANNEL_CREATE = 'CHANNEL_CREATE'
    CHANNEL_UPDATE = 'CHANNEL_UPDATE'
    CHANNEL_DELETE = 'CHANNEL_DELETE'
    CHANNEL_PINS_UPDATE = 'CHANNEL_PINS_UPDATE'
    # Guild
    GUILD_CREATE = 'GUILD_CREATE'
    GUILD_UPDATE = 'GUILD_UPDATE'
    GUILD_DELETE = 'GUILD_DELETE'
    GUILD_BAN_ADD = 'GUILD_BAN_ADD'
    GUILD_BAN_REMOVE = 'GUILD_BAN_REMOVE'
    GUILD_EMOJIS_UPDATE = 'GUILD_EMOJIS_UPDATE'
    GUILD_INTEGRATIONS_UPDATE = 'GUILD_INTEGRATIONS_UPDATE'
    GUILD_MEMBER_ADD = 'GUILD_MEMBER_ADD'
    GUILD_MEMBER_REMOVE = 'GUILD_MEMBER_REMOVE'
    GUILD_MEMBER_UPDATE = 'GUILD_MEMBER_UPDATE'
    GUILD_ROLE_CREATE = 'GUILD_ROLE_CREATE'
    GUILD_ROLE_UPDATE = 'GUILD_ROLE_UPDATE'
    GUILD_ROLE_DELETE = 'GUILD_ROLE_DELETE'
    # Messages
    MESSAGE_CREATE = 'MESSAGE_CREATE'
    MESSAGE_UPDATE = 'MESSAGE_UPDATE'
    MESSAGE_DELETE = 'MESSAGE_DELETE'
    MESSAGE_DELETE_BULK = 'MESSAGE_DELETE_BULK'
    MESSAGE_REACTION_ADD = 'MESSAGE_REACTION_ADD'
    MESSAGE_REACTION_REMOVE = 'MESSAGE_REACTION_REMOVE'
    MESSAGE_REACTION_REMOVE_ALL = 'MESSAGE_REACTION_REMOVE_ALL'
    # Presence
    PRESENCE_UPDATE = 'PRESENCE_UPDATE'
    TYPING_START = 'TYPING_START'
    USER_UPDATE = 'USER_UPDATE'
    # Voice
    VOICE_STATE_UPDATE = 'VOICE_STATE_UPDATE'
    VOICE_SERVER_UPDATE = 'VOICE_SERVER_UPDATE'
    # Webhooks
    WEBHOOKS_UPDATE = 'WEBHOOKS_UPDATE'
