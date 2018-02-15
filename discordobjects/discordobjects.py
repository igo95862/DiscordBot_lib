from .discordclient import DiscordClient
import typing
import re
from . import socket_events_names

__all__ = ['User', 'MyUser', 'DmChannel', 'DmGroupChannel', 'Message', 'Reaction', 'PartialGuild',
           'Guild', 'GuildTextChannel', 'GuildVoiceChannel', 'GuildCategory',
           'GuildMember', 'Role']


class DiscordObject:
    """
    Basic class for all other discord objects
    """
    def __init__(self, client_bind: DiscordClient = None, snowflake: str = None):
        self.client_bind = client_bind
        self.snowflake = snowflake

    def __eq__(self, other: 'DiscordObject') -> bool:
        return self.snowflake == other.snowflake


class User(DiscordObject):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, username: str, discriminator: str, avatar: str,
                 bot: bool = None, mfa_enabled: bool = None, verified: bool = None, email: str = None):
        super().__init__(client_bind, id)
        self.username = username
        self.discriminator = discriminator
        self.avatar_hash = avatar
        self.is_bot = bot
        self.mfa_enabled = mfa_enabled
        self.verified = verified
        self.email = email

    def get_avatar_url(self) -> str:
        return f"https://cdn.discordapp.com/avatars/{self.snowflake}/{self.avatar_hash}.png"

    def get_name_formatted(self) -> str:
        return f"{self.username}#{self.discriminator}"

    def __str__(self) -> str:
        return f"<@{self.snowflake}>"

    def __repr__(self) -> str:
        return f"User: {self.username}#{self.discriminator}"


class Channel(DiscordObject):

    CHANNEL_TYPE_GUILD_TEXT = 0
    CHANNEL_TYPE_DM = 1
    CHANNEL_TYPE_GUILD_VOICE = 2
    CHANNEL_TYPE_GROUP_DM = 3
    CHANNEL_TYPE_GUILD_CATEGORY = 4

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, type: int):
        super().__init__(client_bind, id)
        self.channel_type = type


class TextChannel(Channel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, type: int, last_message_id: str,
                 last_pin_timestamp: str = None):
        super().__init__(client_bind, id, type)
        self.last_message_id = last_message_id
        self.last_pin_timestamp = last_pin_timestamp

    def post_message(self, content: str, force: bool = False) -> 'Message':
        if not force:
            if len(content) > 2000:
                raise TypeError('Message length can\'t be more then 2000 symbols')

        new_message_dict = self.client_bind.channel_message_create(self.snowflake, content)
        return Message(self.client_bind, **new_message_dict)

    def post_file(self, file_name: str, file_bytes: bytes):
        return Message(self.client_bind, **self.client_bind.channel_message_create_file(self.snowflake,
                                                                                        file_name, file_bytes))

    def message_iter(self) -> typing.Generator['Message', None, None]:
        for message_d in self.message_dict_iter():
            yield Message(self.client_bind, **message_d)

    def message_dict_iter(self) -> typing.Generator[dict, None, None]:
        last_message_id = None
        message_list = self.client_bind.channel_message_list(self.snowflake, limit=100, before=last_message_id)
        reached_end = False
        while reached_end is False:
            if len(message_list) == 0:
                reached_end = True
                continue

            for m in message_list:
                yield m
            last_message_id = message_list[-1]['id']

            message_list = self.client_bind.channel_message_list(self.snowflake, limit=100, before=last_message_id)

    def get_last_message(self) -> 'Message':
        return Message(self.client_bind, **self.client_bind.channel_message_get(self.snowflake, self.last_message_id))

    def on_message_created(self) -> None:
        pass


class DmChannel(TextChannel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, type: int, last_message_id: str,
                 recipients: typing.List[dict], last_pin_timestamp: str = None):
        super().__init__(client_bind, id, type, last_message_id, last_pin_timestamp)
        self.recipients_dicts = recipients


class DmGroupChannel(DmChannel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, type: int, last_message_id: str,
                 recipients: typing.List[dict], icon: str, owner_id: str, last_pin_timestamp: str = None):
        super().__init__(client_bind, id, type, last_message_id, recipients, last_pin_timestamp)
        self.icon_hash = icon
        self.owner_id = owner_id


