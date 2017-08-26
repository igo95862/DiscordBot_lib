import requests


class DiscordSession(requests.Session):

    def __init__(self, token: str):
        super(DiscordSession, self).__init__()
        self.headers.update({'Authorization': 'Bot ' + token})

    API_url = 'https://discordapp.com/api/v6'

    # User REST API calls

    def user_me_get(self):
        return self.get(self.API_url + '/users/@me')

    def user_get(self, user_id: int):
        return self.get(self.API_url + '/users/' + str(user_id))

    def user_me_modify(self, username: str):
        return self.patch(self.API_url + '/users/@me', json={'username': username})

    def user_me_guilds_get(self):
        return self.get(self.API_url + '/users/@me/guilds')

    def user_me_guild_leave(self, guild_id: int):
        return self.delete(self.API_url + '/users/@me/guilds/' + str(guild_id))

    def user_me_dm_get(self):
        return self.get(self.API_url + '/users/@me/channels')

    def user_me_dm_create(self, recipient_id: int):
        return self.post(self.API_url + '/users/@me/channels', json={'recipient_id': recipient_id})

    def user_me_dm_create_group(self, access_tokens, nicks):
        # NOTE: Have not been tested. Probably needs some code to check the sanity of passed parameters
        return self.post(self.API_url + '/users/@me/channels', json={'access_tokens': access_tokens, 'nicks': nicks})

    def user_me_connections_get(self):
        return self.get(self.API_url + '/users/@me/connections')

    # Guild REST API calls

    def guild_create(self, ):
        # TODO: implement guild create REST API call
        raise NotImplementedError

    def guild_get(self, guild_id: int):
        return self.get(self.API_url + '/guilds/' + str(guild_id))

    def guild_modify(self, guild_id: int, params: dict):
        # TODO: Does not check or provide interface to what is being changed. Probably to do later
        # IDEA: Have a separated function for modifying one thing
        return self.patch(self.API_url + '/guilds/' + str(guild_id), json=params)

    def guild_delete(self, guild_id: int):
        return self.delete(self.API_url + '/guilds/' + str(guild_id))

    def guild_channels_get(self, guild_id: int):
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/channels')

    def guild_channel_create(self, guild_id: int, params: dict):
        return self.post(self.API_url + '/guilds/' + str(guild_id) + '/channels', json=params)

    def guild_channel_create_text(self, guild_id: int, name: str, permission_overwrites: dict = None):
        params = {'name': name, 'type': 'text'}
        if permission_overwrites is not None:
            params['permission_overwrites'] = permission_overwrites
        return self.guild_channel_create(guild_id, {'name': name, })

    def guild_channel_create_voice(self):
        pass  # TODO: create voice channel function

    def guild_channels_position_modify(self, guild_id: int, channel_id: int, position: int):
        # NOTE: Test if this call accepts multiple channels
        return self.patch(self.API_url + '/guilds/' + str(guild_id) + '/channels', json={'id': channel_id,
                                                                                        'position': position})

    def guild_member_get(self, guild_id: int, user_id: int):
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/members/' + str(user_id))

    def guild_members_list(self, guild_id: int, limit: int = None, after: int = None):
        params = {}
        if limit is not None:
            params['limit'] = limit
        if after is not None:
            params['after'] = after
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/members', json=params or None)

    def guild_member_add(self):
        # TODO: Add guild member function. Probably after O2Auth gets implemented.
        raise NotImplementedError

    def guild_member_modify(self, guild_id: int, user_id: int, params: dict):
        return self.patch(self.API_url + '/guilds/' + str(guild_id) + '/members/' + str(user_id), json=params)

    def guild_member_modify_nick(self, guild_id: int, user_id: int, nick_to_set: str):
        return self.guild_member_modify(guild_id=guild_id, user_id=user_id, params={'nick': nick_to_set})

    def guild_member_modify_roles(self, guild_id: int, user_id: int, roles: list):
        return self.guild_member_modify(guild_id=guild_id, user_id=user_id, params={'roles': roles})

    def guild_member_modify_mute(self, guild_id: int, user_id: int, mute_bool: bool):
        return self.guild_member_modify(guild_id=guild_id, user_id=user_id, params={'mute': mute_bool})

    def guild_member_modify_deaf(self, guild_id: int, user_id: int, deaf_bool: bool):
        return self.guild_member_modify(guild_id=guild_id, user_id=user_id, params={'deaf': deaf_bool})

    def guild_member_modify_move(self, guild_id: int, user_id: int, channel_move_to: int):
        return self.guild_member_modify(guild_id=guild_id, user_id=user_id, params={'channel_id': channel_move_to})

    def guild_member_me_nick_set(self, guild_id: int, nick_to_set: str):
        return self.patch(self.API_url + '/guilds/' + str(guild_id) + '/members/@me/nick', json={'nick': nick_to_set})

    def guild_member_role_add(self, guild_id: int, user_id: int, role_id: int):
        return self.put(self.API_url + '/guilds/' + str(guild_id) + '/members/' + str(user_id) + '/roles/' + str(role_id))

    def guild_member_role_remove(self, guild_id: int, user_id: int, role_id: int):
        return self.delete(self.API_url + '/guilds/' + str(guild_id) + '/members/' + str(user_id) + '/roles/' + str(role_id))

    def guild_member_remove(self, guild_id: int, user_id: int):
        return self.delete(self.API_url + '/guilds/' + str(guild_id) + '/members/' + str(user_id))

    def guild_bans_get(self, guild_id: int):
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/bans')

    def guild_ban_create(self, guild_id: int, user_id: int, delete_messages_days=None):
        if delete_messages_days is not None:
            delete_messages_days = {'delete-message-days': delete_messages_days}
        return self.put(self.API_url + '/guilds/' + str(guild_id) + '/bans/' + str(user_id), json=delete_messages_days)

    def guild_ban_remove(self, guild_id: int, user_id: int):
        return self.delete(self.API_url + '/guilds/' + str(guild_id) + '/bans/' + str(user_id))

    def guild_roles_get(self, guild_id: int):
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/roles')

    def guild_role_create(self, guild_id: int, permissions: int = None, color: int = None,
                          hoist: bool = None, mentionable: bool = None):
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

    def guild_role_position_modify(self, guild_id: int, role_id: int, position: int):
        return self.patch(self.API_url + '/guilds/' + str(guild_id) + '/roles', json={'id': role_id,
                                                                                      'position': position})

    def guild_role_modify(self, guild_id: int, role_id: int, params: dict):
        return self.patch(self.API_url + '/guilds/' + str(guild_id) + '/roles/' + str(role_id), json=params)

    def guild_role_modify_name(self, guild_id: int, role_id: int, name: str):
        return self.guild_role_modify(guild_id=guild_id, role_id=role_id, params={'name': name})

    def guild_role_modify_permissions(self, guild_id: int, role_id: int, permissions: int):
        return self.guild_role_modify(guild_id=guild_id, role_id=role_id, params={'permissions': permissions})

    def guild_role_modify_color(self, guild_id: int, role_id: int, color: int):
        return self.guild_role_modify(guild_id=guild_id, role_id=role_id, params={'color': color})

    def guild_role_modify_hoist(self, guild_id: int, role_id: int, hoist: bool):
        return self.guild_role_modify(guild_id=guild_id, role_id=role_id, params={'hoist': hoist})

    def guild_role_modify_mentionable(self, guild_id: int, role_id: int, mentionable: bool):
        return self.guild_role_modify(guild_id=guild_id, role_id=role_id, params={'mentionable': mentionable})

    def guild_role_delete(self, guild_id: int, role_id: int):
        return self.delete(self.API_url + '/guilds/' + str(guild_id) + '/roles/' + str(role_id))

    def guild_prune_get_count(self, guild_id: int, days: int):
        if not days > 1:
            raise TypeError('Days argument should be larger then 1.')
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/prune', json={'days': days})

    def guild_prune_begin(self, guild_id: int, days: int):
        if not days > 1:
            raise TypeError('Days argument should be larger then 1.')
        return self.post(self.API_url + '/guilds/' + str(guild_id) + '/prune', json={'days': days})

    def guild_voice_regions_get(self, guild_id: int):
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/regions')

    def guild_invites_get(self, guild_id: int):
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/invites')

    # TODO: guild integration calls. Probably after I figure out what they are
    # TODO: guild embeded calls

    # Channels REST API calls.

    def channel_get(self, channel_id: int):
        return self.get(self.API_url + '/channels/' + str(channel_id))

    def channel_modify(self, channel_id: int, params: dict):
        return self.patch(self.API_url + '/channels/' + str(channel_id), json=params)

    def channel_modify_name(self, channel_id: int, name: str):
        return self.channel_modify(channel_id=channel_id, params={'name': name})

    def channel_modify_position(self, channel_id: int, position: int):
        return self.channel_modify(channel_id=channel_id, params={'position': position})

    def channel_modify_topic(self, channel_id: int, topic: str):
        return self.channel_modify(channel_id=channel_id, params={'topic': topic})

    def channel_modify_bitrate(self, channel_id: int, bitrate: int):
        return self.channel_modify(channel_id=channel_id, params={'bitrate': bitrate})

    def channel_modify_userlimit(self, channel_id: int, userlimit: int):
        return self.channel_modify(channel_id=channel_id, params={'userlimit': userlimit})

    def channel_delete(self, channel_id: int):
        return self.delete(self.API_url + '/channels/' + str(channel_id))

    def channel_messages_get(self, channel_id: int, limit: int = None, around: int = None,
                             before: int = None, after: int = None):
        params = {}
        if limit is not None:
            params['limit'] = limit
        if around is not None:
            params['around'] = around
        elif before is not None:
            params['before'] = before
        elif after is not None:
            params['after'] = after
        return self.get(self.API_url + '/channels/' + str(channel_id) + '/messages', json=params or None)

    def channel_message_get(self, channel_id: int, message_id: int):
        return self.get(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id))

    def channel_message_create(self, channel_id: int, content: str, nonce: bool = None, tts: bool = None,
                               file: bytes = None, embed: dict = None):
        if len(content) > 2000:
            raise TypeError('Message length cannot exceed 2000 characters.')
        params = {'content': content}
        if nonce is not None:
            params['nonce'] = nonce
        if tts is not None:
            params['tts'] = tts
        if embed is not None:
            params['embed'] = embed
        return self.post(self.API_url + '/channels/' + str(channel_id) + '/messages', files=file, json=params)

    def channel_message_reaction_create(self, channel_id: int, message_id: int, emoji_id: int):
        return self.put(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id) + '/reactions/'
                        + str(emoji_id) + '/@me')

    def channel_message_reaction_my_delete(self, channel_id: int, message_id: int, emoji_id: int):
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id)
                           + '/reactions/' + str(emoji_id) + '/@me')

    def channel_message_reaction_delete(self, channel_id: int, message_id: int, user_id: int, emoji_id: int):
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id)
                           + '/reactions/' + str(emoji_id) + '/' + str(user_id))

    def channel_message_reaction_get_users(self, channel_id: int, message_id: int, emoji_id: int):
        return self.get(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id) + '/reactions/'
                        + str(emoji_id))

    def channel_message_reaction_delete_all(self, channel_id: int, message_id: int):
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id)
                           + '/reactions')

    def channel_message_edit(self, channel_id: int, message_id: int, content: str=None, embed: dict=None):
        if len(content) > 2000:
            raise TypeError('Message length cannot exceed 2000 characters.')
        params = {}
        if content is not None:
            if len(content) > 2000:
                raise TypeError('Message length cannot exceed 2000 characters.')
            params['content'] = content
        if embed:
            params['embed'] = embed
        return self.patch(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id), json=params or None)

    def channel_message_delete(self, channel_id: int, message_id: int):
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/messages/' + str(message_id))

    def channel_message_bulk_delete(self, channel_id: int, messages_array: list):
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/messages/bulk-delete',
                           json={'messages': messages_array})

    def channel_permissions_overwrite_edit(self, channel_id: int, overwrite_id: int, allow_permissions: int,
                                           deny_permissions: int, type_of_permissions: str):
        if type_of_permissions is not 'member' or type_of_permissions is not 'role':
            raise TypeError('Permission type must be "member" for users or "role" for roles')
        return self.put(self.API_url + '/channels/' + str(channel_id) + '/permissions/' + str(overwrite_id),
                        json={'allow': allow_permissions, 'deny': deny_permissions, 'type': type_of_permissions})

    def channel_permissions_overwrite_delete(self, channel_id: int, overwrite_id: int):
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/permissions/' + str(overwrite_id))

    def channel_invites_get(self, channel_id: int):
        return self.get(self.API_url + '/channels/' + str(channel_id) + '/invites')

    def channel_invite_create(self, channel_id: int, max_age: int = None, max_uses: int = None,
                              temporary_invite: bool = None, unique: bool = None):
        params={}
        if max_age is not None:
            params['max_age'] = max_age
        if max_uses is not None:
            params['max_uses'] = max_uses
        if temporary_invite is not None:
            params['temporary'] = temporary_invite
        if unique is not None:
            params['unique'] = unique
        return self.post(self.API_url + '/channels/' + str(channel_id) + '/invites', json=params)

    def channel_typing_start(self, channel_id: int):
        return self.post(self.API_url + '/channels/' + str(channel_id) + '/typing')

    def channel_pins_get(self, channel_id: int):
        return self.get(self.API_url + '/channels/' + str(channel_id) + '/pins')

    def channel_pins_add(self, channel_id: int, message_id: int):
        return self.put(self.API_url + '/channels/' + str(channel_id) + '/pins/' + str(message_id))

    def channel_pins_delete(self, channel_id: int, message_id: int):
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/pins/' + str(message_id))

    def dm_channel_user_add(self, channel_id: int, user_id: int, access_token: str, user_nick: str):
        return self.put(self.API_url + '/channels/' + str(channel_id) + '/recipients/' + str(user_id),
                        json={'access_token': access_token, 'nick': user_nick})

    def dm_channel_user_remove(self, channel_id: int, user_id: int):
        return self.delete(self.API_url + '/channels/' + str(channel_id) + '/recipients/' + str(user_id))

    # Invite REST API calls

    def invite_get(self, invite_id: int):
        return self.get(self.API_url + '/invites/' + str(invite_id))

    def invite_delete(self, invite_id: int):
        return self.delete(self.API_url + '/invites/' + str(invite_id))

    def invite_accept(self, invite_id: int):
        return self.post(self.API_url + '/invites/' + str(invite_id))


    def getGatewayBot(self):
        return self.get(self.API_url + '/gateway/bot')



def makeAuthorizationURL(bot_id):
    return 'https://discordapp.com/api/oauth2/authorize?client_id=' + str(bot_id) + '&scope=bot&permissions=0'
