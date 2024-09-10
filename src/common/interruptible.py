import asyncio


class Interruptible:
    def __init__(self):
        self._interrupt_event = asyncio.Event()

    def interrupt(self):
        self._interrupt_event.set()

    async def is_interrupted(self):
        return self._interrupt_event.is_set()

    async def check_interruption(self):
        if await self.is_interrupted():
            raise InterruptedError("process interrupted")
