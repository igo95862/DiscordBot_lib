import asyncio
import typing
from _functools import partial as f_partial
from time import time, sleep

from . import discordsocket_thread, discordrest
from .constants import SocketEventNames


class DiscordClient:

    def __init__(self, token: str, use_socket: bool = True, proxies: dict = None):
        self.discord_session = discordrest.DiscordSession(token, proxies)
        self.rate_limit = self.rate_limiter_sync_sleep  
        # TODO: custom rate limiters
        self.rate_limit_table = {'global': (-1, 0)}

        self.event_loop = asyncio.get_event_loop()
        self.socket_thread = None
        # TODO: sharding
        if use_socket:
            self.socket_thread = discordsocket_thread.DiscordSocketThread(token)

    def rate_limiter_sync_sleep(self,
                                api_call_partial: f_partial,
                                table_position: tuple = None):
        """
        Rate limiter that will enter sleep until rate limit clears.

        By default tracks rate limit based on function, if the call 
        has separated rate limits for separated
        
        Semi-suitable for async development: only one call to API can be made at a time,
        but while waiting other coroutines can function in the back ground.

        :param api_call_partial: Functools partial entry that contains the call to Discord API
        :param table_position: Overwrite for table position, used when the call is rate limited based on route
        :return: requests.response object of the call
        """
        if table_position is None:
            table_position = api_call_partial.func  
            # NOTE: defaults to rate limit look up by function

        try:
            remaining_limit = self.rate_limit_table[table_position][0]
        except KeyError:
            self.rate_limit_table[table_position] = None
            remaining_limit = -1

        if remaining_limit == 0:
            sleep_time = self.rate_limit_table[table_position][1] - time()
            if sleep_time > 0:
                if not self.event_loop.is_running():
                    self.event_loop.run_until_complete(asyncio.sleep(sleep_time))
                else:
                    # HACK: blocks thread
                    sleep(sleep_time)
        response = api_call_partial()
        if 'X-RateLimit-Remaining' in response.headers:
            self.rate_limit_table[table_position] = (
                int(response.headers['X-RateLimit-Remaining']),
                int(response.headers['X-RateLimit-Reset']))
        else:
            self.rate_limit_table[table_position] = (-1, 0)
        return response

    def rate_limiter_lookup(self, table_position: tuple):
        entry = self.rate_limit_table[table_position]
        return entry[0], entry[1]

    # region Current User functions
    def me_get(self) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.me_get))
        response.raise_for_status()
        return response.json()

    def user_get(self, user_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.user_get, user_id))
        response.raise_for_status()
        return response.json()

    def me_modify(self, username: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.me_modify, username))
        response.raise_for_status()
        return response.json()

    def me_guild_list(self, before: str = None, after: str = None, limit: int = None) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.me_guild_list, before, after, limit))
        response.raise_for_status()
        return response.json()

    def me_guild_leave(self, guild_id: str) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.me_guild_leave, guild_id))
        response.raise_for_status()
        return True

    def me_connections_get(self) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.me_connections_get))
        response.raise_for_status()
        return response.json()
    # endregion

    # region Direct Messaging (DM) functions
    def dm_my_list(self) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.me_dm_list))
        response.raise_for_status()
        return response.json()

    def dm_create(self, recipient_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.dm_create, recipient_id))
        response.raise_for_status()
        return response.json()

    def dm_create_group(self, access_tokens: list, nicks: dict) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.dm_create_group, access_tokens, nicks))
        response.raise_for_status()
        return response.json()

    def dm_channel_user_add(self, channel_id: str, user_id: str, access_token: str,
                            user_nick: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.dm_user_add, channel_id,
                                             user_id, access_token, user_nick))
        response.raise_for_status()
        return response.json()

    def dm_channel_user_remove(self, channel_id: str, user_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.dm_user_remove, channel_id, user_id))
        response.raise_for_status()
        return response.json()
    # endregion

    # region Guild functions
    # region Guild
    def guild_create(self, guild_name: str, region: str = None, icon: str = None, verification_level: int = None,
                     default_message_notifications: int = None, roles=None, channels=None) -> dict:

        response = self.rate_limit(f_partial(self.discord_session.guild_create, guild_name, region, icon,
                                             verification_level, default_message_notifications, roles, channels))
        response.raise_for_status()
        return response.json()

    def guild_get(self, guild_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_get, guild_id))
        response.raise_for_status()
        return response.json()

    def guild_modify_name(self, guild_id: str, new_name: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_modify_name, guild_id, new_name))
        response.raise_for_status()
        return response.json()

    def guild_modify_region(self, guild_id: str, new_region: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_modify_region, guild_id, new_region))
        response.raise_for_status()
        return response.json()

    def guild_modify_verification_level(self, guild_id: str, new_level: int) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_modify_verification_level, guild_id, new_level))
        response.raise_for_status()
        return response.json()

    def guild_modify_default_notification_level(self, guild_id: str, new_level: int) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.guild_modify_default_notification_level,
                                             guild_id, new_level))
        response.raise_for_status()
        return response.json()

    def guild_modify_afk_channel_id(self, guild_id: str, new_afk_channel_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_modify_afk_channel_id, guild_id,
                                             new_afk_channel_id))
        response.raise_for_status()
        return response.json()

    def guild_modify_afk_timeout(self, guild_id: str, new_afk_timeout: int) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_modify_afk_timeout, guild_id, new_afk_timeout))
        response.raise_for_status()
        return response.json()

    def guild_modify_icon(self, guild_id: str, new_icon: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_modify_icon, guild_id, new_icon))
        response.raise_for_status()
        return response.json()

    def guild_modify_owner_id(self, guild_id: str, new_owner_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_modify_owner_id, guild_id, new_owner_id))
        response.raise_for_status()
        return response.json()

    def guild_modify_splash(self, guild_id: str, new_splash: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_modify_splash, guild_id, new_splash))
        response.raise_for_status()
        return response.json()

    def guild_modify_system_channel_id(self, guild_id: str, new_system_channel_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_modify_system_channel_id, guild_id,
                                             new_system_channel_id))
        response.raise_for_status()
        return response.json()

    def guild_delete(self, guild_id: str) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.guild_delete, guild_id))
        response.raise_for_status()
        return True
    # endregion

    # region Guild Channels
    def guild_channel_list(self, guild_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_channel_list, guild_id))
        response.raise_for_status()
        return response.json()

    def guild_channel_create_text(self, guild_id: str, name: str, permission_overwrites: dict = None,
                                  parent_id: str = None, nsfw: bool = None) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_channel_create_text, guild_id, 
                                             name, permission_overwrites, parent_id, nsfw))
        response.raise_for_status()
        return response.json()

    def guild_channel_create_voice(self, guild_id: str, name: str, permission_overwrites: dict = None,
                                   parent_id: str = None, nsfw: bool = None, bitrate: int = None,
                                   user_limit: int = None) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_channel_create_voice, guild_id,
                                             name, permission_overwrites, parent_id, nsfw, bitrate, user_limit))
        response.raise_for_status()
        return response.json()

    def guild_channel_create_category(self, guild_id: str, name: str, permission_overwrites: dict = None,
                                      nsfw: bool = None) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_channel_create_category, guild_id,
                                             name, permission_overwrites, nsfw))
        response.raise_for_status()
        return response.json()

    def guild_channels_position_modify(self, guild_id: str, list_of_channels: list) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.guild_channels_position_modify, guild_id,
                                             list_of_channels))
        response.raise_for_status()
        return True
    # endregion

    # region Guild Members
    def guild_member_get(self, guild_id: str, user_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_member_get, guild_id, user_id))
        response.raise_for_status()
        return response.json()
        
    def guild_members_list(self, guild_id: str, limit: int = None, after: str = None) -> typing.List[dict]:
        response = self.rate_limit(f_partial(self.discord_session.guild_member_list, guild_id, limit, after))
        response.raise_for_status()
        return response.json()

    def guild_member_iter(self, guild_id: str, step_size: int = 1000) -> typing.Generator[dict, None, None]:
        downloaded_member_dicts = self.guild_members_list(guild_id, limit=step_size)

        while len(downloaded_member_dicts) != 0:
            for d in downloaded_member_dicts:
                yield d
            last_member_id = downloaded_member_dicts[-1]['user']['id']
            downloaded_member_dicts[:] = self.guild_members_list(guild_id, limit=step_size, after=last_member_id)

    def guild_member_add(self, guild_id: str, user_id: str, access_token: str, nick: str = None, roles: list = None,
                         mute: bool = None, deaf: bool = None) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_member_add, guild_id, user_id, access_token,
                                             nick, roles, mute, deaf))
        response.raise_for_status()
        return response.json()
        
    def guild_member_modify_nick(self, guild_id: str, user_id: str, nick_to_set: str) -> bool:
        response = self.rate_limit(
            f_partial(self.discord_session.guild_member_modify_nick, guild_id, user_id, nick_to_set),
            (self.discord_session.guild_member_modify, guild_id))
        response.raise_for_status()
        return True
        
    def guild_member_modify_roles(self, guild_id: str, user_id: str, roles: list) -> bool:
        response = self.rate_limit(
            f_partial(self.discord_session.guild_member_modify_roles, guild_id, user_id, roles),
            (self.discord_session.guild_member_modify, guild_id))
        response.raise_for_status()
        return True
        
    def guild_member_modify_mute(self, guild_id: str, user_id: str, mute_bool: bool) -> bool:
        response = self.rate_limit(
            f_partial(self.discord_session.guild_member_modify_mute, guild_id, user_id, mute_bool)
            (self.discord_session.guild_member_modify, guild_id))
        response.raise_for_status()
        return True
        
    def guild_member_modify_deaf(self, guild_id: str, user_id: str, deaf_bool: bool) -> bool:
        response = self.rate_limit(
            f_partial(self.discord_session.guild_member_modify_deaf, guild_id, user_id, deaf_bool),
            (self.discord_session.guild_member_modify, guild_id))
        response.raise_for_status()
        return True
        
    def guild_member_modify_move(self, guild_id: str, user_id: str, channel_move_to: int) -> bool:
        response = self.rate_limit(
            f_partial(self.discord_session.guild_member_modify_move, guild_id, user_id, channel_move_to),
            (self.discord_session.guild_member_modify, guild_id))
        response.raise_for_status()
        return True
        
    def guild_member_me_nick_set(self, guild_id: str, nick_to_set: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_member_me_nick_set, guild_id, nick_to_set))
        response.raise_for_status()
        return response.json()
        
    def guild_member_role_add(self, guild_id: str, user_id: str, role_id: str) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.guild_member_role_add, guild_id, user_id, role_id),
                                   ("Guild member role manipulation: ", guild_id))
        response.raise_for_status()
        return True
        
    def guild_member_role_remove(self, guild_id: str, user_id: str, role_id: str) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.guild_member_role_remove, guild_id, user_id, role_id),
                                   ("Guild member role manipulation: ", guild_id))
        response.raise_for_status()
        return True
        
    def guild_member_remove(self, guild_id: str, user_id: str) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.guild_member_remove, guild_id, user_id))
        response.raise_for_status()
        return True
    # endregion

    def guild_ban_list(self, guild_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_ban_list, guild_id))
        response.raise_for_status()
        return response.json()

    def guild_ban_create(self, guild_id: str, user_id: str, delete_messages_days=None) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.guild_ban_create, guild_id, user_id,
                                             delete_messages_days))
        response.raise_for_status()
        return True

    def guild_ban_remove(self, guild_id: str, user_id: str) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.guild_ban_remove, guild_id, user_id))
        response.raise_for_status()
        return True

    # region Guild Roles
    def guild_role_list(self, guild_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_role_list, guild_id))
        response.raise_for_status()
        return response.json()
        
    def guild_role_create(self, guild_id: str, permissions: int = None, color: int = None, hoist: bool = None,
                          mentionable: bool = None) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_role_create, guild_id,
                                             permissions, color, hoist, mentionable))
        response.raise_for_status()
        return response.json()
        
    def guild_role_position_modify(self, guild_id: str, list_of_role_positions: list) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_role_position_modify, guild_id,
                                             list_of_role_positions))
        response.raise_for_status()
        return response.json()
        
    def _guild_role_modify(self, guild_id: str, role_id: str, params: dict) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_role_modify, guild_id, role_id, params))
        response.raise_for_status()
        return response.json()
        
    def guild_role_modify_name(self, guild_id: str, role_id: str, name: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_role_modify_name, guild_id, role_id, name))
        response.raise_for_status()
        return response.json()
        
    def guild_role_modify_permissions(self, guild_id: str, role_id: str, permissions: int) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_role_modify_permissions, guild_id, role_id,
                                             permissions))
        response.raise_for_status()
        return response.json()
        
    def guild_role_modify_color(self, guild_id: str, role_id: str, color: int) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_role_modify_color, guild_id, role_id, color))
        response.raise_for_status()
        return response.json()
        
    def guild_role_modify_hoist(self, guild_id: str, role_id: str, hoist: bool) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_role_modify_hoist, guild_id, role_id, hoist))
        response.raise_for_status()
        return response.json()
        
    def guild_role_modify_mentionable(self, guild_id: str, role_id: str, mentionable: bool) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_role_modify_mentionable, guild_id, role_id,
                                             mentionable))
        response.raise_for_status()
        return response.json()
        
    def guild_role_delete(self, guild_id: str, role_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_role_delete, guild_id, role_id))
        response.raise_for_status()
        return response.json()
    # endregion

    def guild_prune_get_count(self, guild_id: str, days: int) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_prune_get_count, guild_id, days))
        response.raise_for_status()
        return response.json()
        
    def guild_prune_begin(self, guild_id: str, days: int) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_prune_begin, guild_id, days))
        response.raise_for_status()
        return response.json()
        
    def guild_voice_region_list(self, guild_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_voice_region_list, guild_id))
        response.raise_for_status()
        return response.json()
        
    def guild_invite_list(self, guild_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_invite_list, guild_id))
        response.raise_for_status()
        return response.json()
        
    def guild_integration_list(self, guild_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_integration_list, guild_id))
        response.raise_for_status()
        return response.json()
        
    def guild_integration_create(self, guild_id: str, integration_type: str, integration_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_integration_create, guild_id,
                                             integration_type, integration_id))
        response.raise_for_status()
        return response.json()
        
    def guild_integration_modify(self, guild_id: str, integration_id: str,
                                 expire_behavior: int, expire_grace_period: int, enable_emoticons: int) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_integration_modify, guild_id,
                                             integration_id, expire_behavior, expire_grace_period, enable_emoticons))
        response.raise_for_status()
        return response.json()
        
    def guild_integration_delete(self, guild_id: str, integration_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_integration_delete, guild_id, integration_id))
        response.raise_for_status()
        return response.json()
        
    def guild_integration_sync(self, guild_id: str, integration_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_integration_sync, guild_id, integration_id))
        response.raise_for_status()
        return response.json()
        
    def guild_embed_get(self, guild_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_embed_get, guild_id))
        response.raise_for_status()
        return response.json()
        
    def guild_embed_modify(self, guild_id: str, enabled: bool = None, channel_id: str = None) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_embed_modify, guild_id, enabled, channel_id))
        response.raise_for_status()
        return response.json()

    # region Guild Emoji
    def guild_emoji_list(self, guild_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_emoji_list, guild_id))
        response.raise_for_status()
        return response.json()
        
    def guild_emoji_get(self, guild_id: str, emoji_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_emoji_get, guild_id, emoji_id))
        response.raise_for_status()
        return response.json()
        
    def guild_emoji_create(self, guild_id: str, emoji_name: str, image: str, roles: tuple = ()) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_emoji_create, guild_id,
                                             emoji_name, image, roles))
        response.raise_for_status()
        return response.json()
        
    def guild_emoji_modify(self, guild_id: str, emoji_id: str, emoji_name: str, roles: tuple = ()) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_emoji_modify, guild_id, emoji_id,
                                             emoji_name, roles))
        response.raise_for_status()
        return response.json()
        
    def guild_emoji_delete(self, guild_id: str, emoji_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.guild_emoji_delete, guild_id, emoji_id))
        response.raise_for_status()
        return response.json()
    # endregion
    # endregion

    # region Channel functions
    def channel_get(self, channel_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.channel_get, channel_id))
        response.raise_for_status()
        return response.json()

    def channel_modify_name(self, channel_id: str, name: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.channel_modify_name, channel_id, name))
        response.raise_for_status()
        return response.json()
        
    def channel_modify_position(self, channel_id: str, position: int) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.channel_modify_position, channel_id, position))
        response.raise_for_status()
        return response.json()
        
    def channel_modify_topic(self, channel_id: str, topic: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.channel_modify_topic, channel_id, topic))
        response.raise_for_status()
        return response.json()
        
    def channel_modify_bitrate(self, channel_id: str, bitrate: int) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.channel_modify_bitrate, channel_id, bitrate))
        response.raise_for_status()
        return response.json()
        
    def channel_modify_user_limit(self, channel_id: str, userlimit: int) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.channel_modify_user_limit, channel_id, userlimit))
        response.raise_for_status()
        return response.json()
        
    def channel_modify_permission_overwrites(self, channel_id: str, overwrite_array: list) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.channel_modify_permission_overwrites, channel_id,
                                             overwrite_array))
        response.raise_for_status()
        return response.json()

    def channel_modify_parent_id(self, channel_id: str, parent_id: str):
    
        response = self.rate_limit(f_partial(self.discord_session.channel_modify_parent_id, channel_id, parent_id))
        response.raise_for_status()
        return response.json()

    def channel_delete(self, channel_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.channel_delete, channel_id))
        response.raise_for_status()
        return response.json()
        
    def channel_message_list(self, channel_id: str, limit: int = None, around: int = None, before: str = None,
                             after: str = None) -> typing.List[dict]:
        response = self.rate_limit(f_partial(self.discord_session.channel_message_list, channel_id,
                                             limit, around, before, after))
        response.raise_for_status()
        return response.json()

    def channel_message_iter(self, channel_id: str, step_size: int = 100) -> typing.Generator[dict, None, None]:
        downloaded_messages_dicts = self.channel_message_list(channel_id, limit=step_size)

        while len(downloaded_messages_dicts) != 0:
            for d in downloaded_messages_dicts:
                yield d
            last_message_id = downloaded_messages_dicts[-1]['id']
            downloaded_messages_dicts[:] = self.channel_message_list(channel_id, limit=step_size,
                                                                     before=last_message_id)
        
    def channel_message_get(self, channel_id: str, message_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.channel_message_get, channel_id, message_id))
        response.raise_for_status()
        return response.json()
        
    def channel_message_create(self, channel_id: str, content: str, nonce: bool = None, tts: bool = None,
                               embed: dict = None, files_tuples: typing.Tuple[str, bytes] = None) -> dict:
        if files_tuples is None:
            fp = f_partial(self.discord_session.channel_message_create_json, channel_id, content, nonce, tts, embed)
        else:
            fp = f_partial(self.discord_session.channel_message_create_multipart, channel_id, content, nonce, tts,
                           files_tuples)

        response = self.rate_limit(fp, (self.discord_session.channel_message_create_json, channel_id))
        response.raise_for_status()
        return response.json()
        
    def channel_message_reaction_create(self, channel_id: str, message_id: str, emoji: str) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.channel_message_reaction_create, channel_id,
                                             message_id, emoji),
                                   ('Emoji channel:', channel_id))
        response.raise_for_status()
        return True
        
    def channel_message_reaction_my_delete(self, channel_id: str, message_id: str, emoji: int) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.channel_message_reaction_my_delete, channel_id,
                                             message_id, emoji))
        response.raise_for_status()
        return True
        
    def channel_message_reaction_delete(self, channel_id: str, message_id: str, user_id: str,
                                        emoji: int) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.channel_message_reaction_delete, channel_id,
                                             message_id, user_id, emoji))
        response.raise_for_status()
        return True
        
    def channel_message_reaction_list_users(self, channel_id: str, message_id: str, emoji: str, before: str = None,
                                            after: str = None, limit: int = None) -> typing.List[dict]:
        response = self.rate_limit(f_partial(self.discord_session.channel_message_reaction_list_users, channel_id,
                                             message_id, emoji, before, after, limit))
        response.raise_for_status()
        return response.json()

    def channel_message_reaction_iter_users(self, channel_id: str, message_id: str, emoji: str,
                                            step_size: int = 100) -> typing.Generator[dict, None, None]:
        downloaded_users_dicts = self.channel_message_reaction_list_users(channel_id, message_id, emoji,
                                                                          limit=step_size)

        while len(downloaded_users_dicts) != 0:
            for d in downloaded_users_dicts:
                yield d
            last_user_id = downloaded_users_dicts[-1]['id']
            downloaded_users_dicts[:] = self.channel_message_reaction_list_users(channel_id, message_id, emoji,
                                                                                 limit=step_size, after=last_user_id)
        
    def channel_message_reaction_delete_all(self, channel_id: str, message_id: str) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.channel_message_reaction_delete_all, channel_id,
                                             message_id),
                                   ('Emoji channel:', channel_id))
        response.raise_for_status()
        return True
        
    def channel_message_edit(self, channel_id: str, message_id: str, content: str = None,
                             embed: dict = None) -> dict:
        response = self.rate_limit(
            f_partial(self.discord_session.channel_message_edit, channel_id, message_id, content, embed),
            (self.discord_session.channel_message_edit, channel_id))
        response.raise_for_status()
        return response.json()
        
    def channel_message_delete(self, channel_id: str, message_id: str) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.channel_message_delete, channel_id, message_id))
        response.raise_for_status()
        return True
        
    def channel_message_bulk_delete(self, channel_id: str, messages_array: list) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.channel_message_bulk_delete, channel_id,
                                             messages_array))
        response.raise_for_status()
        return True
        
    def channel_permissions_overwrite_edit(self, channel_id: str, overwrite_id: str, allow_permissions: int,
                                           deny_permissions: int, type_of_permissions: str) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.channel_permissions_overwrite_edit, channel_id,
                                             overwrite_id, allow_permissions, deny_permissions, type_of_permissions))
        response.raise_for_status()
        return True
        
    def channel_permissions_overwrite_delete(self, channel_id: str, overwrite_id: str) -> bool:
        response = self.rate_limit(f_partial(self.discord_session.channel_permissions_overwrite_delete, channel_id,
                                             overwrite_id))
        response.raise_for_status()
        return True
        
    def channel_invite_list(self, channel_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.channel_invite_list, channel_id))
        response.raise_for_status()
        return response.json()
        
    def channel_invite_create(self, channel_id: str, max_age: int = None, max_uses: int = None,
                              temporary_invite: bool = None, unique: bool = None) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.channel_invite_create, channel_id,
                                             max_age, max_uses, temporary_invite, unique))
        response.raise_for_status()
        return response.json()
        
    def channel_typing_start(self, channel_id: str) -> bool:
        response = self.rate_limit(f_partial(
            self.discord_session.channel_typing_start, channel_id),
            (self.discord_session.channel_typing_start, channel_id))
        response.raise_for_status()
        return True
        
    def channel_pins_get(self, channel_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.channel_pins_get, channel_id))
        response.raise_for_status()
        return response.json()
        
    def channel_pins_add(self, channel_id: str, message_id: str) -> dict:
        response = self.rate_limit(
            f_partial(self.discord_session.channel_pins_add, channel_id, message_id),
            (self.discord_session.channel_pins_add, channel_id))
        response.raise_for_status()
        return response.json()
        
    def channel_pins_delete(self, channel_id: str, message_id: str) -> bool:
        response = self.rate_limit(
            f_partial(self.discord_session.channel_pins_delete, channel_id, message_id),
            (self.discord_session.channel_pins_add, channel_id))
        response.raise_for_status()
        return True
    # endregion

    # region Invites functions
    def invite_get(self, invite_code: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.invite_get, invite_code))
        response.raise_for_status()
        return response.json()
        
    def invite_delete(self, invite_code: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.invite_delete, invite_code))
        response.raise_for_status()
        return response.json()
        
    def invite_accept(self, invite_code: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.invite_accept, invite_code))
        response.raise_for_status()
        return response.json()
    # endregion

    # region Webhook functions
    def webhook_create(self, channel_id: str, name: str, avatar: bytes = None) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.webhook_create, channel_id, name, avatar))
        response.raise_for_status()
        return response.json()
        
    def webhook_get_channel(self, channel_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.webhook_list_channel, channel_id))
        response.raise_for_status()
        return response.json()
        
    def webhook_guild_get(self, guild_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.webhook_list_guild, guild_id))
        response.raise_for_status()
        return response.json()
        
    def webhook_get(self, webhook_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.webhook_get, webhook_id))
        response.raise_for_status()
        return response.json()
        
    def webhook_token_get(self, webhook_id: str, webhook_token: int) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.webhook_token_get, webhook_id, webhook_token))
        response.raise_for_status()
        return response.json()
        
    def webhook_modify(self, webhook_id: str, name: str = None, avatar: bytes = None,
                       channel_id: str = None) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.webhook_modify, webhook_id, name, avatar, channel_id))
        response.raise_for_status()
        return response.json()
        
    def webhook_token_modify(self, webhook_id: str, webhook_token: int, name: str = None, avatar: bytes = None,
                             channel_id: str = None) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.webhook_token_modify, webhook_id, webhook_token,
                                             name, avatar, channel_id))
        response.raise_for_status()
        return response.json()
        
    def webhook_delete(self, webhook_id: str) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.webhook_delete, webhook_id))
        response.raise_for_status()
        return response.json()
        
    def webhook_token_delete(self, webhook_id: str, webhook_token: int) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.webhook_token_delete, webhook_id, webhook_token))
        response.raise_for_status()
        return response.json()
        
    def webhook_execute(self, webhook_id: str, webhook_token: int, content: str, username: str = None,
                        avatar_url: str = None, tts: bool = None, wait_response: bool = None) -> dict:
        response = self.rate_limit(
            f_partial(self.discord_session.webhook_execute, webhook_id, webhook_token,
                      content, username, avatar_url, tts, wait_response),
            ('webhook', webhook_id))
        response.raise_for_status()
        return response.json()
    # endregion

    # region Special functions
    def voice_region_list(self) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.voice_region_list))
        response.raise_for_status()
        return response.json()

    def audit_log_get(self, guild_id: str, filter_user_id: str = None, filter_action_type: int = None,
                      before: str = None, limit: int = None) -> typing.Tuple[dict, dict, dict]:
        response = self.rate_limit(f_partial(self.discord_session.audit_log_get, guild_id,
                                             filter_user_id, filter_action_type, before, limit))
        response.raise_for_status()
        audit_response = response.json()
        return audit_response['audit_log_entries'], audit_response['users'], audit_response['webhooks']

    def audit_log_iter(self, guild_id: str, filter_user_id: str = None, filter_action_type: int = None,
                       step_size: int = 100) -> typing.Generator[typing.Tuple[dict, dict, dict], None, None]:
        audit_logs, users, webhooks = self.audit_log_get(guild_id, filter_user_id, filter_action_type, limit=step_size)

        while len(audit_logs) != 0:
            for d in audit_logs:
                yield d, users, webhooks

            if len(audit_logs) != step_size:
                break

            last_audit_log_id = audit_logs[-1]['id']
            audit_logs, users, webhooks = self.audit_log_get(
                guild_id, filter_user_id, filter_action_type,
                before=last_audit_log_id, limit=step_size)
        
    def gateway_bot_get(self) -> dict:
        response = self.rate_limit(f_partial(self.discord_session.gateway_bot_get))
        response.raise_for_status()
        return response.json()
    # endregion

    # region Web socket functions

    # region Channel
    async def event_gen_channel_create(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.CHANNEL_CREATE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_channel_update(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.CHANNEL_UPDATE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_channel_delete(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.CHANNEL_DELETE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_channel_pins_update(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.CHANNEL_PINS_UPDATE)
        while True:
            yield (await queue.get())[0]

    # endregion

    # region Guild
    async def event_gen_guild_create(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.GUILD_CREATE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_guild_update(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.GUILD_UPDATE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_guild_delete(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.GUILD_DELETE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_guild_ban_add(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.GUILD_BAN_ADD)
        while True:
            yield (await queue.get())[0]

    async def event_gen_guild_ban_remove(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.GUILD_BAN_REMOVE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_guild_emojies_update(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.GUILD_EMOJIS_UPDATE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_guild_integrations_update(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.GUILD_INTEGRATIONS_UPDATE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_guild_member_add(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.GUILD_MEMBER_ADD)
        while True:
            yield (await queue.get())[0]

    async def event_gen_guild_member_remove(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.GUILD_MEMBER_REMOVE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_guild_member_update(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.GUILD_MEMBER_UPDATE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_guild_role_create(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.GUILD_ROLE_CREATE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_guild_role_update(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.GUILD_ROLE_UPDATE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_guild_role_delete(self) -> dict:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.GUILD_ROLE_DELETE)
        while True:
            yield (await queue.get())[0]

    # endregion

    # region Message
    async def event_gen_message_create(self) -> typing.Generator[dict, None, None]:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.MESSAGE_CREATE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_message_update(self) -> typing.Generator[dict, None, None]:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.MESSAGE_UPDATE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_message_delete(self) -> typing.Generator[dict, None, None]:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.MESSAGE_DELETE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_message_delete_bulk(self) -> typing.Generator[dict, None, None]:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.MESSAGE_DELETE_BULK)
        while True:
            yield (await queue.get())[0]

    async def event_gen_message_reaction_add(self) -> typing.Generator[dict, None, None]:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.MESSAGE_REACTION_ADD)
        while True:
            yield (await queue.get())[0]

    async def event_gen_message_reaction_remove(self) -> typing.Generator[dict, None, None]:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.MESSAGE_REACTION_REMOVE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_message_reaction_remove_all(self) -> typing.Generator[dict, None, None]:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.MESSAGE_REACTION_REMOVE_ALL)
        while True:
            yield (await queue.get())[0]

    # endregion

    # region Presence
    async def event_gen_presence_update(self) -> typing.Generator[dict, None, None]:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.PRESENCE_UPDATE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_typing_start(self) -> typing.Generator[dict, None, None]:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.TYPING_START)
        while True:
            yield (await queue.get())[0]

    async def event_gen_user_update_gen(self) -> typing.Generator[dict, None, None]:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.USER_UPDATE)
        while True:
            yield (await queue.get())[0]

    # endregion

    # region Voice
    async def event_gen_voice_state_update_gen(self) -> typing.AsyncGenerator[dict, None]:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.VOICE_STATE_UPDATE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_voice_server_update_gen(self) -> typing.AsyncGenerator[dict, None]:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.VOICE_SERVER_UPDATE)
        while True:
            yield (await queue.get())[0]

    # endregion

    async def event_gen_webhooks_update(self) -> typing.Generator[dict, None, None]:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_single(queue, SocketEventNames.WEBHOOKS_UPDATE)
        while True:
            yield (await queue.get())[0]

    async def event_gen_multiple(self, event_names_tuple: typing.Tuple[str, ...]
                                 ) -> typing.Generator[typing.Tuple[dict, str], None, None]:
        queue = asyncio.Queue()
        self.socket_thread.event_queue_add_multiple(queue, event_names_tuple)
        while True:
            yield (await queue.get())

    # endregion
