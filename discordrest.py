import requests



class DiscordSession(requests.Session):

    def __init__(self, token: str):
        super(DiscordSession, self).__init__()
        self.headers.update({'Authorization': 'Bot ' + token})

    APIurl = 'https://discordapp.com/api/v6'

    # User REST API calls

    def user_current_get(self):
        return self.get(self.APIurl + '/users/@me')

    def user_get(self, user_id: int):
        return self.get(self.APIurl + '/users/' + str(user_id))

    def user_current_modify(self, username: str):
        return self.patch(self.APIurl + '/users/@me', json={'username': username})

    def user_current_guilds_get(self):
        return self.get(self.APIurl + '/users/@me/guilds')

    def user_current_guild_leave(self, guild_id: int):
        return self.delete(self.APIurl + '/users/@me/guilds/' + str(guild_id))

    def user_current_dm_get(self):
        return self.get(self.APIurl + '/users/@me/channels')

    def user_current_dm_create(self, recipient_id: int):
        return self.post(self.APIurl + '/users/@me/channels', json={'recipient_id': recipient_id})

    def user_current_dm_create_group(self, access_tokens, nicks):
        # NOTE: Have not been tested. Probably needs some code to check the sanity of passed parameters
        return self.post(self.APIurl + '/users/@me/channels', json={'access_tokens': access_tokens, 'nicks': nicks})

    def user_current_connections_get(self):
        return self.get(self.APIurl + '/users/@me/connections')

    # Guild REST API calls

    def guild_create(self, ):
        pass

    def guild_get(self, guild_id: int):
        return self.get(self.APIurl + '/guilds/' + str(guild_id))

    def guild_modify(self, guild_id: int, params: dict):
        # TODO: Does not check or provide interface to what is being changed. Probably to do later
        # IDEA: Have a separated function for modifying one thing
        return self.patch(self.APIurl + '/guilds/' + str(guild_id), json=params)

    def guild_delete(self, guild_id: int):
        return self.delete(self.APIurl + '/guilds/' + str(guild_id))

    def guild_channels_get(self, guild_id: int):
        return self.get(self.APIurl + '/guilds/' + str(guild_id) + '/channels')

    def guild_channel_create(self, guild_id: int, params: dict ):
        return self.post(self.APIurl + '/guilds/' + str(guild_id) + '/channels', json=params)

    def guild_channel_create_text(self, guild_id: int, name: str, permission_overwrites: dict = None):
        params = {'name': name, 'type': 'text'}
        if permission_overwrites is not None: params['permission_overwrites'] = permission_overwrites
        return self.guild_channel_create(guild_id, {'name': name, })

    def guild_channel_create_voice(self):
        pass  # TODO: create voice channel function

    def guild_channels_position_modify(self, guild_id: int, channel_id: int, position: int):
        # NOTE: Test if this call accepts multiple channels
        return self.patch(self.APIurl + '/guilds/' + str(guild_id) + '/channels', json={'id': channel_id,
                                                                                        'position': position})

    def guild_member_get(self, guild_id: int, user_id: int):
        return self.get(self.APIurl + '/guilds/' + str(guild_id) + '/members/' + str(user_id))

    def guild_members_list(self, guild_id: int, limit: int = None, after: int = None):
        params = {}
        if limit is not None: params['limit'] = limit
        if after is not None: params['after'] = after
        return self.get(self.APIurl + '/guilds/' + str(guild_id) + '/members', json=params or None)

    def guild_member_add(self):
        # TODO: Add guild member function. Probably after O2Auth gets implemented.
        raise NotImplemented

    def guild_member_modify(self, guild_id: int, user_id: int, params: dict):
        return self.patch(self.APIurl + '/guilds/' + str(guild_id) + '/members/' + str(user_id), json=params)

    def guild_member_modify_nick(self, guild_id: int, user_id: int, nick_to_set: str):
        return self.guild_member_modify(guild_id=guild_id, user_id=user_id, params={'nick': nick_to_set})

    def guild_member_modify_roles(self, guild_id: int, user_id: int, roles: list):
        return self.guild_member_modify(guild_id=guild_id, user_id=user_id, params={'roles': roles})

    def guild_member_modify_mute(self, guild_id: int, user_id: int, mute_bool: bool):
        return self.guild_member_modify(guild_id=guild_id, user_id=user_id, params={'mute': mute_bool})




    def patchEditMessage(self, channelId, messageId, content=None, embed=None):
        json_params = {}
        if content: json_params['content'] = content
        if embed: json_params['embed'] = embed
        return self.patch(self.APIurl + '/channels/' + str(channelId) + '/messages/' + str(messageId), json=json_params)

    def getGatewayBot(self):
        return self.get(self.APIurl + '/gateway/bot')



def makeAuthorizationURL(id):
    return 'https://discordapp.com/api/oauth2/authorize?client_id=' + str(id) + '&scope=bot&permissions=0'