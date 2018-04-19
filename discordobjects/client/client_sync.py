import typing

from .client_async import DiscordClientAsync
import asyncio
import threading


class DiscordClientSync:

    def __init__(self, token: str, use_socket: bool = True, proxies: dict = None, default_timeout: int = 10):
        """

        wrapper template

        return asyncio.run_coroutine_threadsafe(
            self.async_client. ,
            self.client_event_loop
        ).result(timeout=self.timeout)


        :param token:
        :param use_socket:
        :param proxies:
        :param default_timeout:
        """
        self.client_event_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.client_thread = threading.Thread(target=self.client_event_loop.run_forever)
        self.client_thread.start()
        self.async_client = DiscordClientAsync(token, use_socket, proxies, self.client_event_loop)
        self.local_event_loop = asyncio.get_event_loop()
        self.timeout = default_timeout

    def user_get(self, user_id: str) -> dict:
        return asyncio.run_coroutine_threadsafe(
            self.async_client.user_get(user_id),
            self.client_event_loop
        ).result(timeout=self.timeout)

    def me_get(self) -> dict:
        return asyncio.run_coroutine_threadsafe(
            self.async_client.me_get(),
            self.client_event_loop
        ).result(timeout=self.timeout)

    def me_modify(self, username: str) -> dict:
        return asyncio.run_coroutine_threadsafe(
            self.async_client.me_modify(username),
            self.client_event_loop
        ).result(timeout=self.timeout)

    def me_guild_list(self, before: str = None, after: str = None, limit: int = None) -> dict:
        return asyncio.run_coroutine_threadsafe(
            self.async_client.me_guild_list(before, after, limit),
            self.client_event_loop
        ).result(timeout=self.timeout)

    def me_guild_leave(self, guild_id: str) -> bool:
        return asyncio.run_coroutine_threadsafe(
            self.async_client.me_guild_leave(guild_id),
            self.client_event_loop
        ).result(timeout=self.timeout)

    def me_connections_get(self) -> dict:
        return asyncio.run_coroutine_threadsafe(
            self.async_client.me_connections_get(),
            self.client_event_loop
        ).result(timeout=self.timeout)

    def me_dm_list(self) -> dict:
        return asyncio.run_coroutine_threadsafe(
            self.async_client.me_dm_list(),
            self.client_event_loop
        ).result(timeout=self.timeout)
