import re
import typing

from .base_object import DiscordObject
from .channel import Channel
from .channel_text import TextChannel
from .guild_member import GuildMember
from .guild_role import Role
from .user import User
from ..constants import SocketEventNames
from ..client import DiscordClientAsync


class PartialGuild(DiscordObject):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, name: str, icon: str, owner: bool,
                 permissions: int):
        super().__init__(client_bind, id)
        self.guild_name = name
        self.icon_hash = icon
        if not hasattr(self, 'me_is_owner') or owner is not None:
            self.me_is_owner = owner
        if not hasattr(self, 'my_permissions') or permissions is not None:
            self.my_permissions = permissions

    async def leave_async(self) -> None:
        await self.client_bind.me_guild_leave(self.snowflake)

    def json_representation(self) -> dict:
        return {
            'id': self.snowflake,
            'name': self.guild_name,
            'icon': self.icon_hash,
            'owner': self.me_is_owner,
            'permissions': self.my_permissions
        }

    async def extend_to_full_guild_async(self) -> 'Guild':
        full_guild_dict = await self.client_bind.guild_get(self.snowflake)
        if 'owner' not in full_guild_dict:
            full_guild_dict['owner'] = self.me_is_owner
        if 'permissions' not in full_guild_dict:
            full_guild_dict['permissions'] = self.my_permissions
        return Guild(self.client_bind, **full_guild_dict)

    def __repr__(self) -> str:
        return f"Partial Guild: {self.guild_name}"


class Guild(PartialGuild):
    DEFAULT_NOTIFICATION_ALL_MESSAGES = 0
    DEFAULT_NOTIFICATION_ONLY_MENTIONS = 1

    EXPLICIT_CONTENT_FILTER__DISABLED = 0
    EXPLICIT_CONTENT_FILTER__MEMBERS_NO_ROLES = 1
    EXPLICIT_CONTENT_FILTER__ALL_MEMBERS = 2

    # noinspection PyShadowingBuiltins
    def __init__(
            self, client_bind: DiscordClientAsync, id: str, name: str, icon: str, splash: str,
            owner_id: str, region: str, afk_channel_id: str, afk_timeout: int,
            verification_level: int, default_message_notifications: int, explicit_content_filter: int,
            roles: typing.Tuple[dict], emojis: typing.Tuple[dict],
            features: typing.Tuple[str], mfa_level: int, application_id: int, system_channel_id: str,
            embed_enabled: bool = None, embed_channel_id: str = None,
            widget_enabled: bool = None, widget_channel_id: str = None,
            owner: bool = False, permissions: int = None,
            joined_at: str = None, large: bool = None, unavailable: bool = None, member_count: int = None,
            voice_states: dict = None, members: typing.Tuple[dict] = None, channels: typing.Tuple[dict] = None,
            presences: typing.Tuple[dict] = None,
            **kwargs):
        super().__init__(client_bind, id, name, icon, owner, permissions)

        self.splash_hash = splash
        self.owner_id = owner_id
        self.region_name = region
        self.afk_channel_id = afk_channel_id
        self.afk_timeout = afk_timeout
        self.verification_level = verification_level
        self.default_message_notifications_level = default_message_notifications
        self.explicit_content_filter_level = explicit_content_filter
        self.roles_dict_array = {x['id']: x for x in roles}
        self.emojis_dict_array = {x['id']: x for x in emojis}
        self.features_array = features
        self.mfa_level = mfa_level
        self.creator_application_id = application_id
        self.system_channel_id = system_channel_id

        if not hasattr(self, 'embed_enabled') or embed_enabled is not None:
            self.embed_enabled = embed_enabled
            self.embed_channel_id = embed_channel_id
            self.widget_enabled = widget_enabled
            self.widget_channel_id = widget_channel_id

        if not hasattr(self, 'joined_at') or joined_at is not None:
            self.joined_at = joined_at
            self.large_guild = large
            self.unavailable = unavailable
            self.voice_state = voice_states
            self.member_count = member_count
            if members is not None:
                self.members_dicts = {x['user']['id']: x for x in members}
            else:
                self.members_dicts = None
            if channels is not None:
                self.channels_dicts = {x['id']: x for x in channels}
            else:
                self.channels_dicts = None
            self.presences_dicts = presences

        self.kwargs_handler(**kwargs)

    def update_from_dict(self, guild_dict: dict):
        self.__init__(self.client_bind, **guild_dict)

    async def refresh_async(self) -> None:
        self.update_from_dict(await self.client_bind.guild_get(self.snowflake))

    # Roles related calls

    def get_role_by_id(self, role_id: str) -> Role:
        return Role(self.client_bind, **self.roles_dict_array[role_id], parent_guild_id=self.snowflake)

    def find_roles_by_name_regex(self, regex) -> typing.List[Role]:
        matched_roles_list = []
        for k, v in self.roles_dict_array.items():
            if regex.match(v['name']):
                matched_roles_list.append(Role(self.client_bind, **v, parent_guild_id=self.snowflake))
        return matched_roles_list

    def find_roles_by_name(self, regex_string: str) -> typing.List[Role]:
        return self.find_roles_by_name_regex(re.compile(regex_string, re.IGNORECASE))

    def roles_dicts_iter(self) -> typing.Generator[dict, None, None]:
        for k in self.roles_dict_array:
            yield self.roles_dict_array[k]

    def roles_iter(self) -> typing.Generator[Role, None, None]:
        for d in self.roles_dicts_iter():
            yield Role(self.client_bind, **d, parent_guild_id=self.snowflake)

    # Channel related calls

    def get_channel_list(self) -> list:
        return [x for x in self.channels_iter()]

    def text_channels_iter(self) -> typing.Generator['GuildTextChannel', None, None]:
        for channel_d in self.channels_dicts_iter():
            if channel_d['type'] == Channel.CHANNEL_TYPE_GUILD_TEXT:
                yield GuildTextChannel(self.client_bind, **channel_d)

    def channels_iter(self) -> typing.Generator[Channel, None, None]:
        for channel_d in self.channels_dicts_iter():
            yield GuildChannel(self.client_bind, **channel_d)

    def channels_dicts_iter(self) -> typing.Generator[dict, None, None]:
        for channel_k in self.channels_dicts:
            yield self.channels_dicts[channel_k]

    async def refresh_channels_dicts(self) -> typing.Awaitable[None]:
        self.channels_dicts = {x['id']: x async for x in self.client_bind.guild_channel_list(self.snowflake)}
        return typing.cast(typing.Awaitable[None], None)

    # Members related calls

    # TODO: replace with threading
    '''
    async def on_new_member_join(self) -> typing.Generator[GuildMember, None, None]:
        q = self.client_bind.event_queue_add(SocketEventNames.GUILD_MEMBER_ADD)
        with q:
            while True:
                r = await q.get()
                new_member_guild_id = r.pop('guild_id')
                if new_member_guild_id == self.snowflake:
                    yield GuildMember(self.client_bind, **r, parent_guild_id=new_member_guild_id)

    async def on_user_leave(self) -> typing.AsyncGenerator[User, None]:
        q = self.client_bind.event_queue_add(SocketEventNames.GUILD_MEMBER_REMOVE)
        with q:
            while True:
                r = await q.get()
                if r['guild_id'] == self.snowflake:
                    yield User(self.client_bind, **r['user'])
    '''
    async def get_member_from_user(self, user: User) -> typing.Awaitable[GuildMember]:
        return typing.cast(typing.Awaitable[GuildMember],
                           GuildMember(self.client_bind,
                                       **(await self.client_bind.guild_member_get(self.snowflake, user.snowflake)),
                                       guild_id=self.snowflake)
                           )

    def member_dicts_iter(self) -> typing.Generator[dict, None, None]:

        for member_k in self.members_dicts:
            yield self.members_dicts[member_k]

    async def refresh_member_dicts(self) -> None:
        self.members_dicts = {x['user']['id']: x async for x in self.client_bind.guild_member_iter(self.snowflake)}

    def member_iter(self):
        for member_d in self.member_dicts_iter():
            yield GuildMember(self.client_bind, **member_d, guild_id=self.snowflake)

    # __ functions
    def __repr__(self) -> str:
        return f"Guild: {self.guild_name}"


