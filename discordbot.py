import discordrest
import discordsocketthread
import time
import functools


class DiscordBot:

    def __init__(self, token: str):
        self.discord_session = discordrest.DiscordSession(token=token)
        self.rate_limit_table = {}

    def rate_limiter_test(self, func_partial: functools.partial):
        func = func_partial.func

        try:
            remaining_limit = self.rate_limit_table[func][0]
        except KeyError:
            self.rate_limit_table[func] = None
            remaining_limit = -1

        if remaining_limit == 0:
            sleep_time = self.rate_limit_table[func][1] - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)

        response = func_partial()

        self.rate_limit_table[func] = (int(response.headers['X-RateLimit-Remaining']),
                                       int(response.headers['X-RateLimit-Reset']))

        return response
