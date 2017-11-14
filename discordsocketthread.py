import discordsocket
import asyncio
import threading

class DiscordWebsocketThread:

    def __init__(self, discord_websocket: discordsocket.DiscordWebsocket):
        self.discord_websocket = discord_websocket
        self.discord_websocket_loop = asyncio.new_event_loop()
        self.discord_websocket.event_loop = self.discord_websocket_loop

        self.thread = threading.Thread(target=self.discord_websocket_loop.run_forever)
        self.thread.start()

        connect_future = asyncio.run_coroutine_threadsafe(self.discord_websocket._connect(),
                                                          self.discord_websocket_loop)
        connect_future.result(timeout=5)

        identify_future = asyncio.run_coroutine_threadsafe(self.discord_websocket._identify(),
                                                           self.discord_websocket_loop)
        identify_future.result(timeout=5)

        self.hearbeat_future =  asyncio.run_coroutine_threadsafe(self.discord_websocket._heartbeat_cycle(),
                                                                 self.discord_websocket_loop)
        self.receive_future = asyncio.run_coroutine_threadsafe(self.discord_websocket._receive_cycle(),
                                                               self.discord_websocket_loop)

    def request_guild_members(self, guild_id: int, query: str = '', limit: int = 0):
        return asyncio.run_coroutine_threadsafe(self.discord_websocket.request_guild_members(guild_id, query, limit),
                                                self.discord_websocket_loop)