class GuildChannel(Channel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, guild_id: str, name: str, type: int, position: int,
                 permission_overwrites: typing.List[dict], parent_id: str, nsfw: bool,
                 last_message_id: str = None, last_pin_timestamp: str = None):
        if self.__class__.__mro__[0] is not GuildTextChannel:
            super().__init__(client_bind, id, type)
        else:  # HACK: multiple inheritance for GuildTextChannel class workaround
            # noinspection PyArgumentList
            super().__init__(client_bind, id, type, last_message_id, last_pin_timestamp)
        self.guild_id = guild_id
        self.channel_name = name
        self.position = position
        self.permission_overwrites_dicts = permission_overwrites
        self.parent_channel_id = parent_id
        self.nsfw = nsfw

    def get_guild(self) -> Guild:
        return Guild(self.client_bind, **self.client_bind.guild_get(self.guild_id))

    async def modify_nsfw(self, nsfw: bool) -> 'GuildChannel':
        return self.__class__(
            self.client_bind, **(await self.client_bind.channel_modify(self.snowflake, new_nsfw=nsfw))
        )


class GuildCategory(GuildChannel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, guild_id: str, name: str, type: int, position: int,
                 permission_overwrites: typing.List[dict], parent_id: str, nsfw: bool,
                 **kwargs):
        super().__init__(client_bind, id, guild_id, name, type, position, permission_overwrites, parent_id, nsfw)

        self.kwargs_handler(**kwargs)


class GuildTextChannel(GuildChannel, TextChannel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, guild_id: str, name: str, type: int, position: int,
                 permission_overwrites: typing.List[dict], nsfw: bool, topic: str, last_message_id: str,
                 parent_id: str, last_pin_timestamp: str = None,
                 **kwargs):
        super().__init__(client_bind, id, guild_id, name, type, position, permission_overwrites, parent_id, nsfw,
                         last_message_id, last_pin_timestamp)
        self.topic = topic

        self.kwargs_handler(**kwargs)


class GuildVoiceChannel(GuildChannel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClientAsync, id: str, guild_id: str, name: str, type: int, position: int,
                 permission_overwrites: typing.List[dict], parent_id: str, bitrate: int, user_limit: int,
                 nsfw: bool, **kwargs):
        super().__init__(client_bind, id, guild_id, name, type, position, permission_overwrites, parent_id, nsfw)
        self.bitrate = bitrate
        self.user_limit = user_limit

        self.kwargs_handler(**kwargs)