class Message(DiscordObject):

    MESSAGE_TYPE_DEFAULT = 0
    MESSAGE_TYPE_RECIPIENT_ADD = 1
    MESSAGE_TYPE_RECIPIENT_REMOVE = 2
    MESSAGE_TYPE_CALL = 3
    MESSAGE_TYPE_CHANNEL_NAME_CHANGE = 4
    MESSAGE_TYPE_CHANNEL_ICON_CHANGE = 5
    MESSAGE_TYPE_CHANNEL_PINNED_MESSAGE = 6
    MESSAGE_TYPE_GUILD_MEMBER_JOIN = 7

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, channel_id: str, author: dict, content: str, timestamp: str,
                 edited_timestamp: str, tts: bool, mention_everyone: bool, mentions: typing.List[dict], type: int,
                 mention_roles: typing.List[dict], attachments: typing.List[dict], embeds: typing.List[dict],
                 pinned: bool, reactions: typing.List[dict] = None, nonce: bool = None, webhook_id: str = None,
                 ):
        super().__init__(client_bind, id)
        self.parent_channel_id = channel_id
        self.author_dict = author
        self.content = content
        self.timestamp = timestamp
        self.edited_timestamp = edited_timestamp
        self.tts = tts
        self.mention_everyone = mention_everyone
        self.mentions_dicts = {x['id']: x for x in mentions}
        self.type = type
        self.mention_roles_dicts = mention_roles
        self.attachments_dicts = attachments
        self.embeds = embeds
        self.pinned = pinned
        self.reactions = reactions
        self.nonce = nonce
        self.webhook_id = webhook_id

    def update_from_dict(self, message_dict: dict) -> None:
        self.__init__(self.client_bind, **message_dict)

    def refresh(self) -> None:
        self.update_from_dict(self.client_bind.channel_message_get(self.parent_channel_id, self.snowflake))

    def edit(self, new_content: str) -> None:
        self.update_from_dict(self.client_bind.channel_message_edit(self.parent_channel_id, self.snowflake,
                                                                    new_content))

    def remove(self) -> None:
        self.client_bind.channel_message_delete(self.parent_channel_id, self.snowflake)

    def add_unicode_emoji(self, unicode_emoji: str):
        self.client_bind.channel_message_reaction_create(self.parent_channel_id, self.snowflake, unicode_emoji)

    def clear_all_emoji(self) -> None:
        self.client_bind.channel_message_reaction_delete_all(self.parent_channel_id, self.snowflake)

    def gen_reacted_users_by_unicode_emoji(self, unicode_emoji: str) -> typing.Generator['User', None, None]:
        for d in self.client_bind.channel_message_reaction_iter_users(
                self.parent_channel_id, self.snowflake, unicode_emoji,
                ):
            yield User(self.client_bind, **d)

    def get_reactions(self) -> typing.List['Reaction']:
        self.refresh()
        if self.reactions is not None:
            return [Reaction(self.client_bind, **x, parent_message=self) for x in self.reactions]
        else:
            return []

    def get_content(self) -> str:
        return self.content

    def get_author(self) -> User:
        return User(self.client_bind, **self.author_dict)

    def is_author(self, user: User) -> bool:
        return user.snowflake == self.author_dict['id']

    def get_mentioned_users(self) -> typing.List['User']:
        return [User(self.client_bind, **self.mentions_dicts[x]) for x in self.mentions_dicts]

    def attachments_iter(self) -> typing.Generator['Attachment', None, None]:
        for d in self.attachments_dicts:
            yield Attachment(self.client_bind, **d)

    def on_emoji_created(self) -> None:
        pass


class PartialEmoji:

    # noinspection PyShadowingBuiltins
    def __init__(self, id: str, name: str):
        self.emoji_id = id
        self.name = name

    def is_unicode_emoji(self) -> bool:
        return self.emoji_id is None


