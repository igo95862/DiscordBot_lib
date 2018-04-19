import asyncio
import typing
from _functools import partial as f_partial
from concurrent.futures import ThreadPoolExecutor
# IDEA: use multiprocess executor in the future?
from json import JSONDecodeError
from time import time

from requests import Response
from requests.exceptions import ConnectTimeout, ReadTimeout, ConnectionError


class RateLimitSimple:

    def __init__(self, loop: asyncio.AbstractEventLoop = None, retry_period: int = 4):
        self.executor = ThreadPoolExecutor(1, 'rate_limit_single_queue thread executor')
        self.retry_period = retry_period
        self.rate_limit_table = {'global': (-1, 0)}
        if loop is None:
            self.event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        else:
            self.event_loop: asyncio.AbstractEventLoop = loop
        self.lock: asyncio.Lock = asyncio.Lock(loop=self.event_loop)

    async def __call__(self, api_call_partial: f_partial,
                       table_position: tuple = None) -> typing.Union[dict, list, bool]:
        if table_position is None:
            table_position = api_call_partial.func
            # NOTE: defaults to rate limit look up by function

        response_data: dict = None

        await self.lock.acquire()

        try:
            while response_data is None:

                try:
                    remaining_limit = self.rate_limit_table[table_position][0]
                except KeyError:
                    self.rate_limit_table[table_position] = None
                    remaining_limit = -1

                if remaining_limit == 0:
                    sleep_time = self.rate_limit_table[table_position][1] - time()
                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time, loop=self.event_loop)
                        continue

                try:
                    response: Response = await self.event_loop.run_in_executor(self.executor, api_call_partial)
                except ConnectTimeout:
                    await asyncio.sleep(self.retry_period)
                    continue
                except ReadTimeout:
                    await asyncio.sleep(self.retry_period)
                    continue
                except ConnectionError:
                    await asyncio.sleep(self.retry_period)
                    continue

                if 'X-RateLimit-Remaining' in response.headers:
                    self.rate_limit_table[table_position] = (
                        int(response.headers['X-RateLimit-Remaining']),
                        int(response.headers['X-RateLimit-Reset']))
                else:
                    self.rate_limit_table[table_position] = (-1, 0)

                if response.status_code == 500 or response.status_code == 502:
                    # Discord servers are wonky
                    continue
                elif response.status_code >= 400:
                    # You made a bad request or something went wrong. Raise exception.
                    response.raise_for_status()

                try:
                    response_data = response.json()
                except JSONDecodeError:
                    response_data = True
        finally:
            self.lock.release()

        return response_data
