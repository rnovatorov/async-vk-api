from contextlib import asynccontextmanager

import trio


class Throttler:

    def __init__(self, frequency):
        self.frequency = frequency
        # Using binary `trio.Semaphore` instead of `trio.Lock`
        # to be able to release it from the child task.
        self._semaphore = trio.Semaphore(1)

    @asynccontextmanager
    async def __call__(self):
        await self._semaphore.acquire()
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self._tick)
            yield

    @property
    def locked(self):
        return not self._semaphore.value

    @property
    def period(self):
        return 1 / self.frequency

    async def _tick(self):
        await trio.sleep(self.period)
        self._semaphore.release()