class Reaction:

    def __init__(self, client_bind: DiscordClient, count: int, me: bool, emoji: dict, parent_message: Message):
        self.client_bind = client_bind
        self.count = count
        self.me_reacted = me
        self.partial_emoji_dict = emoji
        self.parent_message = parent_message

    def user_reacted_gen(self) -> typing.Generator['User', None, None]:
        for d in self.client_bind.channel_message_reaction_iter_users(
                self.parent_message.parent_channel_id, self.parent_message.snowflake,
                self.partial_emoji_dict['id'] or self.partial_emoji_dict['name']):
            yield User(self.client_bind, **d)


class Attachment(DiscordObject):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, filename: str, size: int, url: str, proxy_url: str,
                 height: int = None, width: int = None):
        super().__init__(client_bind, id)
        self.filename = filename
        self.file_size_bytes = size
        self.url = url
        self.proxy_url = proxy_url
        self.height = height
        self.width = width

    def is_image(self) -> bool:
        return self.height is not None


class MyUser(User):

    def __init__(self, token: str, use_socket: bool = True, proxies: dict = None):
        new_client = DiscordClient(token, use_socket, proxies)
        my_user_dict = new_client.me_get()
        super().__init__(new_client, **my_user_dict)

    def create_dm(self, recipient_id: str) -> DmChannel:
        return DmChannel(self.client_bind, **self.client_bind.dm_create(recipient_id))

    def get_my_partial_guilds(self) -> list:
        # NOTE: only supports less then 100 guilds at the moment
        json_guild_list = self.client_bind.me_guild_list()
        return [PartialGuild(self.client_bind, **g) for g in json_guild_list]

    def get_guild_by_id(self, guild_id: str) -> 'Guild':
        return Guild(self.client_bind, **self.client_bind.guild_get(guild_id))

    def get_channel_by_id(self, channel_id: str) -> 'GuildTextChannel':
        channel_dict = self.client_bind.channel_get(channel_id)
        if channel_dict['type'] == Channel.CHANNEL_TYPE_GUILD_TEXT:
            return GuildTextChannel(self.client_bind, **channel_dict)


