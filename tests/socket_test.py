import unittest
from discordobjects import discordsocket
import asyncio


class SocketInitTest(unittest.TestCase):

    def setUp(self):
        self.event_loop = asyncio.get_event_loop()
        token_file = open('./token')
        self.token = token_file.read()
        token_file.close()
        self.discord_socket = discordsocket.DiscordSocket(self.token)

    def test_initialising_socket(self):
        self.event_loop.run_until_complete(self.discord_socket.init())
        self.assertIsNotNone(self.discord_socket.session_id, 'Session id was caught.')


if __name__ == '__main__':
    unittest.main()
