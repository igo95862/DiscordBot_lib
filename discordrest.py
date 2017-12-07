import requests

class DiscordSession(requests.Session):

    def __init__(self, token: str):
        super(DiscordSession, self).__init__()
        self.headers.update({'Authorization': 'Bot ' + token})

    API_url = 'https://discordapp.com/api/v6'

    # User REST API calls

    def me_get(self)->requests.Response:
        return self.get(self.API_url + '/users/@me')

    def user_get(self, user_id: int)->requests.Response:
        return self.get(self.API_url + '/users/' + str(user_id))

    def me_modify(self, username: str)->requests.Response:
        # TODO: add avatar change support
        return self.patch(self.API_url + '/users/@me', json={'username': username})

    def me_guilds_get(self, before: int = None, after: int = None, limit: int = None)->requests.Response:
        params = {}
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        if limit is not None:
            params['limit'] = limit
        return self.get(self.API_url + '/users/@me/guilds', params=params or None)

    def me_guild_leave(self, guild_id: int)->requests.Response:
        return self.delete(self.API_url + '/users/@me/guilds/' + str(guild_id))

    def me_dm_get(self)->requests.Response:
        return self.get(self.API_url + '/users/@me/channels')

    def me_dm_create(self, recipient_id: int)->requests.Response:
        return self.post(self.API_url + '/users/@me/channels', json={'recipient_id': recipient_id})

    def me_dm_create_group(self, access_tokens: list, nicks: dict)->requests.Response:
        # NOTE: Have not been tested.
        return self.post(self.API_url + '/users/@me/channels', json={'access_tokens': access_tokens, 'nicks': nicks})

    def me_connections_get(self)->requests.Response:
        return self.get(self.API_url + '/users/@me/connections')

    # Guild REST API calls

    def guild_create(self, guild_name: str, region: str = None, icon: str = None, verification_level: int = None
                     , default_message_notifications: int = None, roles=None, channels=None)->requests.Response:
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

        return self.post(self.API_url + '/guilds', json=json_params)

    def guild_get(self, guild_id: int)->requests.Response:
        return self.get(self.API_url + '/guilds/' + str(guild_id))

    def _guild_modify(self, guild_id: int, params: dict)->requests.Response:
        return self.patch(self.API_url + '/guilds/' + str(guild_id), json=params)

    # Guild modify sub functions
    def guild_modify_name(self, guild_id: int, new_name: str)->requests.Response:
        return self._guild_modify(guild_id=guild_id, params={'name': new_name})

    def guild_modify_region(self, guild_id: int, new_region:str)->requests.Response:
        return self._guild_modify(guild_id=guild_id, params={'region': new_region})

    def guild_modify_verification_level(self, guild_id: int, new_level: int)->requests.Response:
        return self._guild_modify(guild_id=guild_id, params={'verification_level': new_level})

    def guild_modify_default_notification_level(self, guild_id: int, new_level: int)->requests.Response:
        return self._guild_modify(guild_id=guild_id, params={'default_message_notifications': new_level})

    def guild_modify_afk_channel_id(self, guild_id: int, new_afk_channel_id: int)->requests.Response:
        return self._guild_modify(guild_id=guild_id, params={'afk_channel_id': new_afk_channel_id})

    def guild_modify_afk_timeout(self, guild_id: int, new_afk_timeout: int)->requests.Response:
        return self._guild_modify(guild_id=guild_id, params={'afk_timeout': new_afk_timeout})

    def guild_modify_icon(self, guild_id: int, new_icon: str)->requests.Response:
        return self._guild_modify(guild_id=guild_id, params={'icon': new_icon})

    def guild_modify_owner_id(self, guild_id: int, new_owner_id: int)->requests.Response:
        return self._guild_modify(guild_id=guild_id, params={'owner_id': new_owner_id})

    def guild_modify_splash(self, guild_id: int, new_splash: str)->requests.Response:
        return self._guild_modify(guild_id=guild_id, params={'splash': new_splash})

    def guild_modify_system_channel_id(self, guild_id: int, new_system_channel_id: int)->requests.Response:
        return self._guild_modify(guild_id=guild_id, params={'system_channel_id': new_system_channel_id})

    def guild_delete(self, guild_id: int)->requests.Response:
        return self.delete(self.API_url + '/guilds/' + str(guild_id))

    def guild_channels_get(self, guild_id: int)->requests.Response:
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/channels')

    def _guild_channel_create(self, guild_id: int, params: dict)->requests.Response:
        # NOTE: this function should not be called directly
        return self.post(self.API_url + '/guilds/' + str(guild_id) + '/channels', json=params)

    def guild_channel_create_text(self, guild_id: int, name: str, permission_overwrites: dict = None,
                                  parent_id: int = None, nsfw: bool = None)->requests.Response:
        new_channel_params = {'name': name, 'type': 0}
        if permission_overwrites is not None:
            new_channel_params['permission_overwrites'] = permission_overwrites
        if parent_id is not None:
            new_channel_params['parent_id'] = parent_id
        if nsfw is not None:
            new_channel_params['nsfw'] = nsfw

        return self._guild_channel_create(guild_id=guild_id, params=new_channel_params)

    def guild_channel_create_voice(self, guild_id: int, name: str, permission_overwrites: dict = None,
                                   parent_id: int = None, nsfw: bool = None,
                                   bitrate: int = None, user_limit: int = None)->requests.Response:
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

        return self._guild_channel_create(guild_id=guild_id, params=new_channel_params)

    def guild_channel_create_category(self, guild_id: int, name: str, permission_overwrites: dict = None,
                                      nsfw: bool = None)->requests.Response:
        # NOTE: Category channels can't have parents. Not documented in API reference but was found experimentally
        new_channel_params = {'name': name, 'type': 4}
        if permission_overwrites is not None:
            new_channel_params['permission_overwrites'] = permission_overwrites
        if nsfw is not None:
            new_channel_params['nsfw'] = nsfw

        return self._guild_channel_create(guild_id=guild_id, params=new_channel_params)

    def guild_channels_position_modify(self, guild_id: int, list_of_channels: list)->requests.Response:
        # NOTE: This call requires list of dictionaries with with field of id of the channel and its position.
        # Position integers are independent of each other.
        # Multiple channels can have same position. There can be gaps between them.
        # Position integer can also be negative.
        # Unlike what documentation says you can pass a single channel to this call.
        return self.patch(self.API_url + '/guilds/' + str(guild_id) + '/channels', json=list_of_channels)

    def guild_member_get(self, guild_id: int, user_id: int)->requests.Response:
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/members/' + str(user_id))

    def guild_members_list(self, guild_id: int, limit: int = None, after: int = None)->requests.Response:
        # NOTE: default amount of users returned is just one
        params = {}
        if limit is not None:
            params['limit'] = limit
        if after is not None:
            params['after'] = after
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/members', params=params or None)

    def guild_member_add(self, guild_id: int, user_id: int,access_token: str, nick: str = None, roles: list = None,
                         mute: bool = None, deaf: bool = None)->requests.Response:
        params = {'access_token': access_token}
        if nick is not None:
            params['nick'] = nick
        if roles is not None:
            params['roles'] = roles
        if mute is not None:
            params['mute'] = mute
        if deaf is not None:
            params['deaf'] = deaf
        return self.put(self.API_url + '/guilds/' + str(guild_id) + '/members/' + str(user_id), json=params)

    def _guild_member_modify(self, guild_id: int, user_id: int, params: dict)->requests.Response:
        return self.patch(self.API_url + '/guilds/' + str(guild_id) + '/members/' + str(user_id), json=params)

    def guild_member_modify_nick(self, guild_id: int, user_id: int, nick_to_set: str)->requests.Response:
        return self._guild_member_modify(guild_id=guild_id, user_id=user_id, params={'nick': nick_to_set})

    def guild_member_modify_roles(self, guild_id: int, user_id: int, roles: list)->requests.Response:
        return self._guild_member_modify(guild_id=guild_id, user_id=user_id, params={'roles': roles})

    def guild_member_modify_mute(self, guild_id: int, user_id: int, mute_bool: bool)->requests.Response:
        return self._guild_member_modify(guild_id=guild_id, user_id=user_id, params={'mute': mute_bool})

    def guild_member_modify_deaf(self, guild_id: int, user_id: int, deaf_bool: bool)->requests.Response:
        return self._guild_member_modify(guild_id=guild_id, user_id=user_id, params={'deaf': deaf_bool})

    def guild_member_modify_move(self, guild_id: int, user_id: int, channel_move_to: int)->requests.Response:
        return self._guild_member_modify(guild_id=guild_id, user_id=user_id, params={'channel_id': channel_move_to})

    def guild_member_me_nick_set(self, guild_id: int, nick_to_set: str)->requests.Response:
        # IDEA: move to other me functions?
        return self.patch(self.API_url + '/guilds/' + str(guild_id) + '/members/@me/nick', json={'nick': nick_to_set})

    def guild_member_role_add(self, guild_id: int, user_id: int, role_id: int)->requests.Response:
        return self.put(self.API_url + '/guilds/' + str(guild_id) + '/members/'
                        + str(user_id) + '/roles/' + str(role_id))

    def guild_member_role_remove(self, guild_id: int, user_id: int, role_id: int)->requests.Response:
        return self.delete(self.API_url + '/guilds/' + str(guild_id) + '/members/'
                           + str(user_id) + '/roles/' + str(role_id))

    def guild_member_remove(self, guild_id: int, user_id: int)->requests.Response:
        return self.delete(self.API_url + '/guilds/' + str(guild_id) + '/members/' + str(user_id))

    def guild_bans_get(self, guild_id: int)->requests.Response:
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/bans')

    def guild_ban_create(self, guild_id: int, user_id: int, delete_messages_days=None)->requests.Response:
        if delete_messages_days is not None:
            delete_messages_days = {'delete-message-days': delete_messages_days}
        return self.put(self.API_url + '/guilds/' + str(guild_id) + '/bans/'
                        + str(user_id), params=delete_messages_days)

    def guild_ban_remove(self, guild_id: int, user_id: int)->requests.Response:
        return self.delete(self.API_url + '/guilds/' + str(guild_id) + '/bans/' + str(user_id))

    def guild_roles_get(self, guild_id: int)->requests.Response:
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/roles')

    def guild_role_create(self, guild_id: int, permissions: int = None, color: int = None,
                          hoist: bool = None, mentionable: bool = None)->requests.Response:
        paramas = {}
        if permissions is not None:
            paramas['permissions'] = permissions
        if permissions is not None:
            paramas['color'] = color
        if permissions is not None:
            paramas['hoist'] = hoist
        if permissions is not None:
            paramas['mentionable'] = mentionable
        return self.post(self.API_url + '/guilds/' + str(guild_id) + '/roles', json=paramas or None)

    def guild_role_position_modify(self, guild_id: int, list_of_role_positions: list)->requests.Response:
        return self.patch(self.API_url + '/guilds/' + str(guild_id) + '/roles', json=list_of_role_positions)

    def _guild_role_modify(self, guild_id: int, role_id: int, params: dict)->requests.Response:
        return self.patch(self.API_url + '/guilds/' + str(guild_id) + '/roles/' + str(role_id), json=params)

    def guild_role_modify_name(self, guild_id: int, role_id: int, name: str)->requests.Response:
        return self._guild_role_modify(guild_id=guild_id, role_id=role_id, params={'name': name})

    def guild_role_modify_permissions(self, guild_id: int, role_id: int, permissions: int)->requests.Response:
        return self._guild_role_modify(guild_id=guild_id, role_id=role_id, params={'permissions': permissions})

    def guild_role_modify_color(self, guild_id: int, role_id: int, color: int)->requests.Response:
        return self._guild_role_modify(guild_id=guild_id, role_id=role_id, params={'color': color})

    def guild_role_modify_hoist(self, guild_id: int, role_id: int, hoist: bool)->requests.Response:
        return self._guild_role_modify(guild_id=guild_id, role_id=role_id, params={'hoist': hoist})

    def guild_role_modify_mentionable(self, guild_id: int, role_id: int, mentionable: bool)->requests.Response:
        return self._guild_role_modify(guild_id=guild_id, role_id=role_id, params={'mentionable': mentionable})

    def guild_role_delete(self, guild_id: int, role_id: int)->requests.Response:
        return self.delete(self.API_url + '/guilds/' + str(guild_id) + '/roles/' + str(role_id))

    def guild_prune_get_count(self, guild_id: int, days: int)->requests.Response:
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/prune', params={'days': days})

    def guild_prune_begin(self, guild_id: int, days: int)->requests.Response:
        return self.post(self.API_url + '/guilds/' + str(guild_id) + '/prune', params={'days': days})

    def guild_voice_regions_get(self, guild_id: int)->requests.Response:
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/regions')

    def guild_invites_get(self, guild_id: int)->requests.Response:
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/invites')

    # NOTE: guild integration calls had not been tested.

    def guild_integrations_get(self, guild_id: int)->requests.Response:
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/integrations')

    def guild_integration_create(self, guild_id: int, integration_type: str, integration_id: int)->requests.Response:
        return self.post(self.API_url + '/guilds/' + str(guild_id) + '/integrations', json={'type': integration_type,
                                                                                            'id': integration_id})

    def guild_integration_modify(self, guild_id: int, integration_id: int, expire_behavior: int,
                                 expire_grace_period: int, enable_emoticons: int)->requests.Response:
        return self.patch(self.API_url + '/guilds/' + str(guild_id) + '/integrations/' + str(integration_id),
                          json={
                              'expire_behavior': expire_behavior,
                              'expire_grace_period': expire_grace_period,
                              'enable_emoticons': enable_emoticons
                          })

    def guild_integration_delete(self, guild_id: int, integration_id: int):
        return self.delete(self.API_url + '/guilds/' + str(guild_id) + '/integrations/' + str(integration_id))

    def guild_integration_sync(self, guild_id: int, integration_id: int):
        return self.post(self.API_url + '/guilds/' + str(guild_id) + '/integrations/' + str(integration_id) + '/sync')

    def guild_embed_get(self, guild_id: int):
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/embed')

    def guild_embed_modify(self, guild_id: int, enabled: bool = None, channel_id: int = None):
        params = {}
        if enabled is not None:
            params['enabled'] = enabled
        if channel_id is not None:
            params['channel_id'] = channel_id

        return self.patch(self.API_url + '/guilds/' + str(guild_id) + '/embed', json=params)

    # Channels REST API calls.

    def channel_get(self, channel_id: int)->requests.Response:
        return self.get(self.API_url + '/channels/' + str(channel_id))

    def _channel_modify(self, channel_id: int, params: dict)->requests.Response:
        return self.patch(self.API_url + '/channels/' + str(channel_id), json=params)

    def channel_modify_name(self, channel_id: int, name: str)->requests.Response:
        return self._channel_modify(channel_id=channel_id, params={'name': name})

    def channel_modify_position(self, channel_id: int, position: int)->requests.Response:
        return self._channel_modify(channel_id=channel_id, params={'position': position})

    def channel_modify_topic(self, channel_id: int, topic: str)->requests.Response:
        return self._channel_modify(channel_id=channel_id, params={'topic': topic})

    def channel_modify_bitrate(self, channel_id: int, bitrate: int)->requests.Response:
        return self._channel_modify(channel_id=channel_id, params={'bitrate': bitrate})

    def channel_modify_user_limit(self, channel_id: int, userlimit: int)->requests.Response:
        return self._channel_modify(channel_id=channel_id, params={'userlimit': userlimit})

    def channel_modify_permission_overwrites(self, channel_id: int, overwrite_array: list):
        return self._channel_modify(channel_id=channel_id, params={'permission_overwrites': overwrite_array})

    def channel_modify_parent_id(self, channel_id: int, parent_id: int):
        return self._channel_modify(channel_id=channel_id, params={'parent_id': parent_id})

    def channel_delete(self, channel_id: int)->requests.Response:
        return self.delete(self.API_url + '/channels/' + str(channel_id))

    def channel_messages_get(self, channel_id: int, limit: int = None, around: int = None,
                             before: int = None, after: int = None)->requests.Response:
        params = {}
        if limit is not None:
            params['limit'] = limit
        if around is not None:
            params['around'] = around
        elif before is not None:
            params['before'] = before
        elif after is not None:
            params['after'] = after
        return self.get(self.API_url + '/channels/' + str(channel_id) + '/messages', params=params or None)

    def channel_message_get(self, channel_id: int, message_id: int)->requests.Response:
        return self.get(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id))

    def channel_message_create(self, channel_id: int, content: str, nonce: bool = None, tts: bool = None,
                               file: bytes = None, embed: dict = None)->requests.Response:
        # TODO: check if files can be actually used. Fix if they can't.
        params = {'content': content}
        if nonce is not None:
            params['nonce'] = nonce
        if tts is not None:
            params['tts'] = tts
        if embed is not None:
            params['embed'] = embed
        return self.post(self.API_url + '/channels/' + str(channel_id) + '/messages', files=file, json=params)

    def channel_message_reaction_create(self, channel_id: int, message_id: int, emoji: int)->requests.Response:
        return self.put(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id) + '/reactions/'
                        + str(emoji) + '/@me')

    def channel_message_reaction_my_delete(self, channel_id: int, message_id: int, emoji: int)->requests.Response:
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id)
                           + '/reactions/' + str(emoji) + '/@me')

    def channel_message_reaction_delete(self, channel_id: int, message_id: int, user_id: int, emoji: int)->requests.Response:
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id)
                           + '/reactions/' + str(emoji) + '/' + str(user_id))

    def channel_message_reaction_get_users(self, channel_id: int, message_id: int, emoji: int, before: int = None,
                                           after: int = None, limit: int = None)->requests.Response:
        params={}
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        if limit is not None:
            params['limit'] = limit
        return self.get(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id) + '/reactions/'
                        + str(emoji), params=params or None)

    def channel_message_reaction_delete_all(self, channel_id: int, message_id: int)->requests.Response:
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id)
                           + '/reactions')

    def channel_message_edit(self, channel_id: int, message_id: int, content: str=None, embed: dict=None)->requests.Response:
        params = {}
        if content is not None:
            params['content'] = content
        if embed is not None:
            params['embed'] = embed
        return self.patch(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id),
                          json=params or None)

    def channel_message_delete(self, channel_id: int, message_id: int)->requests.Response:
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id))

    def channel_message_bulk_delete(self, channel_id: int, messages_array: list)->requests.Response:
        return self.post(self.API_url + '/channels/' + str(channel_id) + '/messages/bulk-delete',
                         json={'messages': messages_array})

    def channel_permissions_overwrite_edit(self, channel_id: int, overwrite_id: int, allow_permissions: int,
                                           deny_permissions: int, type_of_permissions: str)->requests.Response:
        return self.put(self.API_url + '/channels/' + str(channel_id) + '/permissions/' + str(overwrite_id),
                        json={'allow': allow_permissions, 'deny': deny_permissions, 'type': type_of_permissions})

    def channel_permissions_overwrite_delete(self, channel_id: int, overwrite_id: int)->requests.Response:
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/permissions/' + str(overwrite_id))

    def channel_invites_get(self, channel_id: int)->requests.Response:
        return self.get(self.API_url + '/channels/' + str(channel_id) + '/invites')

    def channel_invite_create(self, channel_id: int, max_age: int = None, max_uses: int = None,
                              temporary_invite: bool = None, unique: bool = None)->requests.Response:
        params = {}
        if max_age is not None:
            params['max_age'] = max_age
        if max_uses is not None:
            params['max_uses'] = max_uses
        if temporary_invite is not None:
            params['temporary'] = temporary_invite
        if unique is not None:
            params['unique'] = unique
        return self.post(self.API_url + '/channels/' + str(channel_id) + '/invites', json=params)

    def channel_typing_start(self, channel_id: int)->requests.Response:
        return self.post(self.API_url + '/channels/' + str(channel_id) + '/typing')

    def channel_pins_get(self, channel_id: int)->requests.Response:
        return self.get(self.API_url + '/channels/' + str(channel_id) + '/pins')

    def channel_pins_add(self, channel_id: int, message_id: int)->requests.Response:
        return self.put(self.API_url + '/channels/' + str(channel_id) + '/pins/' + str(message_id))

    def channel_pins_delete(self, channel_id: int, message_id: int)->requests.Response:
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/pins/' + str(message_id))

    def dm_channel_user_add(self, channel_id: int, user_id: int, access_token: str, user_nick: str)->requests.Response:
        return self.put(self.API_url + '/channels/' + str(channel_id) + '/recipients/' + str(user_id),
                        json={'access_token': access_token, 'nick': user_nick})

    def dm_channel_user_remove(self, channel_id: int, user_id: int)->requests.Response:
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/recipients/' + str(user_id))

    # Invite REST API calls

    def invite_get(self, invite_id: int)->requests.Response:
        return self.get(self.API_url + '/invites/' + str(invite_id))

    def invite_delete(self, invite_id: int)->requests.Response:
        return self.delete(self.API_url + '/invites/' + str(invite_id))

    def invite_accept(self, invite_id: int)->requests.Response:
        return self.post(self.API_url + '/invites/' + str(invite_id))

    # Webhook REST API calls

    def webhook_create(self, channel_id: int, name: str, avatar: bytes = None)->requests.Response:
        return self.post(self.API_url + '/channels/' + str(channel_id) + '/webhooks',
                         json={'name': name, 'avatar': avatar})

    def webhook_get_channel(self, channel_id: int)->requests.Response:
        return self.get(self.API_url + '/channels/' + str(channel_id) + '/webhooks')

    def webhook_get_guild(self, guild_id: int)->requests.Response:
        return self.get(self.API_url + '/channels/' + str(guild_id) + '/webhooks')

    def webhook_get(self, webhook_id: int)->requests.Response:
        return self.get(self.API_url + '/webhooks/' + str(webhook_id))

    def webhook_token_get(self, webhook_id: int, webhook_token: int)->requests.Response:
        return self.get(self.API_url + '/webhooks/' + str(webhook_id) + '/' + str(webhook_token))

    def webhook_modify(self, webhook_id: int, name: str = None, avatar: bytes = None)->requests.Response:
        params = {}
        if name is not None:
            params['name'] = name
        if avatar is not None:
            params['avatar'] = avatar
        return self.patch(self.API_url + '/webhooks/' + str(webhook_id), json=params)

    def webhook_token_modify(self, webhook_id: int, webhook_token: int, name: str = None, avatar: bytes = None)->requests.Response:
        params = {}
        if name is not None:
            params['name'] = name
        if avatar is not None:
            params['avatar'] = avatar
        return self.patch(self.API_url + '/webhooks/' + str(webhook_id) + '/' + str(webhook_token), json=params)

    def webhook_delete(self, webhook_id: int)->requests.Response:
        return self.delete(self.API_url + '/webhooks/' + str(webhook_id))

    def webhook_token_delete_(self, webhook_id: int, webhook_token: int)->requests.Response:
        return self.delete(self.API_url + '/webhooks/' + str(webhook_id) + '/' + str(webhook_token))

    def webhook_execute(self, webhook_id: int, webhook_token: int)->requests.Response:
        pass

    # Special calls

    def voice_regions_get(self)->requests.Response:
        return self.get(self.API_url + '/voice/regions')

    def audit_log_get(self, guild_id: int, filter_user_id: int = None, filter_action_type: int = None,
                      filter_before_entry_id: int = None, limit: int = None)->requests.Response:
        params = {}
        if limit is not None:
            if 1 <= limit <= 100:
                params['limit'] = limit
            else:
                raise TypeError('Number of returned entries must be between 1 and 100')
        if filter_user_id is not None:
            params['user_id'] = filter_user_id
        if filter_action_type is not None:
            params['action_type'] = filter_action_type
        if filter_before_entry_id is not None:
            params['before'] = filter_before_entry_id
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/audit-logs', json=params or None)

    def gateway_bot_get(self)->requests.Response:
        return self.get(self.API_url + '/gateway/bot')


def authorization_url_get(bot_id: int)->str:
    return 'https://discordapp.com/api/oauth2/authorize?client_id=' + str(bot_id) + '&scope=bot&permissions=0'