class PartialGuild(DiscordObject):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, name: str, icon: str, owner: bool,
                 permissions: int):
        super().__init__(client_bind, id)
        self.guild_name = name
        self.icon_hash = icon
        if not hasattr(self, 'me_is_owner') or owner is not None:
            self.me_is_owner = owner
        if not hasattr(self, 'my_permissions') or permissions is not None:
            self.my_permissions = permissions

    def leave(self) -> None:
        self.client_bind.me_guild_leave(self.snowflake)

    def json_representation(self) -> dict:
        return {
            'id': self.snowflake,
            'name': self.guild_name,
            'icon': self.icon_hash,
            'owner': self.me_is_owner,
            'permissions': self.my_permissions
        }

    def extend_to_full_guild(self) -> 'Guild':
        full_guild_dict = self.client_bind.guild_get(self.snowflake)
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
            self, client_bind: DiscordClient, id: str, name: str, icon: str, splash: str,
            owner_id: str, region: str, afk_channel_id: str, afk_timeout: int,
            verification_level: int, default_message_notifications: int, explicit_content_filter: int,
            roles: typing.Tuple[dict], emojis: typing.Tuple[dict],
            features: typing.Tuple[str], mfa_level: int, application_id: int, system_channel_id: str,
            embed_enabled: bool = None, embed_channel_id: str = None,
            widget_enabled: bool = None, widget_channel_id: str = None,
            owner: bool = False, permissions: int = None,
            joined_at: str = None, large: bool = None, unavailable: bool = None, member_count: int = None,
            voice_states: dict = None, members: typing.Tuple[dict] = None, channels: typing.Tuple[dict] = None,
            presences: typing.Tuple[dict] = None):
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

    def update_from_dict(self, guild_dict: dict):
        self.__init__(self.client_bind, **guild_dict)

    def refresh(self) -> None:
        self.update_from_dict(self.client_bind.guild_get(self.snowflake))

    # Roles related calls

    def get_role_by_id(self, role_id: str) -> 'Role':
        return Role(self.client_bind, **self.roles_dict_array[role_id], parent_guild_id=self.snowflake)

    def find_roles_by_name_regex(self, regex) -> typing.List['Role']:
        matched_roles_list = []
        for k, v in self.roles_dict_array.items():
            if regex.match(v['name']):
                matched_roles_list.append(Role(self.client_bind, **v, parent_guild_id=self.snowflake))
        return matched_roles_list

    def find_roles_by_name(self, regex_string: str) -> typing.List['Role']:
        return self.find_roles_by_name_regex(re.compile(regex_string, re.IGNORECASE))

    def roles_dicts_iter(self) -> typing.Generator[dict, None, None]:
        for k in self.roles_dict_array:
            yield self.roles_dict_array[k]

    def roles_iter(self) -> typing.Generator['Role', None, None]:
        for d in self.roles_dicts_iter():
            yield Role(self.client_bind, **d, parent_guild_id=self.snowflake)

    # Channel related calls

    def get_channel_list(self) -> list:
        return [x for x in self.channels_iter()]

    def text_channels_iter(self, download_new: bool = True) -> typing.Generator:
        for channel_d in self.channels_dicts_iter(download_new):
            if channel_d['type'] == Channel.CHANNEL_TYPE_GUILD_TEXT:
                yield GuildTextChannel(self.client_bind, **channel_d)

    def channels_iter(self, download_new: bool = True) -> typing.Generator['Channel', None, None]:
        for channel_d in self.channels_dicts_iter(download_new):
            yield GuildChannel(self.client_bind, **channel_d)

    def channels_dicts_iter(self, download_new: bool = True) -> typing.Generator[dict, None, None]:
        if download_new:
            self.refresh_channels_dicts()

        for channel_k in self.channels_dicts:
            yield self.channels_dicts[channel_k]

    def refresh_channels_dicts(self) -> None:
        self.channels_dicts = {x['id']: x for x in self.client_bind.guild_channel_list(self.snowflake)}

    # Members related calls

    async def on_new_member_join(self) -> typing.Generator['GuildMember', None, None]:
        q = self.client_bind.event_queue_add(socket_events_names.GUILD_MEMBER_ADD)
        with q:
            while True:
                r = await q.get()
                new_member_guild_id = r.pop('guild_id')
                if new_member_guild_id == self.snowflake:
                    yield GuildMember(self.client_bind, **r, parent_guild_id=new_member_guild_id)

    async def on_user_leave(self) -> typing.Generator['User', None, None]:
        q = self.client_bind.event_queue_add(socket_events_names.GUILD_MEMBER_REMOVE)
        with q:
            while True:
                r = await q.get()
                if r['guild_id'] == self.snowflake:
                    yield User(self.client_bind, **r['user'])

    def get_member_from_user(self, user: User) -> 'GuildMember':
        return GuildMember(self.client_bind, **self.client_bind.guild_member_get(self.snowflake, user.snowflake),
                           parent_guild_id=self.snowflake)

    def member_dicts_iter(self, download_new: bool = True) -> typing.Generator[dict, None, None]:
        if download_new:
            self.refresh_member_dicts()

        for member_k in self.members_dicts:
            yield self.members_dicts[member_k]

    def refresh_member_dicts(self) -> None:
        downloaded_member_dicts = self.client_bind.guild_members_list(self.snowflake, limit=1000)
        member_dicts = []
        member_dicts[:] = downloaded_member_dicts
        while len(downloaded_member_dicts) == 1000:
            downloaded_member_dicts = self.client_bind.guild_members_list(
                self.snowflake, limit=1000,
                after=downloaded_member_dicts[-1]['user']['id'])
            member_dicts += downloaded_member_dicts
        self.members_dicts = {x['user']['id']: x for x in member_dicts}

    def member_iter(self, download_new: bool = True):
        for member_d in self.member_dicts_iter(download_new):
            yield GuildMember(self.client_bind, **member_d, parent_guild_id=self.snowflake)

    # __ functions
    def __repr__(self) -> str:
        return f"Guild: {self.guild_name}"


class CustomEmoji(DiscordObject):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, name: str, roles: typing.List[int], user: dict,
                 require_colons: bool, managed: bool, animated: bool):
        super().__init__(client_bind, id)
        self.emoji_name = name
        self.roles_allowed = roles
        self.user_creator_dict = user
        self.require_colons = require_colons
        self.managed = managed
        self.animated = animated

    def get_url(self) -> str:
        return f"https://cdn.discordapp.com/emojis/{self.snowflake}.png"


