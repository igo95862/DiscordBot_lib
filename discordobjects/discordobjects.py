from .discordclient import DiscordClient


class DiscordObject:
    """
    Basic class for all other discord objects
    """
    def __init__(self, client_bind: DiscordClient, snowflake: int):
        self.client_bind = client_bind
        self.snowflake = snowflake


class DiscordMe(DiscordObject):

    def __init__(self, token: str):
        new_client = DiscordClient(token)
        my_snowflake = new_client.me_get()['id']
        super().__init__(new_client, my_snowflake)

    def get_my_guilds(self):
        pass

    def get_my_dms(self):
        pass


class DiscordGuild(DiscordObject):

    def __init__(self, client_bind: DiscordClient, snowflake: int):
        super().__init__(client_bind, snowflake)


class DiscordChannel(DiscordObject):

    def __init__(self, client_bind: DiscordClient, snowflake):
        super().__init__(client_bind, snowflake)

    def post_message(self, content: str, force: bool = False):
        if not force:
            if len(content) > 2000:
                raise TypeError('Message lenght can\'t be more then 2000 symbols')

        new_message_dict = self.client_bind.channel_message_create(self.snowflake, content)
        return DiscordMessage.from_dict(new_message_dict, self.client_bind)

    @staticmethod
    def from_id(channel_id: int, client_bind: DiscordClient):
        channel_data = client_bind.channel_get(channel_id)
        return DiscordChannel(client_bind, channel_data['id'])


class DiscordMessage(DiscordObject):

    def __init__(self, client_bind: DiscordClient, snowflake: int, parent_channel_id: int):
        super().__init__(client_bind, snowflake)
        self.parent_channel_id = parent_channel_id

    def edit(self, new_content: str):
        self.client_bind.channel_message_edit(self.parent_channel_id, self.snowflake, new_content)

    def __del__(self):
        self.client_bind.channel_message_delete(self.parent_channel_id, self.snowflake)

    @staticmethod
    def from_dict(message_dict: dict, client_bind: DiscordClient):
        return DiscordMessage(client_bind, message_dict['id'], message_dict['channel_id'])


class DiscordUser(DiscordObject):

    def __init__(self, client_bind: DiscordClient, snowflake: int):
        super().__init__(client_bind, snowflake)
