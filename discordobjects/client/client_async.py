import asyncio
import typing
from _functools import partial as f_partial

from .rate_limit_simple import RateLimitSimple
from ..discordrest import DiscordSession
from ..discordsocket_thread import SocketThread


class DiscordClientAsync:

    def __init__(self, token: str, use_socket: bool = True, proxies: dict = None,
                 event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
        self.rest_session = DiscordSession(token, proxies)
        self.event_loop = event_loop
        # TODO: custom rate limiters
        self.rate_limit = RateLimitSimple(self.event_loop)
        self.socket_thread = None
        # TODO: sharding
        self.socket_thread = SocketThread(token, start_immediately=use_socket)

        self.event_ready = self.socket_thread.event_ready
        self.event_resumed = self.socket_thread.event_resumed
        self.event_channel_create = self.socket_thread.event_channel_create
        self.event_channel_update = self.socket_thread.event_channel_update
        self.event_channel_delete = self.socket_thread.event_channel_delete
        self.event_channel_pins_update = self.socket_thread.event_channel_pins_update
        self.event_guild_create = self.socket_thread.event_guild_create
        self.event_guild_update = self.socket_thread.event_guild_update
        self.event_guild_delete = self.socket_thread.event_guild_delete
        self.event_guild_ban_add = self.socket_thread.event_guild_ban_add
        self.event_guild_ban_remove = self.socket_thread.event_guild_ban_remove
        self.event_guild_emoji_update = self.socket_thread.event_guild_emoji_update
        self.event_guild_integrations_update = self.socket_thread.event_guild_integrations_update
        self.event_guild_member_add = self.socket_thread.event_guild_member_add
        self.event_guild_member_update = self.socket_thread.event_guild_member_update
        self.event_guild_member_remove = self.socket_thread.event_guild_member_remove
        self.event_guild_role_create = self.socket_thread.event_guild_role_create
        self.event_guild_role_update = self.socket_thread.event_guild_role_update
        self.event_guild_role_delete = self.socket_thread.event_guild_role_delete
        self.event_message_create = self.socket_thread.event_message_create
        self.event_message_update = self.socket_thread.event_message_update
        self.event_message_delete = self.socket_thread.event_message_delete
        self.event_message_delete_bulk = self.socket_thread.event_message_delete_bulk
        self.event_message_reaction_add = self.socket_thread.event_message_reaction_add
        self.event_message_reaction_remove = self.socket_thread.event_message_reaction_remove
        self.event_message_reaction_remove_all = self.socket_thread.event_message_reaction_remove_all
        self.event_presence_update = self.socket_thread.event_presence_update
        self.event_typing_start = self.socket_thread.event_typing_start
        self.event_user_update = self.socket_thread.event_user_update
        self.event_voice_state_update = self.socket_thread.event_voice_state_update
        self.event_voice_server_update = self.socket_thread.event_voice_server_update
        self.event_webhooks_update = self.socket_thread.event_webhooks_update

    def start_socket(self):
        self.socket_thread.start()

    async def user_get(self, user_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.user_get, user_id))

    # region Current User functions
    async def me_get(self) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.me_get))

    async def me_modify(self, username: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.me_modify, username))

    async def me_guild_list(self, before: str = None, after: str = None, limit: int = None) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.me_guild_list, before, after, limit))

    async def me_guild_leave(self, guild_id: str) -> bool:
        return await self.rate_limit(f_partial(self.rest_session.me_guild_leave, guild_id))

    async def me_connections_get(self) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.me_connections_get))

    async def me_dm_list(self) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.me_dm_list))

    # endregion

    # region Direct Messaging (DM) functions
    async def dm_create(self, recipient_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.dm_create, recipient_id))

    async def dm_create_group(self, access_tokens: list, nicks: dict) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.dm_create_group, access_tokens, nicks))

    async def dm_channel_user_add(self, channel_id: str, user_id: str, access_token: str, user_nick: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.dm_user_add,
                                               channel_id, user_id, access_token, user_nick))

    async def dm_channel_user_remove(self, channel_id: str, user_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.dm_user_remove, channel_id, user_id))

    # endregion

    # region Guild
    async def guild_create(self, guild_name: str, region: str = None, icon: str = None, verification_level: int = None,
                           default_message_notifications: int = None, roles=None, channels=None) -> dict:
        return await self.rate_limit(f_partial(
            self.rest_session.guild_create,
            guild_name, region, icon, verification_level, default_message_notifications, roles, channels))

    async def guild_get(self, guild_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_get, guild_id))

    async def guild_modify(
            self, guild_id: str, new_name: str = None, new_voice_region_id: str = None,
            new_verification_level: int = None, new_default_level_notifications: int = None,
            new_explicit_content_filter: int = None, new_afk_channel_id: str = None,
            new_afk_timeout: int = None, new_icon: str = None, new_owner: str = None,
            new_splash: str = None, new_system_channel_id: str = None) -> dict:
        return await self.rate_limit(f_partial(
            self.rest_session.guild_modify,
            guild_id, new_name, new_voice_region_id,
            new_verification_level, new_default_level_notifications,
            new_explicit_content_filter, new_afk_channel_id,
            new_afk_timeout, new_icon, new_owner,
            new_splash, new_system_channel_id
        ))

    async def guild_delete(self, guild_id: str) -> bool:
        return await self.rate_limit(f_partial(self.rest_session.guild_delete, guild_id))

    # region Guild Channels
    async def guild_channel_list(self, guild_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_channel_list, guild_id))

    async def guild_channel_create_text(
            self, guild_id: str, name: str, permission_overwrites: typing.List[dict] = None,
            parent_id: str = None, nsfw: bool = None) -> dict:
        return await self.rate_limit(f_partial(
            self.rest_session.guild_channel_create_text,
            guild_id, name, permission_overwrites, parent_id, nsfw))

    async def guild_channel_create_voice(
            self, guild_id: str, name: str, permission_overwrites: typing.List[dict] = None,
            parent_id: str = None, nsfw: bool = None, bitrate: int = None, user_limit: int = None) -> dict:
        return await self.rate_limit(f_partial(
            self.rest_session.guild_channel_create_voice,
            guild_id, name, permission_overwrites, parent_id, nsfw, bitrate, user_limit))

    async def guild_channel_create_category(
            self, guild_id: str, name: str, permission_overwrites: typing.List[dict] = None,
            nsfw: bool = None) -> dict:
        return await self.rate_limit(f_partial(
            self.rest_session.guild_channel_create_category,
            guild_id, name, permission_overwrites, nsfw))

    async def guild_channels_position_modify(
            self, guild_id: str,
            list_of_channels: typing.List[typing.Dict[str, int]]) -> bool:
        return await self.rate_limit(f_partial(
            self.rest_session.guild_channels_position_modify,
            guild_id, list_of_channels))

    # endregion

    # region Guild Members
    async def guild_member_get(self, guild_id: str, user_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_member_get, guild_id, user_id))

    async def guild_members_list(self, guild_id: str, limit: int = None, after: str = None) -> typing.List[dict]:
        return await self.rate_limit(f_partial(
            self.rest_session.guild_member_list,
            guild_id, limit, after))

    async def guild_member_iter(self, guild_id: str, step_size: int = 1000) -> typing.AsyncGenerator[dict, None]:
        downloaded_member_dicts: typing.List[dict] = await self.guild_members_list(guild_id, limit=step_size)

        while len(downloaded_member_dicts) != 0:
            for d in downloaded_member_dicts:
                yield d
            last_member_id = downloaded_member_dicts[-1]['user']['id']
            downloaded_member_dicts[:] = await self.guild_members_list(guild_id, limit=step_size, after=last_member_id)

    async def guild_member_add(self, guild_id: str, user_id: str, access_token: str, nick: str = None,
                               roles: list = None, mute: bool = None, deaf: bool = None) -> dict:
        return await self.rate_limit(f_partial(
            self.rest_session.guild_member_add,
            guild_id, user_id, access_token, nick, roles, mute, deaf))

    async def guild_member_modify(
            self, guild_id: str, user_id: str, new_nick: str = None, new_roles: list = None,
            new_mute: bool = None, new_deaf: bool = None, new_channel_id: str = None) -> dict:
        return await self.rate_limit(
            f_partial(
                self.rest_session.guild_member_modify,
                guild_id, user_id, new_nick, new_roles,
                new_mute, new_deaf, new_channel_id,
            ))

    async def guild_member_me_nick_set(self, guild_id: str, nick_to_set: str) -> dict:
        return await self.rate_limit(
            f_partial(
                self.rest_session.guild_member_me_nick_set,
                guild_id, nick_to_set))

    async def guild_member_role_add(self, guild_id: str, user_id: str, role_id: str) -> bool:
        return await self.rate_limit(
            f_partial(
                self.rest_session.guild_member_role_add,
                guild_id, user_id, role_id),
            ("Guild member role manipulation: ", guild_id))

    async def guild_member_role_remove(self, guild_id: str, user_id: str, role_id: str) -> bool:
        return await self.rate_limit(
            f_partial(
                self.rest_session.guild_member_role_remove,
                guild_id, user_id, role_id),
            ("Guild member role manipulation: ", guild_id))

    async def guild_member_remove(self, guild_id: str, user_id: str) -> bool:
        return await self.rate_limit(
            f_partial(
                self.rest_session.guild_member_remove,
                guild_id, user_id))

    # endregion

    async def guild_ban_list(self, guild_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_ban_list, guild_id))

    async def guild_ban_create(self, guild_id: str, user_id: str, delete_messages_days=None) -> bool:
        return await self.rate_limit(
            f_partial(
                self.rest_session.guild_ban_create,
                guild_id, user_id, delete_messages_days))

    async def guild_ban_remove(self, guild_id: str, user_id: str) -> bool:
        return await self.rate_limit(f_partial(self.rest_session.guild_ban_remove, guild_id, user_id))

    # region Guild Roles
    async def guild_role_list(self, guild_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_role_list, guild_id))

    async def guild_role_create(self, guild_id: str, name: str = None, permissions: int = None,
                                color: int = None, hoist: bool = None,
                                mentionable: bool = None) -> dict:
        return await self.rate_limit(
            f_partial(
                self.rest_session.guild_role_create,
                guild_id, name, permissions, color, hoist, mentionable))

    async def guild_role_position_modify(self, guild_id: str,
                                         list_of_role_positions: typing.List[typing.Dict[str, int]]) -> dict:
        return await self.rate_limit(
            f_partial(
                self.rest_session.guild_role_position_modify,
                guild_id, list_of_role_positions))

    async def guild_role_modify(
            self,
            guild_id: str, role_id: str, new_name: str = None, new_permissions: int = None, new_color: int = None,
            new_hoist: bool = None, new_mentionable: bool = None) -> dict:
        return await self.rate_limit(f_partial(
            self.rest_session.guild_role_modify,
            guild_id, role_id, new_name, new_permissions, new_color,
            new_hoist, new_mentionable))

    async def guild_role_delete(self, guild_id: str, role_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_role_delete, guild_id, role_id))

    # endregion

    async def guild_prune_get_count(self, guild_id: str, days: int) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_prune_get_count, guild_id, days))

    async def guild_prune_begin(self, guild_id: str, days: int) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_prune_begin, guild_id, days))

    async def guild_voice_region_list(self, guild_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_voice_region_list, guild_id))

    async def guild_invite_list(self, guild_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_invite_list, guild_id))

    async def guild_integration_list(self, guild_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_integration_list, guild_id))

    async def guild_integration_create(self, guild_id: str, integration_type: str, integration_id: str) -> dict:
        return await self.rate_limit(
            f_partial(
                self.rest_session.guild_integration_create,
                guild_id, integration_type, integration_id))

    async def guild_integration_modify(self, guild_id: str, integration_id: str,
                                       expire_behavior: int, expire_grace_period: int, enable_emoticons: int) -> dict:
        return await self.rate_limit(
            f_partial(
                self.rest_session.guild_integration_modify,
                guild_id, integration_id, expire_behavior, expire_grace_period, enable_emoticons))

    async def guild_integration_delete(self, guild_id: str, integration_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_integration_delete, guild_id, integration_id))

    async def guild_integration_sync(self, guild_id: str, integration_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_integration_sync, guild_id, integration_id))

    async def guild_embed_get(self, guild_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_embed_get, guild_id))

    async def guild_embed_modify(self, guild_id: str, enabled: bool = None, channel_id: str = None) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_embed_modify, guild_id, enabled, channel_id))

    # region Guild Emoji
    async def guild_emoji_list(self, guild_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_emoji_list, guild_id))

    async def guild_emoji_get(self, guild_id: str, emoji_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_emoji_get, guild_id, emoji_id))

    async def guild_emoji_create(self, guild_id: str, emoji_name: str, image: str, roles: tuple = ()) -> dict:
        return await self.rate_limit(
            f_partial(
                self.rest_session.guild_emoji_create,
                guild_id, emoji_name, image, roles))

    async def guild_emoji_modify(self, guild_id: str, emoji_id: str, emoji_name: str, roles: tuple = ()) -> dict:
        return await self.rate_limit(
            f_partial(
                self.rest_session.guild_emoji_modify,
                guild_id, emoji_id, emoji_name, roles))

    async def guild_emoji_delete(self, guild_id: str, emoji_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.guild_emoji_delete, guild_id, emoji_id))

    # endregion
    # endregion

    # region Channel functions
    async def channel_get(self, channel_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.channel_get, channel_id))

    async def channel_modify(
            self, channel_id: str, new_name: str = None, new_position: int = None, new_topic: str = None,
            new_nsfw: bool = None,
            new_bitrate: int = None, new_user_limit: int = None, new_overwrite_array: list = None,
            new_parent_id: str = None):
        params = {}
        if new_name is not None:
            params['name'] = new_name
        if new_position is not None:
            params['position'] = new_position
        if new_topic is not None:
            params['topic'] = new_topic
        if new_nsfw is not None:
            params['nsfw'] = new_nsfw
        if new_bitrate is not None:
            params['bitrate'] = new_bitrate
        if new_user_limit is not None:
            params['userlimit'] = new_user_limit
        if new_overwrite_array is not None:
            params['permission_overwrites'] = new_overwrite_array
        if new_parent_id is not None:
            params['parent_id'] = new_parent_id
        return await self.rate_limit(f_partial(self.rest_session.channel_modify, channel_id, params))

    async def channel_delete(self, channel_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.channel_delete, channel_id))

    async def channel_message_list(self, channel_id: str, limit: int = None,
                                   around: int = None, before: str = None, after: str = None) -> typing.List[dict]:
        return await self.rate_limit(
            f_partial(
                self.rest_session.channel_message_list,
                channel_id, limit, around, before, after))

    async def channel_message_iter(
            self, channel_id: str, start_id: str = None, step_size: int = 100) -> typing.AsyncGenerator[dict, None]:

        downloaded_messages_dicts: typing.List[dict] = await self.channel_message_list(
            channel_id, limit=step_size, before=start_id)

        while len(downloaded_messages_dicts) != 0:
            for d in downloaded_messages_dicts:
                yield d
            last_message_id = downloaded_messages_dicts[-1]['id']
            downloaded_messages_dicts[:] = await self.channel_message_list(channel_id,
                                                                           limit=step_size, before=last_message_id)

    async def channel_message_get(self, channel_id: str, message_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.channel_message_get, channel_id, message_id))

    async def channel_message_create(self, channel_id: str, content: str, nonce: bool = None, tts: bool = None,
                                     embed: dict = None, files_tuples: typing.Tuple[str, bytes] = None) -> dict:
        if files_tuples is None:
            fp = f_partial(
                self.rest_session.channel_message_create_json,
                channel_id, content, nonce, tts, embed)
        else:
            fp = f_partial(
                self.rest_session.channel_message_create_multipart,
                channel_id, content, nonce, tts, files_tuples)

        return await self.rate_limit(fp, ('Channel Message create|edit_async', channel_id))

    async def channel_message_reaction_create(self, channel_id: str, message_id: str, emoji: str) -> bool:
        return await self.rate_limit(
            f_partial(
                self.rest_session.channel_message_reaction_create,
                channel_id, message_id, emoji),
            ('Emoji channel:', channel_id))

    async def channel_message_reaction_my_delete(self, channel_id: str, message_id: str, emoji: int) -> bool:
        return await self.rate_limit(
            f_partial(
                self.rest_session.channel_message_reaction_my_delete,
                channel_id, message_id, emoji))

    async def channel_message_reaction_delete(self, channel_id: str, message_id: str, user_id: str,
                                              emoji: str) -> bool:
        return await self.rate_limit(
            f_partial(
                self.rest_session.channel_message_reaction_delete,
                channel_id, message_id, user_id, emoji))

    async def channel_message_reaction_list_users(self, channel_id: str, message_id: str,
                                                  emoji: str, before: str = None,
                                                  after: str = None, limit: int = None) -> typing.List[dict]:
        return await self.rate_limit(
            f_partial(
                self.rest_session.channel_message_reaction_list_users,
                channel_id, message_id, emoji, before, after, limit))

    async def channel_message_reaction_iter_users(self, channel_id: str, message_id: str, emoji: str,
                                                  step_size: int = 100) -> typing.AsyncGenerator[dict, None]:
        downloaded_users_dicts: typing.List[dict] = await self.channel_message_reaction_list_users(
            channel_id, message_id, emoji, limit=step_size)

        while len(downloaded_users_dicts) != 0:
            for d in downloaded_users_dicts:
                yield d
            last_user_id = downloaded_users_dicts[-1]['id']
            downloaded_users_dicts[:] = await self.channel_message_reaction_list_users(
                channel_id, message_id, emoji, limit=step_size, after=last_user_id)

    async def channel_message_reaction_delete_all(self, channel_id: str, message_id: str) -> bool:
        return await self.rate_limit(
            f_partial(
                self.rest_session.channel_message_reaction_delete_all,
                channel_id, message_id),
            ('Emoji channel:', channel_id))

    async def channel_message_edit(self, channel_id: str, message_id: str, content: str = None,
                                   embed: dict = None) -> dict:
        return await self.rate_limit(
            f_partial(
                self.rest_session.channel_message_edit,
                channel_id, message_id, content, embed),
            ('Channel Message create|edit_async', channel_id))

    async def channel_message_delete(self, channel_id: str, message_id: str) -> bool:
        return await self.rate_limit(f_partial(self.rest_session.channel_message_delete, channel_id, message_id))

    async def channel_message_bulk_delete(self, channel_id: str, messages_array: list) -> bool:
        return await self.rate_limit(
            f_partial(
                self.rest_session.channel_message_bulk_delete,
                channel_id, messages_array))

    async def channel_permissions_overwrite_edit(self, channel_id: str, overwrite_id: str, allow_permissions: int,
                                                 deny_permissions: int, type_of_permissions: str) -> bool:
        return await self.rate_limit(
            f_partial(
                self.rest_session.channel_permissions_overwrite_edit,
                channel_id, overwrite_id, allow_permissions, deny_permissions, type_of_permissions))

    async def channel_permissions_overwrite_delete(self, channel_id: str, overwrite_id: str) -> bool:
        return await self.rate_limit(
            f_partial(
                self.rest_session.channel_permissions_overwrite_delete,
                channel_id, overwrite_id))

    async def channel_invite_list(self, channel_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.channel_invite_list, channel_id))

    async def channel_invite_create(self, channel_id: str, max_age: int = None, max_uses: int = None,
                                    temporary_invite: bool = None, unique: bool = None) -> dict:
        return await self.rate_limit(
            f_partial(
                self.rest_session.channel_invite_create,
                channel_id, max_age, max_uses, temporary_invite, unique))

    async def channel_typing_start(self, channel_id: str) -> bool:
        return await self.rate_limit(f_partial(
            self.rest_session.channel_typing_start, channel_id),
            (self.rest_session.channel_typing_start, channel_id))

    async def channel_pins_get(self, channel_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.channel_pins_get, channel_id))

    async def channel_pins_add(self, channel_id: str, message_id: str) -> dict:
        return await self.rate_limit(
            f_partial(
                self.rest_session.channel_pins_add,
                channel_id, message_id),
            ('Channel pins', channel_id))

    async def channel_pins_delete(self, channel_id: str, message_id: str) -> bool:
        return await self.rate_limit(
            f_partial(
                self.rest_session.channel_pins_delete,
                channel_id, message_id),
            ('Channel pins', channel_id))

    # endregion

    # region Invites functions
    async def invite_get(self, invite_code: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.invite_get, invite_code))

    async def invite_delete(self, invite_code: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.invite_delete, invite_code))

    async def invite_accept(self, invite_code: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.invite_accept, invite_code))

    # endregion

    # region Webhook functions
    async def webhook_create(self, channel_id: str, name: str, avatar: bytes = None) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.webhook_create, channel_id, name, avatar))

    async def webhook_get_channel(self, channel_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.webhook_list_channel, channel_id))

    async def webhook_guild_get(self, guild_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.webhook_list_guild, guild_id))

    async def webhook_get(self, webhook_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.webhook_get, webhook_id))

    async def webhook_token_get(self, webhook_id: str, webhook_token: int) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.webhook_token_get, webhook_id, webhook_token))

    async def webhook_modify(self, webhook_id: str, name: str = None, avatar: bytes = None,
                             channel_id: str = None) -> dict:
        return await self.rate_limit(
            f_partial(
                self.rest_session.webhook_modify,
                webhook_id, name, avatar, channel_id))

    async def webhook_token_modify(self, webhook_id: str, webhook_token: int, name: str = None, avatar: bytes = None,
                                   channel_id: str = None) -> dict:
        return await self.rate_limit(
            f_partial(self.rest_session.webhook_token_modify,
                      webhook_id, webhook_token, name, avatar, channel_id))

    async def webhook_delete(self, webhook_id: str) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.webhook_delete, webhook_id))

    async def webhook_token_delete(self, webhook_id: str, webhook_token: int) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.webhook_token_delete, webhook_id, webhook_token))

    async def webhook_execute(self, webhook_id: str, webhook_token: int, content: str, username: str = None,
                              avatar_url: str = None, tts: bool = None, wait_response: bool = None) -> dict:
        return await self.rate_limit(
            f_partial(
                self.rest_session.webhook_execute,
                webhook_id, webhook_token, content, username, avatar_url, tts, wait_response),
            ('webhook', webhook_id))

    # endregion

    async def voice_region_list(self) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.voice_region_list))

    async def audit_log_get(self, guild_id: str, filter_user_id: str = None, filter_action_type: int = None,
                            before: str = None, limit: int = None) -> typing.Tuple[dict, dict, dict]:
        audit_response = await self.rate_limit(
            f_partial(
                self.rest_session.audit_log_get,
                guild_id, filter_user_id, filter_action_type, before, limit))

        return audit_response['audit_log_entries'], audit_response['users'], audit_response['webhooks']

    async def audit_log_iter(self, guild_id: str, filter_user_id: str = None, filter_action_type: int = None,
                             step_size: int = 100) -> typing.AsyncGenerator[typing.Tuple[dict, dict, dict], None]:
        audit_logs, users, webhooks = self.audit_log_get(guild_id, filter_user_id, filter_action_type,
                                                         limit=step_size)

        while len(audit_logs) != 0:
            for d in audit_logs:
                yield d, users, webhooks

            if len(audit_logs) != step_size:
                break

            last_audit_log_id = audit_logs[-1]['id']
            audit_logs, users, webhooks = self.audit_log_get(
                guild_id, filter_user_id, filter_action_type,
                before=last_audit_log_id, limit=step_size)

    async def gateway_bot_get(self) -> dict:
        return await self.rate_limit(f_partial(self.rest_session.gateway_bot_get))
