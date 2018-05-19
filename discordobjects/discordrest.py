from requests import Response as RequestsResponse
from requests import Session as RequestsSession
import typing


class DiscordSession(RequestsSession):

    def __init__(self, token: str, proxies: dict = None):
        super(DiscordSession, self).__init__()
        self.headers.update({'Authorization': 'Bot ' + token})
        if proxies is not None:
            self.proxies = proxies

    API_URL = 'https://discordapp.com/api/v6'
    API_URL_LENGTH = len(API_URL)
    TIMEOUT_OVERWRITE = 5

    # region Timeout overwrites
    def get(self, *args, **kwargs) -> RequestsResponse:
        return super().get(*args, **kwargs, timeout=self.TIMEOUT_OVERWRITE)

    def post(self, *args, **kwargs) -> RequestsResponse:
        return super().post(*args, **kwargs, timeout=self.TIMEOUT_OVERWRITE)

    def patch(self, *args, **kwargs) -> RequestsResponse:
        return super().patch(*args, **kwargs, timeout=self.TIMEOUT_OVERWRITE)

    def delete(self, *args, **kwargs) -> RequestsResponse:
        return super().delete(*args, **kwargs, timeout=self.TIMEOUT_OVERWRITE)

    def put(self, *args, **kwargs) -> RequestsResponse:
        return super().put(*args, **kwargs, timeout=self.TIMEOUT_OVERWRITE)
    # endregion

    # region Current User REST API calls

    def me_get(self) -> RequestsResponse:
        return self.get(f'{self.API_URL}/users/@me')

    def user_get(self, user_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/users/{user_id}')

    def me_modify(self, username: str) -> RequestsResponse:
        # TODO: add avatar change support
        return self.patch(f'{self.API_URL}/users/@me', json={'username': username})

    def me_guild_list(self, before: str = None, after: str = None, limit: int = None) -> RequestsResponse:
        params = {}
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        if limit is not None:
            params['limit'] = limit
        return self.get(f'{self.API_URL}/users/@me/guilds', params=params or None)

    def me_guild_leave(self, guild_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/users/@me/guilds/{guild_id}')

    def me_connections_get(self) -> RequestsResponse:
        return self.get(f'{self.API_URL}/users/@me/connections')

    def me_dm_list(self) -> RequestsResponse:
        return self.get(f'{self.API_URL}/users/@me/channels')

    # Direct Messaging (DM) calls

    def dm_create(self, recipient_id: str) -> RequestsResponse:
        return self.post(f'{self.API_URL}/users/@me/channels', json={'recipient_id': recipient_id})

    def dm_create_group(self, access_tokens: list, nicks: dict) -> RequestsResponse:
        # NOTE: Have not been tested.
        return self.post(f'{self.API_URL}/users/@me/channels', json={'access_tokens': access_tokens, 'nicks': nicks})

    def dm_user_add(self, channel_id: str, user_id: str, access_token: str, user_nick: str) -> RequestsResponse:
        return self.put(f'{self.API_URL}/channels/{channel_id}/recipients/{user_id}',
                        json={'access_token': access_token, 'nick': user_nick})

    def dm_user_remove(self, channel_id: str, user_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/channels/{channel_id}/recipients/{user_id}')
    # endregion

    # region Guild REST API calls

    def guild_create(self, guild_name: str, region: str = None, icon: str = None, verification_level: int = None,
                     default_message_notifications: int = None, roles=None, channels=None) -> RequestsResponse:
        json_params = {'name': guild_name}
        if region is not None:
            json_params['region'] = region
        if icon is not None:
            json_params['icon'] = icon
        if verification_level is not None:
            json_params['verification_level'] = verification_level
        if default_message_notifications is not None:
            json_params['default_message_notifications'] = default_message_notifications
        if roles is not None:
            json_params['roles'] = roles
        if channels is not None:
            json_params['channels'] = channels

        return self.post(f'{self.API_URL}/guilds', json=json_params)

    def guild_get(self, guild_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/guilds/{guild_id}')

    def guild_modify(
            self, guild_id: str, new_name: str = None, new_voice_region_id: str = None,
            new_verification_level: int = None, new_default_level_notifications: int = None,
            new_explicit_content_filter: int = None, new_afk_channel_id: str = None,
            new_afk_timeout: int = None, new_icon: str = None, new_owner: str = None,
            new_splash: str = None, new_system_channel_id: str = None) -> RequestsResponse:
        params = {}
        if new_name is not None:
            params['name'] = new_name
        if new_voice_region_id is not None:
            params['voice_region_id'] = new_voice_region_id
        if new_verification_level is not None:
            params['verification_level'] = new_verification_level
        if new_default_level_notifications is not None:
            params['default_level_notifications'] = new_default_level_notifications
        if new_explicit_content_filter is not None:
            params['explicit_content_filter'] = new_explicit_content_filter
        if new_afk_channel_id is not None:
            params['afk_channel_id'] = new_afk_channel_id
        if new_afk_timeout is not None:
            params['afk_timeout'] = new_afk_timeout
        if new_icon is not None:
            params['icon'] = new_icon
        if new_owner is not None:
            params['owner_id'] = new_owner
        if new_splash is not None:
            params['splash'] = new_splash
        if new_system_channel_id is not None:
            params['system_channel_id'] = new_system_channel_id
        return self.patch(f'{self.API_URL}/guilds/{guild_id}', json=params)

    def guild_delete(self, guild_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/guilds/{guild_id}')

    # region Guild Channels
    def guild_channel_list(self, guild_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/guilds/{guild_id}/channels')

    def _guild_channel_create(self, guild_id: str, params: dict) -> RequestsResponse:
        # NOTE: this function should not be called directly
        return self.post(f'{self.API_URL}/guilds/{guild_id}/channels', json=params)

    def guild_channel_create_text(self, guild_id: str, name: str, permission_overwrites: typing.List[dict] = None,
                                  parent_id: str = None, nsfw: bool = None) -> RequestsResponse:
        new_channel_params = {'name': name, 'type': 0}
        if permission_overwrites is not None:
            new_channel_params['permission_overwrites'] = permission_overwrites
        if parent_id is not None:
            new_channel_params['parent_id'] = parent_id
        if nsfw is not None:
            new_channel_params['nsfw'] = nsfw

        return self._guild_channel_create(guild_id, new_channel_params)

    def guild_channel_create_voice(self, guild_id: str, name: str, permission_overwrites: typing.List[dict] = None,
                                   parent_id: str = None, nsfw: bool = None,
                                   bitrate: int = None, user_limit: int = None) -> RequestsResponse:
        new_channel_params = {'name': name, 'type': 2}
        if permission_overwrites is not None:
            new_channel_params['permission_overwrites'] = permission_overwrites
        if parent_id is not None:
            new_channel_params['parent_id'] = parent_id
        if nsfw is not None:
            new_channel_params['nsfw'] = nsfw
        if bitrate is not None:
            new_channel_params['bitrate'] = bitrate
        if user_limit is not None:
            new_channel_params['user_limit'] = user_limit

        return self._guild_channel_create(guild_id, new_channel_params)

    def guild_channel_create_category(self, guild_id: str, name: str, permission_overwrites: typing.List[dict] = None,
                                      nsfw: bool = None) -> RequestsResponse:
        # NOTE: Category channels can't have parents. Not documented in API reference but was found experimentally
        new_channel_params = {'name': name, 'type': 4}
        if permission_overwrites is not None:
            new_channel_params['permission_overwrites'] = permission_overwrites
        if nsfw is not None:
            new_channel_params['nsfw'] = nsfw

        return self._guild_channel_create(guild_id, new_channel_params)

    def guild_channels_position_modify(
            self, guild_id: str,
            list_of_channels: typing.List[typing.Dict[str, int]]) -> RequestsResponse:
        # NOTE: This call requires list of dictionaries with with field of id of the channel and its position.
        # Position integers are independent of each other.
        # Multiple channels can have same position. There can be gaps between them.
        # Position integer can also be negative.
        # Unlike what documentation says you can pass a single channel to this call.
        return self.patch(f'{self.API_URL}/guilds/{guild_id}/channels', json=list_of_channels)
    # endregion

    # region Guild Member
    def guild_member_get(self, guild_id: str, user_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/guilds/{guild_id}/members/{user_id}')

    def guild_member_list(self, guild_id: str, limit: int = None, after: str = None) -> RequestsResponse:
        # NOTE: default amount of users returned is just one
        params = {}
        if limit is not None:
            params['limit'] = limit
        if after is not None:
            params['after'] = after
        return self.get(f'{self.API_URL}/guilds/{guild_id}/members', params=params or None)

    def guild_member_add(self, guild_id: str, user_id: str, access_token: str, nick: str = None, roles: list = None,
                         mute: bool = None, deaf: bool = None) -> RequestsResponse:
        params = {'access_token': access_token}
        if nick is not None:
            params['nick'] = nick
        if roles is not None:
            params['roles'] = roles
        if mute is not None:
            params['mute'] = mute
        if deaf is not None:
            params['deaf'] = deaf
        return self.put(f'{self.API_URL}/guilds/{guild_id}/members/{user_id}', json=params)

    def guild_member_modify(
            self, guild_id: str, user_id: str, new_nick: str = None, new_roles: list = None,
            new_mute: bool = None, new_deaf: bool = None, new_channel_id: str = None) -> RequestsResponse:
        params = {}
        if new_nick is not None:
            params['nick'] = new_nick
        if new_roles is not None:
            params['roles'] = new_roles
        if new_mute is not None:
            params['mute'] = new_mute
        if new_deaf is not None:
            params['deaf'] = new_deaf
        if new_channel_id is not None:
            params['channel_id'] = new_channel_id
        return self.patch(f'{self.API_URL}/guilds/{guild_id}/members/{user_id}', json=params)

    def guild_member_me_nick_set(self, guild_id: str, nick_to_set: str) -> RequestsResponse:
        # IDEA: move to other me functions?
        return self.patch(f'{self.API_URL}/guilds/{guild_id}/members/@me/nick', json={'nick': nick_to_set})

    def guild_member_role_add(self, guild_id: str, user_id: str, role_id: str) -> RequestsResponse:
        return self.put(f'{self.API_URL}/guilds/{guild_id}/members/{user_id}/roles/{role_id}')

    def guild_member_role_remove(self, guild_id: str, user_id: str, role_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/guilds/{guild_id}/members/{user_id}/roles/{role_id}')

    def guild_member_remove(self, guild_id: str, user_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/guilds/{guild_id}/members/{user_id}')
    # endregion

    # region Guild Ban
    def guild_ban_list(self, guild_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/guilds/{guild_id}/bans')

    def guild_ban_create(self, guild_id: str, user_id: str, delete_messages_days=None) -> RequestsResponse:
        if delete_messages_days is not None:
            delete_messages_days = {'delete-message-days': delete_messages_days}
        return self.put(f'{self.API_URL}/guilds/{guild_id}/bans/{user_id}', params=delete_messages_days)

    def guild_ban_remove(self, guild_id: str, user_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/guilds/{guild_id}/bans/{user_id}')
    # endregion

    # region Guild Role
    def guild_role_list(self, guild_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/guilds/{guild_id}/roles')

    def guild_role_create(self, guild_id: str, name: str = None, permissions: int = None, color: int = None,
                          hoist: bool = None, mentionable: bool = None) -> RequestsResponse:
        params = {}
        if name is not None:
            params['name'] = name
        if permissions is not None:
            params['permissions'] = permissions
        if permissions is not None:
            params['color'] = color
        if permissions is not None:
            params['hoist'] = hoist
        if permissions is not None:
            params['mentionable'] = mentionable
        return self.post(f'{self.API_URL}/guilds/{guild_id}/roles', json=params or None)

    def guild_role_position_modify(
            self, guild_id: str,
            list_of_role_positions: typing.List[typing.Dict[str, int]]) -> RequestsResponse:
        return self.patch(f'{self.API_URL}/guilds/{guild_id}/roles', json=list_of_role_positions)

    def guild_role_modify(
            self, guild_id: str, role_id: str, new_name: str = None, new_permissions: int = None, new_color: int = None,
            new_hoist: bool = None, new_mentionable: bool = None):
        params = {}
        if new_name is not None:
            params['name'] = new_name
        if new_permissions is not None:
            params['permissions'] = new_permissions
        if new_color is not None:
            params['color'] = new_color
        if new_hoist is not None:
            params['hoist'] = new_hoist
        if new_mentionable is not None:
            params['mentionable'] = new_mentionable
        return self.patch(f'{self.API_URL}/guilds/{guild_id}/roles/{role_id}', json=params)

    def guild_role_delete(self, guild_id: str, role_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/guilds/{guild_id}/roles/{role_id}')
    # endregion

    def guild_prune_get_count(self, guild_id: str, days: int) -> RequestsResponse:
        return self.get(f'{self.API_URL}/guilds/{guild_id}/prune', params={'days': days})

    def guild_prune_begin(self, guild_id: str, days: int) -> RequestsResponse:
        return self.post(f'{self.API_URL}/guilds/{guild_id}/prune', params={'days': days})

    def guild_voice_region_list(self, guild_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/guilds/{guild_id}/regions')

    def guild_invite_list(self, guild_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/guilds/{guild_id}/invites')

    # NOTE: guild integration calls had not been tested.

    def guild_integration_list(self, guild_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/guilds/{guild_id}/integrations')

    def guild_integration_create(self, guild_id: str, integration_type: str, integration_id: str) -> RequestsResponse:
        return self.post(f'{self.API_URL}/guilds/{guild_id}/integrations', json={'type': integration_type,
                                                                                 'id': integration_id})

    def guild_integration_modify(self, guild_id: str, integration_id: str, expire_behavior: int,
                                 expire_grace_period: int, enable_emoticons: int) -> RequestsResponse:
        return self.patch(f'{self.API_URL}/guilds/{guild_id}/integrations/{integration_id}',
                          json={
                              'expire_behavior': expire_behavior,
                              'expire_grace_period': expire_grace_period,
                              'enable_emoticons': enable_emoticons
                          })

    def guild_integration_delete(self, guild_id: str, integration_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/guilds/{guild_id}/integrations/{integration_id}')

    def guild_integration_sync(self, guild_id: str, integration_id: str) -> RequestsResponse:
        return self.post(f'{self.API_URL}/guilds/{guild_id}/integrations/{integration_id}/sync')

    def guild_embed_get(self, guild_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/guilds/{guild_id}/embed')

    def guild_embed_modify(self, guild_id: str, enabled: bool = None, channel_id: str = None) -> RequestsResponse:
        params = {}
        if enabled is not None:
            params['enabled'] = enabled
        if channel_id is not None:
            params['channel_id'] = channel_id

        return self.patch(f'{self.API_URL}/guilds/{guild_id}/embed', json=params)

    # region Guild emoji
    def guild_emoji_list(self, guild_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/guilds/{guild_id}/emojis')

    def guild_emoji_get(self, guild_id: str, emoji_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/guilds/{guild_id}/emojis/{emoji_id}')

    def guild_emoji_create(self, guild_id: str, emoji_name: str, image: str, roles: tuple = ()) -> RequestsResponse:
        return self.post(f'{self.API_URL}/guilds/{guild_id}/emojis',
                         json={
                             'name': emoji_name,
                             'image': image,
                             'roles': roles
                         })

    def guild_emoji_modify(self, guild_id: str, emoji_id: str, emoji_name: str, roles: tuple = ()) -> RequestsResponse:
        return self.patch(f'{self.API_URL}/guilds/{guild_id}/emojis/{emoji_id}',
                          json={
                              'name': emoji_name,
                              'roles': roles
                          })

    def guild_emoji_delete(self, guild_id: str, emoji_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/guilds/{guild_id}/emojis/{emoji_id}')
    # endregion
    # endregion

    # region Channels REST API calls.

    def channel_get(self, channel_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/channels/{channel_id}')

    def channel_modify(
            self, channel_id: str, new_name: str = None, new_position: int = None, new_topic: str = None,
            new_nsfw: bool = None, new_bitrate: int = None, new_user_limit: int = None,
            new_overwrite_array: typing.List[dict] = None,
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
        return self.patch(f'{self.API_URL}/channels/{channel_id}', json=params)

    def channel_delete(self, channel_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/channels/{channel_id}')

    # region Messages
    def channel_message_list(self, channel_id: str, limit: int = None, around: str = None,
                             before: str = None, after: str = None) -> RequestsResponse:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if around is not None:
            params['around'] = around
        elif before is not None:
            params['before'] = before
        elif after is not None:
            params['after'] = after
        return self.get(f'{self.API_URL}/channels/{channel_id}/messages', params=params or None)

    def channel_message_get(self, channel_id: str, message_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/channels/{channel_id}/messages/{message_id}')

    def channel_message_create_json(self, channel_id: str, content: str, nonce: bool = None, tts: bool = None,
                                    embed: dict = None) -> RequestsResponse:
        params = {'content': content}
        if nonce is not None:
            params['nonce'] = nonce
        if tts is not None:
            params['tts'] = tts
        if embed is not None:
            params['embed'] = embed
        return self.post(f'{self.API_URL}/channels/{channel_id}/messages', json=params)

    def channel_message_create_multipart(self, channel_id: str, content: str = None,
                                         nonce: bool = None, tts: bool = None,
                                         files: list = None) -> RequestsResponse:
        params = {}
        if content is not None:
            params['content'] = content
        if nonce is not None:
            params['nonce'] = nonce
        if tts is not None:
            params['tts'] = tts
        return self.post(f'{self.API_URL}/channels/{channel_id}/messages', data=params or None, files=files or None)

    def channel_message_reaction_create(self, channel_id: str, message_id: str, emoji: str) -> RequestsResponse:
        return self.put(f'{self.API_URL}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me')

    def channel_message_reaction_my_delete(self, channel_id: str, message_id: str, emoji: int) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me')

    def channel_message_reaction_delete(self, channel_id: str, message_id: str, user_id: str,
                                        emoji: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}')

    def channel_message_reaction_list_users(self, channel_id: str, message_id: str, emoji: int, before: str = None,
                                            after: str = None, limit: int = None) -> RequestsResponse:
        params = {}
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        if limit is not None:
            params['limit'] = limit
        return self.get(f'{self.API_URL}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}',
                        params=params or None)

    def channel_message_reaction_delete_all(self, channel_id: str, message_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/channels/{channel_id}/messages/{message_id}/reactions')

    def channel_message_edit(self, channel_id: str, message_id: str, content: str = None,
                             embed: dict = None) -> RequestsResponse:
        params = {}
        if content is not None:
            params['content'] = content
        if embed is not None:
            params['embed'] = embed
        return self.patch(f'{self.API_URL}/channels/{channel_id}/messages/{message_id}',
                          json=params or None)

    def channel_message_delete(self, channel_id: str, message_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/channels/{channel_id}/messages/{message_id}')

    def channel_message_bulk_delete(self, channel_id: str, messages_array: list) -> RequestsResponse:
        return self.post(f'{self.API_URL}/channels/{channel_id}/messages/bulk-delete',
                         json={'messages': messages_array})
    # endregion

    def channel_permissions_overwrite_edit(self, channel_id: str, overwrite_id: str, allow_permissions: int,
                                           deny_permissions: int, type_of_permissions: str) -> RequestsResponse:
        return self.put(f'{self.API_URL}/channels/{channel_id}/permissions/{overwrite_id}',
                        json={'allow': allow_permissions, 'deny': deny_permissions, 'type': type_of_permissions})

    def channel_permissions_overwrite_delete(self, channel_id: str, overwrite_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/channels/{channel_id}/permissions/{overwrite_id}')

    def channel_invite_list(self, channel_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/channels/{channel_id}/invites')

    def channel_invite_create(self, channel_id: str, max_age: int = None, max_uses: int = None,
                              temporary_invite: bool = None, unique: bool = None) -> RequestsResponse:
        params = {}
        if max_age is not None:
            params['max_age'] = max_age
        if max_uses is not None:
            params['max_uses'] = max_uses
        if temporary_invite is not None:
            params['temporary'] = temporary_invite
        if unique is not None:
            params['unique'] = unique
        return self.post(f'{self.API_URL}/channels/{channel_id}/invites', json=params)

    def channel_typing_start(self, channel_id: str) -> RequestsResponse:
        return self.post(f'{self.API_URL}/channels/{channel_id}/typing')

    def channel_pins_get(self, channel_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/channels/{channel_id}/pins')

    def channel_pins_add(self, channel_id: str, message_id: str) -> RequestsResponse:
        return self.put(f'{self.API_URL}/channels/{channel_id}/pins/{message_id}')

    def channel_pins_delete(self, channel_id: str, message_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/channels/{channel_id}/pins/{message_id}')
    # endregion

    # region Invite REST API calls

    def invite_get(self, invite_code: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/invites/{invite_code}')

    def invite_delete(self, invite_code: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/invites/{invite_code}')

    def invite_accept(self, invite_code: str) -> RequestsResponse:
        return self.post(f'{self.API_URL}/invites/{invite_code}')
    # endregion

    # region Webhook REST API calls

    def webhook_create(self, channel_id: str, name: str, avatar: bytes = None) -> RequestsResponse:
        return self.post(f'{self.API_URL}/channels/{channel_id}/webhooks',
                         json={'name': name, 'avatar': avatar})

    def webhook_list_channel(self, channel_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/channels/{channel_id}/webhooks')

    def webhook_list_guild(self, guild_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/guilds/{guild_id}/webhooks')

    def webhook_get(self, webhook_id: str) -> RequestsResponse:
        return self.get(f'{self.API_URL}/webhooks/{webhook_id}')

    def webhook_token_get(self, webhook_id: str, webhook_token: int) -> RequestsResponse:
        return self.get(f'{self.API_URL}/webhooks/{webhook_id}/{webhook_token}')

    def webhook_modify(self, webhook_id: str, name: str = None, avatar: bytes = None,
                       channel_id: str = None) -> RequestsResponse:
        params = {}
        if name is not None:
            params['name'] = name
        if avatar is not None:
            params['avatar'] = avatar
        if channel_id is not None:
            params['channel_id'] = channel_id
        return self.patch(f'{self.API_URL}/webhooks/{webhook_id}', json=params)

    def webhook_token_modify(self, webhook_id: str, webhook_token: int, name: str = None, avatar: bytes = None,
                             channel_id: str = None) -> RequestsResponse:
        params = {}
        if name is not None:
            params['name'] = name
        if avatar is not None:
            params['avatar'] = avatar
        if channel_id is not None:
            params['channel_id'] = channel_id
        return self.patch(f'{self.API_URL}/webhooks/{webhook_id}/{webhook_token}', json=params)

    def webhook_delete(self, webhook_id: str) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/webhooks/{webhook_id}')

    def webhook_token_delete(self, webhook_id: str, webhook_token: int) -> RequestsResponse:
        return self.delete(f'{self.API_URL}/webhooks/{webhook_id}/{webhook_token}')

    def webhook_execute(self, webhook_id: str, webhook_token: int, content: str,
                        username: str = None, avatar_url: str = None, tts: bool = None,
                        wait_response: bool = None) -> RequestsResponse:
        # TODO: add support for uploading files and embeds
        json_params = {'content': content}
        if username is not None:
            json_params['username'] = username
        if avatar_url is not None:
            json_params['avatar_url'] = avatar_url
        if tts is not None:
            json_params['tts'] = tts
        if wait_response is not None:
            json_params['wait_response'] = wait_response

        return self.post(f'{self.API_URL}/webhooks/{webhook_id}/{webhook_token}', json=json_params)

    # TODO: slack and github webhooks
    # endregion

    # region Special calls

    def voice_region_list(self) -> RequestsResponse:
        return self.get(f'{self.API_URL}/voice/regions')

    def audit_log_get(self, guild_id: str, filter_user_id: str = None, filter_action_type: int = None,
                      filter_before_entry_id: str = None, limit: int = None) -> RequestsResponse:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if filter_user_id is not None:
            params['user_id'] = filter_user_id
        if filter_action_type is not None:
            params['action_type'] = filter_action_type
        if filter_before_entry_id is not None:
            params['before'] = filter_before_entry_id
        return self.get(f'{self.API_URL}/guilds/{guild_id}/audit-logs', params=params or None)

    def gateway_bot_get(self) -> RequestsResponse:
        return self.get(f'{self.API_URL}/gateway/bot')
    # endregion


def authorization_url_get(bot_id: str) -> str:
    return f'https://discordapp.com/api/oauth2/authorize?client_id={bot_id}&scope=bot&permissions=0'
