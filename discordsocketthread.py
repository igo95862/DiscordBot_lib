import discordsocket
import asyncio
import threading
from functools import partial as func_partial


class DiscordSocketThread:

    def __init__(self, *args):

        if type(args[0]) is str:
            # NOTE: check that the string has proper length and etc.?
            self.discord_socket_loop = asyncio.new_event_loop()
            self.discord_socket = discordsocket.DiscordSocket(args[0], event_loop=self.discord_socket_loop)
        elif type(args[0]) is discordsocket.DiscordSocket:
            self.discord_socket = args[0]
            self.discord_socket.event_loop = self.discord_socket_loop
        else:
            raise TypeError('Neither token nor socket was passed to socket.')

        self.discord_socket_loop.create_task(self.discord_socket.init())

        self.thread = threading.Thread(target=self.discord_socket_loop.run_forever)
        self.thread.start()

    def request_guild_members(self, guild_id: int, query: str = '', limit: int = 0):
        return asyncio.run_coroutine_threadsafe(self.discord_socket.request_guild_members(guild_id, query, limit),
                                                self.discord_socket_loop)

    def status_update(self, status_type: str, is_afk: bool,
                      game: dict = None, since_time_seconds: int = None):
        return asyncio.run_coroutine_threadsafe(self.discord_socket.status_update(status_type, is_afk,
                                                                                  game, since_time_seconds),
                                                self.discord_socket_loop)

    def voice_state_update(self, guild_id: int, channel_id: int = None,
                           mute_self: bool = None, deaf_self: bool = False):
        return asyncio.run_coroutine_threadsafe(self.discord_socket.voice_state_update(guild_id, channel_id,
                                                                                       mute_self, deaf_self),
                                                self.discord_socket_loop)

    def event_hook_add(self, coroutine):
        self.discord_socket_loop.call_soon_threadsafe(func_partial(self.discord_socket.event_hooks.append, coroutine))


