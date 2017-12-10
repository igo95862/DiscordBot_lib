from requests import Response as RequestsResponse
from requests import Session as RequestsSession


class DiscordSession(RequestsSession):

    def __init__(self, token: str):
        super(DiscordSession, self).__init__()
        self.headers.update({'Authorization': 'Bot ' + token})

    API_url = 'https://discordapp.com/api/v6'

    # User REST API calls

    def me_get(self) -> RequestsResponse:
        return self.get(f'{self.API_url}/users/@me')

    def user_get(self, user_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/users/{user_id}')

    def me_modify(self, username: str) -> RequestsResponse:
        # TODO: add avatar change support
        return self.patch(f'{self.API_url}/users/@me', json={'username': username})

    def me_guilds_get(self, before: int = None, after: int = None, limit: int = None) -> RequestsResponse:
        params = {}
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        if limit is not None:
            params['limit'] = limit
        return self.get(f'{self.API_url}/users/@me/guilds', params=params or None)

    def me_guild_leave(self, guild_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/users/@me/guilds/{guild_id}')

    def me_dm_get(self) -> RequestsResponse:
        return self.get(f'{self.API_url}/users/@me/channels')

    def me_dm_create(self, recipient_id: int) -> RequestsResponse:
        return self.post(f'{self.API_url}/users/@me/channels', json={'recipient_id': recipient_id})

    def me_dm_create_group(self, access_tokens: list, nicks: dict) -> RequestsResponse:
        # NOTE: Have not been tested.
        return self.post(f'{self.API_url}/users/@me/channels', json={'access_tokens': access_tokens, 'nicks': nicks})

    def me_connections_get(self) -> RequestsResponse:
        return self.get(f'{self.API_url}/users/@me/connections')

    # Guild REST API calls

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

        return self.post(f'{self.API_url}/guilds', json=json_params)

    def guild_get(self, guild_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/guilds/{guild_id}')

    def _guild_modify(self, guild_id: int, params: dict) -> RequestsResponse:
        return self.patch(f'{self.API_url}/guilds/{guild_id}', json=params)

    # Guild modify sub functions
    def guild_modify_name(self, guild_id: int, new_name: str) -> RequestsResponse:
        return self._guild_modify(guild_id, {'name': new_name})

    def guild_modify_region(self, guild_id: int, new_region: str) -> RequestsResponse:
        return self._guild_modify(guild_id, {'region': new_region})

    def guild_modify_verification_level(self, guild_id: int, new_level: int) -> RequestsResponse:
        return self._guild_modify(guild_id, {'verification_level': new_level})

    def guild_modify_default_notification_level(self, guild_id: int, new_level: int) -> RequestsResponse:
        return self._guild_modify(guild_id, {'default_message_notifications': new_level})

    def guild_modify_afk_channel_id(self, guild_id: int, new_afk_channel_id: int) -> RequestsResponse:
        return self._guild_modify(guild_id, {'afk_channel_id': new_afk_channel_id})

    def guild_modify_afk_timeout(self, guild_id: int, new_afk_timeout: int) -> RequestsResponse:
        return self._guild_modify(guild_id, {'afk_timeout': new_afk_timeout})

    def guild_modify_icon(self, guild_id: int, new_icon: str) -> RequestsResponse:
        return self._guild_modify(guild_id, {'icon': new_icon})

    def guild_modify_owner_id(self, guild_id: int, new_owner_id: int) -> RequestsResponse:
        return self._guild_modify(guild_id, {'owner_id': new_owner_id})

    def guild_modify_splash(self, guild_id: int, new_splash: str) -> RequestsResponse:
        return self._guild_modify(guild_id, {'splash': new_splash})

    def guild_modify_system_channel_id(self, guild_id: int, new_system_channel_id: int) -> RequestsResponse:
        return self._guild_modify(guild_id, {'system_channel_id': new_system_channel_id})

    def guild_delete(self, guild_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/guilds/{guild_id}')

    def guild_channels_get(self, guild_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/guilds/{guild_id}/channels')

    def _guild_channel_create(self, guild_id: int, params: dict) -> RequestsResponse:
        # NOTE: this function should not be called directly
        return self.post(f'{self.API_url}/guilds/{guild_id}/channels', json=params)

    def guild_channel_create_text(self, guild_id: int, name: str, permission_overwrites: dict = None,
                                  parent_id: int = None, nsfw: bool = None) -> RequestsResponse:
        new_channel_params = {'name': name, 'type': 0}
        if permission_overwrites is not None:
            new_channel_params['permission_overwrites'] = permission_overwrites
        if parent_id is not None:
            new_channel_params['parent_id'] = parent_id
        if nsfw is not None:
            new_channel_params['nsfw'] = nsfw

        return self._guild_channel_create(guild_id, new_channel_params)

    def guild_channel_create_voice(self, guild_id: int, name: str, permission_overwrites: dict = None,
                                   parent_id: int = None, nsfw: bool = None,
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

    def guild_channel_create_category(self, guild_id: int, name: str, permission_overwrites: dict = None,
                                      nsfw: bool = None) -> RequestsResponse:
        # NOTE: Category channels can't have parents. Not documented in API reference but was found experimentally
        new_channel_params = {'name': name, 'type': 4}
        if permission_overwrites is not None:
            new_channel_params['permission_overwrites'] = permission_overwrites
        if nsfw is not None:
            new_channel_params['nsfw'] = nsfw

        return self._guild_channel_create(guild_id, new_channel_params)

    def guild_channels_position_modify(self, guild_id: int, list_of_channels: list) -> RequestsResponse:
        # NOTE: This call requires list of dictionaries with with field of id of the channel and its position.
        # Position integers are independent of each other.
        # Multiple channels can have same position. There can be gaps between them.
        # Position integer can also be negative.
        # Unlike what documentation says you can pass a single channel to this call.
        return self.patch(f'{self.API_url}/guilds/{guild_id}/channels', json=list_of_channels)

    def guild_member_get(self, guild_id: int, user_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/guilds/{guild_id}/members/{user_id}')

    def guild_members_list(self, guild_id: int, limit: int = None, after: int = None) -> RequestsResponse:
        # NOTE: default amount of users returned is just one
        params = {}
        if limit is not None:
            params['limit'] = limit
        if after is not None:
            params['after'] = after
        return self.get(f'{self.API_url}/guilds/{guild_id}/members', params=params or None)

    def guild_member_add(self, guild_id: int, user_id: int, access_token: str, nick: str = None, roles: list = None,
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
        return self.put(f'{self.API_url}/guilds/{guild_id}/members/{user_id}', json=params)

    def _guild_member_modify(self, guild_id: int, user_id: int, params: dict) -> RequestsResponse:
        return self.patch(f'{self.API_url}/guilds/{guild_id}/members/{user_id}', json=params)

    # Guild member modify sub functions

    def guild_member_modify_nick(self, guild_id: int, user_id: int, nick_to_set: str) -> RequestsResponse:
        return self._guild_member_modify(guild_id, user_id, {'nick': nick_to_set})

    def guild_member_modify_roles(self, guild_id: int, user_id: int, roles: list) -> RequestsResponse:
        return self._guild_member_modify(guild_id, user_id, {'roles': roles})

    def guild_member_modify_mute(self, guild_id: int, user_id: int, mute_bool: bool) -> RequestsResponse:
        return self._guild_member_modify(guild_id, user_id, {'mute': mute_bool})

    def guild_member_modify_deaf(self, guild_id: int, user_id: int, deaf_bool: bool) -> RequestsResponse:
        return self._guild_member_modify(guild_id, user_id, {'deaf': deaf_bool})

    def guild_member_modify_move(self, guild_id: int, user_id: int, channel_move_to: int) -> RequestsResponse:
        return self._guild_member_modify(guild_id, user_id, {'channel_id': channel_move_to})

    def guild_member_me_nick_set(self, guild_id: int, nick_to_set: str) -> RequestsResponse:
        # IDEA: move to other me functions?
        return self.patch(f'{self.API_url}/guilds/{guild_id}/members/@me/nick', json={'nick': nick_to_set})

    def guild_member_role_add(self, guild_id: int, user_id: int, role_id: int) -> RequestsResponse:
        return self.put(f'{self.API_url}/guilds/{guild_id}/members/{user_id}/roles/{role_id}')

    def guild_member_role_remove(self, guild_id: int, user_id: int, role_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/guilds/{guild_id}/members/{user_id}/roles/{role_id}')

    def guild_member_remove(self, guild_id: int, user_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/guilds/{guild_id}/members/{user_id}')

    def guild_bans_get(self, guild_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/guilds/{guild_id}/bans')

    def guild_ban_create(self, guild_id: int, user_id: int, delete_messages_days=None) -> RequestsResponse:
        if delete_messages_days is not None:
            delete_messages_days = {'delete-message-days': delete_messages_days}
        return self.put(f'{self.API_url}/guilds/{guild_id}/bans/{user_id}', params=delete_messages_days)

    def guild_ban_remove(self, guild_id: int, user_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/guilds/{guild_id}/bans/{user_id}')

    def guild_roles_get(self, guild_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/guilds/{guild_id}/roles')

    def guild_role_create(self, guild_id: int, permissions: int = None, color: int = None,
                          hoist: bool = None, mentionable: bool = None) -> RequestsResponse:
        params = {}
        if permissions is not None:
            params['permissions'] = permissions
        if permissions is not None:
            params['color'] = color
        if permissions is not None:
            params['hoist'] = hoist
        if permissions is not None:
            params['mentionable'] = mentionable
        return self.post(f'{self.API_url}/guilds/{guild_id}/roles', json=params or None)

    def guild_role_position_modify(self, guild_id: int, list_of_role_positions: list) -> RequestsResponse:
        return self.patch(f'{self.API_url}/guilds/{guild_id}/roles', json=list_of_role_positions)

    # Guild Role modify sub-functions

    def _guild_role_modify(self, guild_id: int, role_id: int, params: dict) -> RequestsResponse:
        return self.patch(f'{self.API_url}/guilds/{guild_id}/roles/{role_id}', json=params)

    def guild_role_modify_name(self, guild_id: int, role_id: int, name: str) -> RequestsResponse:
        return self._guild_role_modify(guild_id, role_id, {'name': name})

    def guild_role_modify_permissions(self, guild_id: int, role_id: int, permissions: int) -> RequestsResponse:
        return self._guild_role_modify(guild_id, role_id, {'permissions': permissions})

    def guild_role_modify_color(self, guild_id: int, role_id: int, color: int) -> RequestsResponse:
        return self._guild_role_modify(guild_id, role_id, {'color': color})

    def guild_role_modify_hoist(self, guild_id: int, role_id: int, hoist: bool) -> RequestsResponse:
        return self._guild_role_modify(guild_id, role_id, {'hoist': hoist})

    def guild_role_modify_mentionable(self, guild_id: int, role_id: int, mentionable: bool) -> RequestsResponse:
        return self._guild_role_modify(guild_id, role_id, {'mentionable': mentionable})

    def guild_role_delete(self, guild_id: int, role_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/guilds/{guild_id}/roles/{role_id}')

    def guild_prune_get_count(self, guild_id: int, days: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/guilds/{guild_id}/prune', params={'days': days})

    def guild_prune_begin(self, guild_id: int, days: int) -> RequestsResponse:
        return self.post(f'{self.API_url}/guilds/{guild_id}/prune', params={'days': days})

    def guild_voice_regions_get(self, guild_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/guilds/{guild_id}/regions')

    def guild_invites_get(self, guild_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/guilds/{guild_id}/invites')

    # NOTE: guild integration calls had not been tested.

    def guild_integrations_get(self, guild_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/guilds/{guild_id}/integrations')

    def guild_integration_create(self, guild_id: int, integration_type: str, integration_id: int) -> RequestsResponse:
        return self.post(f'{self.API_url}/guilds/{guild_id}/integrations', json={'type': integration_type,
                                                                                 'id': integration_id})

    def guild_integration_modify(self, guild_id: int, integration_id: int, expire_behavior: int,
                                 expire_grace_period: int, enable_emoticons: int) -> RequestsResponse:
        return self.patch(f'{self.API_url}/guilds/{guild_id}/integrations/{integration_id}',
                          json={
                              'expire_behavior': expire_behavior,
                              'expire_grace_period': expire_grace_period,
                              'enable_emoticons': enable_emoticons
                          })

    def guild_integration_delete(self, guild_id: int, integration_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/guilds/{guild_id}/integrations/{integration_id}')

    def guild_integration_sync(self, guild_id: int, integration_id: int) -> RequestsResponse:
        return self.post(f'{self.API_url}/guilds/{guild_id}/integrations/{integration_id}/sync')

    def guild_embed_get(self, guild_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/guilds/{guild_id}/embed')

    def guild_embed_modify(self, guild_id: int, enabled: bool = None, channel_id: int = None) -> RequestsResponse:
        params = {}
        if enabled is not None:
            params['enabled'] = enabled
        if channel_id is not None:
            params['channel_id'] = channel_id

        return self.patch(f'{self.API_url}/guilds/{guild_id}/embed', json=params)

    # Guild emoji calls

    def guild_emoji_list(self, guild_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/guilds/{guild_id}/emojis')

    def guild_emoji_get(self, guild_id: int, emoji_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/guilds/{guild_id}/emojis/{emoji_id}')

    def guild_emoji_create(self, guild_id: int, emoji_name: str, image: str, roles: tuple = ()) -> RequestsResponse:
        return self.post(f'{self.API_url}/guilds/{guild_id}/emojis',
                         json={
                             'name': emoji_name,
                             'image': image,
                             'roles': roles
                         })

    def guild_emoji_modify(self, guild_id: int, emoji_id: int, emoji_name: str, roles: tuple = ()) -> RequestsResponse:
        return self.patch(f'{self.API_url}/guilds/{guild_id}/emojis/{emoji_id}',
                          json={
                              'name': emoji_name,
                              'roles': roles
                          })

    def guild_emoji_delete(self, guild_id: int, emoji_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/guilds/{guild_id}/emojis/{emoji_id}')

    # Channels REST API calls.

    def channel_get(self, channel_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/channels/{channel_id}')

    def _channel_modify(self, channel_id: int, params: dict) -> RequestsResponse:
        return self.patch(f'{self.API_url}/channels/{channel_id}', json=params)

    # Channel modify sub-functions

    def channel_modify_name(self, channel_id: int, name: str) -> RequestsResponse:
        return self._channel_modify(channel_id, {'name': name})

    def channel_modify_position(self, channel_id: int, position: int) -> RequestsResponse:
        return self._channel_modify(channel_id, {'position': position})

    def channel_modify_topic(self, channel_id: int, topic: str) -> RequestsResponse:
        return self._channel_modify(channel_id, {'topic': topic})

    def channel_modify_bitrate(self, channel_id: int, bitrate: int) -> RequestsResponse:
        return self._channel_modify(channel_id, {'bitrate': bitrate})

    def channel_modify_user_limit(self, channel_id: int, userlimit: int) -> RequestsResponse:
        return self._channel_modify(channel_id, {'userlimit': userlimit})

    def channel_modify_permission_overwrites(self, channel_id: int, overwrite_array: list) -> RequestsResponse:
        return self._channel_modify(channel_id, {'permission_overwrites': overwrite_array})

    def channel_modify_parent_id(self, channel_id: int, parent_id: int) -> RequestsResponse:
        return self._channel_modify(channel_id, {'parent_id': parent_id})

    def channel_delete(self, channel_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/channels/{channel_id}')

    def channel_messages_get(self, channel_id: int, limit: int = None, around: int = None,
                             before: int = None, after: int = None) -> RequestsResponse:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if around is not None:
            params['around'] = around
        elif before is not None:
            params['before'] = before
        elif after is not None:
            params['after'] = after
        return self.get(f'{self.API_url}/channels/{channel_id}/messages', params=params or None)

    def channel_message_get(self, channel_id: int, message_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/channels/{channel_id}/messages/{message_id}')

    def channel_message_create(self, channel_id: int, content: str, nonce: bool = None, tts: bool = None,
                               file: bytes = None, embed: dict = None) -> RequestsResponse:
        # TODO: check if files can be actually used. Fix if they can't.
        params = {'content': content}
        if nonce is not None:
            params['nonce'] = nonce
        if tts is not None:
            params['tts'] = tts
        if embed is not None:
            params['embed'] = embed
        return self.post(f'{self.API_url}/channels/{channel_id}/messages', files=file, json=params)

    def channel_message_reaction_create(self, channel_id: int, message_id: int, emoji: int) -> RequestsResponse:
        return self.put(f'{self.API_url}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me')

    def channel_message_reaction_my_delete(self, channel_id: int, message_id: int, emoji: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me')

    def channel_message_reaction_delete(self, channel_id: int, message_id: int, user_id: int,
                                        emoji: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}')

    def channel_message_reaction_get_users(self, channel_id: int, message_id: int, emoji: int, before: int = None,
                                           after: int = None, limit: int = None) -> RequestsResponse:
        params = {}
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        if limit is not None:
            params['limit'] = limit
        return self.get(f'{self.API_url}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}',
                        params=params or None)

    def channel_message_reaction_delete_all(self, channel_id: int, message_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/channels/{channel_id}/messages/{message_id}/reactions')

    def channel_message_edit(self, channel_id: int, message_id: int, content: str = None,
                             embed: dict = None) -> RequestsResponse:
        params = {}
        if content is not None:
            params['content'] = content
        if embed is not None:
            params['embed'] = embed
        return self.patch(f'{self.API_url}/channels/{channel_id}/messages/{message_id}',
                          json=params or None)

    def channel_message_delete(self, channel_id: int, message_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/channels/{channel_id}/messages/{message_id}')

    def channel_message_bulk_delete(self, channel_id: int, messages_array: list) -> RequestsResponse:
        return self.post(f'{self.API_url}/channels/{channel_id}/messages/bulk-delete',
                         json={'messages': messages_array})

    def channel_permissions_overwrite_edit(self, channel_id: int, overwrite_id: int, allow_permissions: int,
                                           deny_permissions: int, type_of_permissions: str) -> RequestsResponse:
        return self.put(f'{self.API_url}/channels/{channel_id}/permissions/{overwrite_id}',
                        json={'allow': allow_permissions, 'deny': deny_permissions, 'type': type_of_permissions})

    def channel_permissions_overwrite_delete(self, channel_id: int, overwrite_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/channels/{channel_id}/permissions/{overwrite_id}')

    def channel_invites_get(self, channel_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/channels/{channel_id}/invites')

    def channel_invite_create(self, channel_id: int, max_age: int = None, max_uses: int = None,
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
        return self.post(f'{self.API_url}/channels/{channel_id}/invites', json=params)

    def channel_typing_start(self, channel_id: int) -> RequestsResponse:
        return self.post(f'{self.API_url}/channels/{channel_id}/typing')

    def channel_pins_get(self, channel_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/channels/{channel_id}/pins')

    def channel_pins_add(self, channel_id: int, message_id: int) -> RequestsResponse:
        return self.put(f'{self.API_url}/channels/{channel_id}/pins/{message_id}')

    def channel_pins_delete(self, channel_id: int, message_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/channels/{channel_id}/pins/{message_id}')

    def dm_channel_user_add(self, channel_id: int, user_id: int, access_token: str, user_nick: str) -> RequestsResponse:
        return self.put(f'{self.API_url}/channels/{channel_id}/recipients/{user_id}',
                        json={'access_token': access_token, 'nick': user_nick})

    def dm_channel_user_remove(self, channel_id: int, user_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/channels/{channel_id}/recipients/{user_id}')

    # Invite REST API calls

    def invite_get(self, invite_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/invites/{invite_id}')

    def invite_delete(self, invite_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/invites/{invite_id}')

    def invite_accept(self, invite_id: int) -> RequestsResponse:
        return self.post(f'{self.API_url}/invites/{invite_id}')

    # Webhook REST API calls

    def webhook_create(self, channel_id: int, name: str, avatar: bytes = None) -> RequestsResponse:
        return self.post(f'{self.API_url}/channels/{channel_id}/webhooks',
                         json={'name': name, 'avatar': avatar})

    def webhook_get_channel(self, channel_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/channels/{channel_id}/webhooks')

    def webhook_guild_get(self, guild_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/channels/{guild_id}/webhooks')

    def webhook_get(self, webhook_id: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/webhooks/{webhook_id}')

    def webhook_token_get(self, webhook_id: int, webhook_token: int) -> RequestsResponse:
        return self.get(f'{self.API_url}/webhooks/{webhook_id}/{webhook_token}')

    def webhook_modify(self, webhook_id: int, name: str = None, avatar: bytes = None,
                       channel_id: int = None) -> RequestsResponse:
        params = {}
        if name is not None:
            params['name'] = name
        if avatar is not None:
            params['avatar'] = avatar
        if channel_id is not None:
            params['channel_id'] = channel_id
        return self.patch(f'{self.API_url}/webhooks/{webhook_id}', json=params)

    def webhook_token_modify(self, webhook_id: int, webhook_token: int, name: str = None, avatar: bytes = None,
                             channel_id: int = None) -> RequestsResponse:
        params = {}
        if name is not None:
            params['name'] = name
        if avatar is not None:
            params['avatar'] = avatar
        if channel_id is not None:
            params['channel_id'] = channel_id
        return self.patch(f'{self.API_url}/webhooks/{webhook_id}/{webhook_token}', json=params)

    def webhook_delete(self, webhook_id: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/webhooks/{webhook_id}')

    def webhook_token_delete_(self, webhook_id: int, webhook_token: int) -> RequestsResponse:
        return self.delete(f'{self.API_url}/webhooks/{webhook_id}/{webhook_token}')

    def webhook_execute(self, webhook_id: int, webhook_token: int, content: str,
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

        return self.post(f'{self.API_url}/webhooks/{webhook_id}/{webhook_token}', json=json_params)

    # TODO: slack and github webhooks

    # Special calls

    def voice_regions_get(self) -> RequestsResponse:
        return self.get(f'{self.API_url}/voice/regions')

    def audit_log_get(self, guild_id: int, filter_user_id: int = None, filter_action_type: int = None,
                      filter_before_entry_id: int = None, limit: int = None) -> RequestsResponse:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if filter_user_id is not None:
            params['user_id'] = filter_user_id
        if filter_action_type is not None:
            params['action_type'] = filter_action_type
        if filter_before_entry_id is not None:
            params['before'] = filter_before_entry_id
        return self.get(f'{self.API_url}/guilds/{guild_id}/audit-logs', params=params or None)

    def gateway_bot_get(self) -> RequestsResponse:
        return self.get(f'{self.API_url}/gateway/bot')


def authorization_url_get(bot_id: int) -> str:
    return 'https://discordapp.com/api/oauth2/authorize?client_id=' + str(bot_id) + '&scope=bot&permissions=0'