class Role(DiscordObject):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, name: str, color: int, hoist: bool, position: int,
                 permissions: int, managed: bool, mentionable: bool,
                 parent_guild_id: str = None):
        super().__init__(client_bind, id)
        self.role_name = name
        self.role_color = color
        self.display_separately = hoist
        self.position = position
        self.permissions = permissions
        self.managed = managed
        self.mentionable = mentionable
        self.parent_guild_id = parent_guild_id

    def has_name(self, other_name: str) -> bool:
        return self.role_name == other_name

    def __repr__(self) -> str:
        return f"Role: {self.role_name}"


class GuildMember(User):

    def __init__(self, client_bind: DiscordClient, user: dict, roles: typing.Tuple[str],
                 joined_at: int, deaf: bool, mute: bool, nick: str = None,
                 parent_guild_id: str = None):
        super().__init__(client_bind, **user)

        self.nickname = nick
        self.roles_ids = roles
        self.joined_at = joined_at
        self.is_deaf = deaf
        self.is_mute = mute
        if not hasattr(self, 'parent_guild_id') or parent_guild_id is not None:
            self.parent_guild_id = parent_guild_id

    def kick(self) -> None:
        self.client_bind.guild_member_remove(self.parent_guild_id, self.snowflake)

    def add_role(self, role: Role):
        self.client_bind.guild_member_role_add(self.parent_guild_id, self.snowflake, role.snowflake)

    def remove_role(self, role: Role):
        self.client_bind.guild_member_role_remove(self.parent_guild_id, self.snowflake, role.snowflake)

    def set_roles(self, roles: typing.List[Role]):
        self.client_bind.guild_member_modify_roles(self.parent_guild_id, self.snowflake, [x.snowflake for x in roles])

    def set_roles_by_ids(self, roles_ids: typing.List[str]):
        self.client_bind.guild_member_modify_roles(self.parent_guild_id, self.snowflake, roles_ids)

    def roles_ids_iter(self) -> typing.Generator[str, None, None]:
        for i in self.roles_ids:
            yield i

    def update_from_dict(self, member_dict: dict):
        self.__init__(self.client_bind, **member_dict)

    def refresh(self) -> None:
        self.update_from_dict(**self.client_bind.guild_member_get(self.parent_guild_id, self.snowflake))

    @typing.overload
    def __contains__(self, item: Role) -> bool:
        ...

    @typing.overload
    def __contains__(self, item: int) -> bool:
        ...

    def __contains__(self, item) -> bool:
        if isinstance(item, Role):
            return item.snowflake in self.roles_ids
        elif isinstance(item, int):
            return item in self.roles_ids
        else:
            raise NotImplementedError


class GuildChannel(Channel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, guild_id: str, name: str, type: int, position: int,
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


class GuildTextChannel(GuildChannel, TextChannel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, guild_id: str, name: str, type: int, position: int,
                 permission_overwrites: typing.List[dict], nsfw: bool, topic: str, last_message_id: str,
                 parent_id: str, last_pin_timestamp: str = None):
        super().__init__(client_bind, id, guild_id, name, type, position, permission_overwrites, parent_id, nsfw,
                         last_message_id, last_pin_timestamp)
        self.topic = topic


class GuildVoiceChannel(GuildChannel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, guild_id: str, name: str, type: int, position: int,
                 permission_overwrites: typing.List[dict], parent_id: str, bitrate: int, user_limit: int,
                 nsfw: bool):
        super().__init__(client_bind, id, guild_id, name, type, position, permission_overwrites, parent_id, nsfw)
        self.bitrate = bitrate
        self.user_limit = user_limit


class GuildCategory(GuildChannel):

    # noinspection PyShadowingBuiltins
    def __init__(self, client_bind: DiscordClient, id: str, guild_id: str, name: str, type: int, position: int,
                 permission_overwrites: typing.List[dict], parent_id: str, nsfw: bool):
        super().__init__(client_bind, id, guild_id, name, type, position, permission_overwrites, parent_id, nsfw)