'''
    
    async def dm_create(self, recipient_id: str) -> dict:
        return await super().dm_create(recipient_id)

    async def dm_create_group(self, access_tokens: list, nicks: dict) -> dict:
        return await super().dm_create_group(access_tokens, nicks)

    async def dm_channel_user_add(self, channel_id: str, user_id: str, access_token: str, user_nick: str) -> dict:
        return await super().dm_channel_user_add(channel_id, user_id, access_token, user_nick)

    async def dm_channel_user_remove(self, channel_id: str, user_id: str) -> dict:
        return await super().dm_channel_user_remove(channel_id, user_id)

    async def guild_create(self, guild_name: str, region: str = None, icon: str = None, verification_level: int = None,
                           default_message_notifications: int = None, roles=None, channels=None) -> dict:
        return await super().guild_create(guild_name, region, icon, verification_level, default_message_notifications,
                                          roles, channels)

    async def guild_get(self, guild_id: str) -> dict:
        return await super().guild_get(guild_id)

    async def guild_modify_name(self, guild_id: str, new_name: str) -> dict:
        return await super().guild_modify_name(guild_id, new_name)

    async def guild_modify_region(self, guild_id: str, new_region: str) -> dict:
        return await super().guild_modify_region(guild_id, new_region)

    async def guild_modify_verification_level(self, guild_id: str, new_level: int) -> dict:
        return await super().guild_modify_verification_level(guild_id, new_level)

    async def guild_modify_default_notification_level(self, guild_id: str, new_level: int) -> bool:
        return await super().guild_modify_default_notification_level(guild_id, new_level)

    async def guild_modify_afk_channel_id(self, guild_id: str, new_afk_channel_id: str) -> dict:
        return await super().guild_modify_afk_channel_id(guild_id, new_afk_channel_id)

    async def guild_modify_afk_timeout(self, guild_id: str, new_afk_timeout: int) -> dict:
        return await super().guild_modify_afk_timeout(guild_id, new_afk_timeout)

    async def guild_modify_icon(self, guild_id: str, new_icon: str) -> dict:
        return await super().guild_modify_icon(guild_id, new_icon)

    async def guild_modify_owner_id(self, guild_id: str, new_owner_id: str) -> dict:
        return await super().guild_modify_owner_id(guild_id, new_owner_id)

    async def guild_modify_splash(self, guild_id: str, new_splash: str) -> dict:
        return await super().guild_modify_splash(guild_id, new_splash)

    async def guild_modify_system_channel_id(self, guild_id: str, new_system_channel_id: str) -> dict:
        return await super().guild_modify_system_channel_id(guild_id, new_system_channel_id)

    async def guild_delete(self, guild_id: str) -> bool:
        return await super().guild_delete(guild_id)

    async def guild_channel_list(self, guild_id: str) -> dict:
        return await super().guild_channel_list(guild_id)

    async def guild_channel_create_text(self, guild_id: str, name: str, permission_overwrites: dict = None,
                                        parent_id: str = None, nsfw: bool = None) -> dict:
        return await super().guild_channel_create_text(guild_id, name, permission_overwrites, parent_id, nsfw)

    async def guild_channel_create_voice(self, guild_id: str, name: str, permission_overwrites: dict = None,
                                         parent_id: str = None, nsfw: bool = None, bitrate: int = None,
                                         user_limit: int = None) -> dict:
        return await super().guild_channel_create_voice(guild_id, name, permission_overwrites, parent_id, nsfw, bitrate,
                                                        user_limit)

    async def guild_channel_create_category(self, guild_id: str, name: str, permission_overwrites: dict = None,
                                            nsfw: bool = None) -> dict:
        return await super().guild_channel_create_category(guild_id, name, permission_overwrites, nsfw)

    async def guild_channels_position_modify(self, guild_id: str, list_of_channels: list) -> bool:
        return await super().guild_channels_position_modify(guild_id, list_of_channels)

    async def guild_member_get(self, guild_id: str, user_id: str) -> dict:
        return await super().guild_member_get(guild_id, user_id)

    async def guild_members_list(self, guild_id: str, limit: int = None, after: str = None) -> typing.List[dict]:
        return await super().guild_members_list(guild_id, limit, after)

    async def guild_member_iter(self, guild_id: str, step_size: int = 1000) -> typing.Generator[dict, None, None]:
        return await super().guild_member_iter(guild_id, step_size)

    async def guild_member_add(self, guild_id: str, user_id: str, access_token: str, nick: str = None,
                               roles: list = None, mute: bool = None, deaf: bool = None) -> dict:
        return await super().guild_member_add(guild_id, user_id, access_token, nick, roles, mute, deaf)

    async def guild_member_modify_nick(self, guild_id: str, user_id: str, nick_to_set: str) -> bool:
        return await super().guild_member_modify_nick(guild_id, user_id, nick_to_set)

    async def guild_member_modify_roles(self, guild_id: str, user_id: str, roles: list) -> bool:
        return await super().guild_member_modify_roles(guild_id, user_id, roles)

    async def guild_member_modify_mute(self, guild_id: str, user_id: str, mute_bool: bool) -> bool:
        return await super().guild_member_modify_mute(guild_id, user_id, mute_bool)

    async def guild_member_modify_deaf(self, guild_id: str, user_id: str, deaf_bool: bool) -> bool:
        return await super().guild_member_modify_deaf(guild_id, user_id, deaf_bool)

    async def guild_member_modify_move(self, guild_id: str, user_id: str, channel_move_to: int) -> bool:
        return await super().guild_member_modify_move(guild_id, user_id, channel_move_to)

    async def guild_member_me_nick_set(self, guild_id: str, nick_to_set: str) -> dict:
        return await super().guild_member_me_nick_set(guild_id, nick_to_set)

    async def guild_member_role_add(self, guild_id: str, user_id: str, role_id: str) -> bool:
        return await super().guild_member_role_add(guild_id, user_id, role_id)

    async def guild_member_role_remove(self, guild_id: str, user_id: str, role_id: str) -> bool:
        return await super().guild_member_role_remove(guild_id, user_id, role_id)

    async def guild_member_remove(self, guild_id: str, user_id: str) -> bool:
        return await super().guild_member_remove(guild_id, user_id)

    async def guild_ban_list(self, guild_id: str) -> dict:
        return await super().guild_ban_list(guild_id)

    async def guild_ban_create(self, guild_id: str, user_id: str, delete_messages_days=None) -> bool:
        return await super().guild_ban_create(guild_id, user_id, delete_messages_days)

    async def guild_ban_remove(self, guild_id: str, user_id: str) -> bool:
        return await super().guild_ban_remove(guild_id, user_id)

    async def guild_role_list(self, guild_id: str) -> dict:
        return await super().guild_role_list(guild_id)

    async def guild_role_create(self, guild_id: str, permissions: int = None, color: int = None, hoist: bool = None,
                                mentionable: bool = None) -> dict:
        return await super().guild_role_create(guild_id, permissions, color, hoist, mentionable)

    async def guild_role_position_modify(self, guild_id: str, list_of_role_positions: list) -> dict:
        return await super().guild_role_position_modify(guild_id, list_of_role_positions)

    async def _guild_role_modify(self, guild_id: str, role_id: str, params: dict) -> dict:
        return await super()._guild_role_modify(guild_id, role_id, params)

    async def guild_role_modify_name(self, guild_id: str, role_id: str, name: str) -> dict:
        return await super().guild_role_modify_name(guild_id, role_id, name)

    async def guild_role_modify_permissions(self, guild_id: str, role_id: str, permissions: int) -> dict:
        return await super().guild_role_modify_permissions(guild_id, role_id, permissions)

    async def guild_role_modify_color(self, guild_id: str, role_id: str, color: int) -> dict:
        return await super().guild_role_modify_color(guild_id, role_id, color)

    async def guild_role_modify_hoist(self, guild_id: str, role_id: str, hoist: bool) -> dict:
        return await super().guild_role_modify_hoist(guild_id, role_id, hoist)

    async def guild_role_modify_mentionable(self, guild_id: str, role_id: str, mentionable: bool) -> dict:
        return await super().guild_role_modify_mentionable(guild_id, role_id, mentionable)

    async def guild_role_delete(self, guild_id: str, role_id: str) -> dict:
        return await super().guild_role_delete(guild_id, role_id)

    async def guild_prune_get_count(self, guild_id: str, days: int) -> dict:
        return await super().guild_prune_get_count(guild_id, days)

    async def guild_prune_begin(self, guild_id: str, days: int) -> dict:
        return await super().guild_prune_begin(guild_id, days)

    async def guild_voice_region_list(self, guild_id: str) -> dict:
        return await super().guild_voice_region_list(guild_id)

    async def guild_invite_list(self, guild_id: str) -> dict:
        return await super().guild_invite_list(guild_id)

    async def guild_integration_list(self, guild_id: str) -> dict:
        return await super().guild_integration_list(guild_id)

    async def guild_integration_create(self, guild_id: str, integration_type: str, integration_id: str) -> dict:
        return await super().guild_integration_create(guild_id, integration_type, integration_id)

    async def guild_integration_modify(self, guild_id: str, integration_id: str, expire_behavior: int,
                                       expire_grace_period: int, enable_emoticons: int) -> dict:
        return await super().guild_integration_modify(guild_id, integration_id, expire_behavior, expire_grace_period,
                                                      enable_emoticons)

    async def guild_integration_delete(self, guild_id: str, integration_id: str) -> dict:
        return await super().guild_integration_delete(guild_id, integration_id)

    async def guild_integration_sync(self, guild_id: str, integration_id: str) -> dict:
        return await super().guild_integration_sync(guild_id, integration_id)

    async def guild_embed_get(self, guild_id: str) -> dict:
        return await super().guild_embed_get(guild_id)

    async def guild_embed_modify(self, guild_id: str, enabled: bool = None, channel_id: str = None) -> dict:
        return await super().guild_embed_modify(guild_id, enabled, channel_id)

    async def guild_emoji_list(self, guild_id: str) -> dict:
        return await super().guild_emoji_list(guild_id)

    async def guild_emoji_get(self, guild_id: str, emoji_id: str) -> dict:
        return await super().guild_emoji_get(guild_id, emoji_id)

    async def guild_emoji_create(self, guild_id: str, emoji_name: str, image: str, roles: tuple = ()) -> dict:
        return await super().guild_emoji_create(guild_id, emoji_name, image, roles)

    async def guild_emoji_modify(self, guild_id: str, emoji_id: str, emoji_name: str, roles: tuple = ()) -> dict:
        return await super().guild_emoji_modify(guild_id, emoji_id, emoji_name, roles)

    async def guild_emoji_delete(self, guild_id: str, emoji_id: str) -> dict:
        return await super().guild_emoji_delete(guild_id, emoji_id)

    async def channel_get(self, channel_id: str) -> dict:
        return await super().channel_get(channel_id)

    async def channel_modify_name(self, channel_id: str, name: str) -> dict:
        return await super().channel_modify_name(channel_id, name)

    async def channel_modify_position(self, channel_id: str, position: int) -> dict:
        return await super().channel_modify_position(channel_id, position)

    async def channel_modify_topic(self, channel_id: str, topic: str) -> dict:
        return await super().channel_modify_topic(channel_id, topic)

    async def channel_modify_bitrate(self, channel_id: str, bitrate: int) -> dict:
        return await super().channel_modify_bitrate(channel_id, bitrate)

    async def channel_modify_user_limit(self, channel_id: str, userlimit: int) -> dict:
        return await super().channel_modify_user_limit(channel_id, userlimit)

    async def channel_modify_permission_overwrites(self, channel_id: str, overwrite_array: list) -> dict:
        return await super().channel_modify_permission_overwrites(channel_id, overwrite_array)

    async def channel_modify_parent_id(self, channel_id: str, parent_id: str):
        return await super().channel_modify_parent_id(channel_id, parent_id)

    async def channel_delete(self, channel_id: str) -> dict:
        return await super().channel_delete(channel_id)

    async def channel_message_list(self, channel_id: str, limit: int = None, around: int = None, before: str = None,
                                   after: str = None) -> typing.List[dict]:
        return await super().channel_message_list(channel_id, limit, around, before, after)

    async def channel_message_iter(self, channel_id: str, step_size: int = 100) -> typing.AsyncGenerator[dict, None]:
        return await super().channel_message_iter(channel_id, step_size)

    async def channel_message_get(self, channel_id: str, message_id: str) -> dict:
        return await super().channel_message_get(channel_id, message_id)

    async def channel_message_create(self, channel_id: str, content: str, nonce: bool = None, tts: bool = None,
                                     embed: dict = None, files_tuples: typing.Tuple[str, bytes] = None) -> dict:
        return await super().channel_message_create(channel_id, content, nonce, tts, embed, files_tuples)

    async def channel_message_reaction_create(self, channel_id: str, message_id: str, emoji: str) -> bool:
        return await super().channel_message_reaction_create(channel_id, message_id, emoji)

    async def channel_message_reaction_my_delete(self, channel_id: str, message_id: str, emoji: int) -> bool:
        return await super().channel_message_reaction_my_delete(channel_id, message_id, emoji)

    async def channel_message_reaction_delete(self, channel_id: str, message_id: str, user_id: str, emoji: int) -> bool:
        return await super().channel_message_reaction_delete(channel_id, message_id, user_id, emoji)

    async def channel_message_reaction_list_users(self, channel_id: str, message_id: str, emoji: str,
                                                  before: str = None, after: str = None, limit: int = None) -> \
    typing.List[dict]:
        return await super().channel_message_reaction_list_users(channel_id, message_id, emoji, before, after, limit)

    async def channel_message_reaction_iter_users(self, channel_id: str, message_id: str, emoji: str,
                                                  step_size: int = 100) -> typing.AsyncGenerator[dict, None]:
        return await super().channel_message_reaction_iter_users(channel_id, message_id, emoji, step_size)

    async def channel_message_reaction_delete_all(self, channel_id: str, message_id: str) -> bool:
        return await super().channel_message_reaction_delete_all(channel_id, message_id)

    async def channel_message_edit(self, channel_id: str, message_id: str, content: str = None,
                                   embed: dict = None) -> dict:
        return await super().channel_message_edit(channel_id, message_id, content, embed)

    async def channel_message_delete(self, channel_id: str, message_id: str) -> bool:
        return await super().channel_message_delete(channel_id, message_id)

    async def channel_message_bulk_delete(self, channel_id: str, messages_array: list) -> bool:
        return await super().channel_message_bulk_delete(channel_id, messages_array)

    async def channel_permissions_overwrite_edit(self, channel_id: str, overwrite_id: str, allow_permissions: int,
                                                 deny_permissions: int, type_of_permissions: str) -> bool:
        return await super().channel_permissions_overwrite_edit(channel_id, overwrite_id, allow_permissions,
                                                                deny_permissions, type_of_permissions)

    async def channel_permissions_overwrite_delete(self, channel_id: str, overwrite_id: str) -> bool:
        return await super().channel_permissions_overwrite_delete(channel_id, overwrite_id)

    async def channel_invite_list(self, channel_id: str) -> dict:
        return await super().channel_invite_list(channel_id)

    async def channel_invite_create(self, channel_id: str, max_age: int = None, max_uses: int = None,
                                    temporary_invite: bool = None, unique: bool = None) -> dict:
        return await super().channel_invite_create(channel_id, max_age, max_uses, temporary_invite, unique)

    async def channel_typing_start(self, channel_id: str) -> bool:
        return await super().channel_typing_start(channel_id)

    async def channel_pins_get(self, channel_id: str) -> dict:
        return await super().channel_pins_get(channel_id)

    async def channel_pins_add(self, channel_id: str, message_id: str) -> dict:
        return await super().channel_pins_add(channel_id, message_id)

    async def channel_pins_delete(self, channel_id: str, message_id: str) -> bool:
        return await super().channel_pins_delete(channel_id, message_id)

    async def invite_get(self, invite_code: str) -> dict:
        return await super().invite_get(invite_code)

    async def invite_delete(self, invite_code: str) -> dict:
        return await super().invite_delete(invite_code)

    async def invite_accept(self, invite_code: str) -> dict:
        return await super().invite_accept(invite_code)

    async def webhook_create(self, channel_id: str, name: str, avatar: bytes = None) -> dict:
        return await super().webhook_create(channel_id, name, avatar)

    async def webhook_get_channel(self, channel_id: str) -> dict:
        return await super().webhook_get_channel(channel_id)

    async def webhook_guild_get(self, guild_id: str) -> dict:
        return await super().webhook_guild_get(guild_id)

    async def webhook_get(self, webhook_id: str) -> dict:
        return await super().webhook_get(webhook_id)

    async def webhook_token_get(self, webhook_id: str, webhook_token: int) -> dict:
        return await super().webhook_token_get(webhook_id, webhook_token)

    async def webhook_modify(self, webhook_id: str, name: str = None, avatar: bytes = None,
                             channel_id: str = None) -> dict:
        return await super().webhook_modify(webhook_id, name, avatar, channel_id)

    async def webhook_token_modify(self, webhook_id: str, webhook_token: int, name: str = None, avatar: bytes = None,
                                   channel_id: str = None) -> dict:
        return await super().webhook_token_modify(webhook_id, webhook_token, name, avatar, channel_id)

    async def webhook_delete(self, webhook_id: str) -> dict:
        return await super().webhook_delete(webhook_id)

    async def webhook_token_delete(self, webhook_id: str, webhook_token: int) -> dict:
        return await super().webhook_token_delete(webhook_id, webhook_token)

    async def webhook_execute(self, webhook_id: str, webhook_token: int, content: str, username: str = None,
                              avatar_url: str = None, tts: bool = None, wait_response: bool = None) -> dict:
        return await super().webhook_execute(webhook_id, webhook_token, content, username, avatar_url, tts,
                                             wait_response)

    async def voice_region_list(self) -> dict:
        return await super().voice_region_list()

    async def audit_log_get(self, guild_id: str, filter_user_id: str = None, filter_action_type: int = None,
                            before: str = None, limit: int = None) -> typing.Tuple[dict, dict, dict]:
        return await super().audit_log_get(guild_id, filter_user_id, filter_action_type, before, limit)

    async def audit_log_iter(self, guild_id: str, filter_user_id: str = None, filter_action_type: int = None,
                             step_size: int = 100) -> typing.AsyncGenerator[typing.Tuple[dict, dict, dict], None]:
        return await super().audit_log_iter(guild_id, filter_user_id, filter_action_type, step_size)

    async def gateway_bot_get(self) -> dict:
        return await super().gateway_bot_get()



'''