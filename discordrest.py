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
        raise NotImplemented

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

    def guild_channel_create(self, guild_id: int, params: dict ):
        return self.post(self.API_url + '/guilds/' + str(guild_id) + '/channels', json=params)

    def guild_channel_create_text(self, guild_id: int, name: str, permission_overwrites: dict = None):
        params = {'name': name, 'type': 'text'}
        if permission_overwrites is not None: params['permission_overwrites'] = permission_overwrites
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
        raise NotImplemented

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

    def guild_member_kick(self, guild_id: int, user_id: int):
        return self.delete(self.API_url + '/guilds/' + str(guild_id) + '/members/' + str(user_id))

    def guild_bans_get(self, guild_id: int):
        return self.get(self.API_url + '/guilds/' + str(guild_id) + '/bans')

    def guild_ban_create(self, guild_id: int, user_id: int, delete_messages_days=None):
        if delete_messages_days is not None:
            delete_messages_days = {'delete-message-days': delete_messages_days}
        return self.put(self.API_url + '/guilds/' + str(guild_id) + '/bans/' + str(user_id), json=delete_messages_days)

    def guild_ban_remove(self, guild_id: int, user_id: int):
        return self.delete(self.API_url + '/guilds/' + str(guild_id) + '/bans/' + str(user_id))


    def patchEditMessage(self, channelId, messageId, content=None, embed=None):
        json_params = {}
        if content: json_params['content'] = content
        if embed: json_params['embed'] = embed
        return self.patch(self.API_url + '/channels/' + str(channelId) + '/messages/' + str(messageId), json=json_params)

    def getGatewayBot(self):
        return self.get(self.API_url + '/gateway/bot')



def makeAuthorizationURL(id):
    return 'https://discordapp.com/api/oauth2/authorize?client_id=' + str(id) + '&scope=bot&permissions=0'