"""
Objects that will not update themselves. Must be updated by calling a method.
"""

from .attachment import Attachment
from .channel_dm import DmChannel
from .channel_dm_group import DmGroupChannel
from .emoji import Emoji
from .guild import Guild, GuildCategory, GuildTextChannel, GuildVoiceChannel
from .guild_emoji import CustomEmoji
from .guild_invite import GuildInvite
from .guild_member import GuildMember
from .guild_role import Role
from .message import Message
from .reaction import Reaction
from .user import User

__all__ = ['Attachment', 'DmChannel', 'DmGroupChannel', 'Emoji', 'Message',
           'Guild', 'GuildCategory', 'GuildTextChannel', 'GuildVoiceChannel',
           'CustomEmoji', 'GuildInvite', 'GuildMember', 'Role', 'Reaction', 'User']
