import discordsocket
import asyncio
import threading


class DiscordSocketThread:

    def __init__(self, discord_websocket: discordsocket.DiscordSocket):
        self.discord_socket = discord_websocket
        self.discord_socket_loop = asyncio.new_event_loop()
        self.discord_socket.event_loop = self.discord_socket_loop

        self.thread = threading.Thread(target=self.discord_socket_loop.run_forever)
        self.thread.start()

        connect_future = asyncio.run_coroutine_threadsafe(self.discord_socket._connect(),
                                                          self.discord_socket_loop)
        connect_future.result(timeout=5)

        identify_future = asyncio.run_coroutine_threadsafe(self.discord_socket._identify(),
                                                           self.discord_socket_loop)
        identify_future.result(timeout=5)

        self.heartbeat_future = asyncio.run_coroutine_threadsafe(self.discord_socket._heartbeat_cycle(),
                                                                 self.discord_socket_loop)
        self.receive_future = asyncio.run_coroutine_threadsafe(self.discord_socket._receive_cycle(),
                                                               self.discord_socket_loop)

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
                                                                                       mute_self, deaf_self))