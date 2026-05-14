import asyncio
import os

IDLE = object()
class LogSink:
    def __init__(self, terminal=False):
        self._queue = asyncio.Queue()
        self._closed = False
        self._copy_queue: list[str] = []
        self._file = None
        self._terminal = terminal  # TerminalSink or None

    # ----------------------------
    #   Write to pipe
    # ----------------------------
    async def write(self, data: str):

        await self._queue.put(data)
        self._copy_queue.append(data)
        if self._file is not None:
            self._file.write(data)
            self._file.flush()
        elif self._terminal is True:
            print(data,end="")



    async def read_chunks(self):
        while True:
            item = await self._queue.get()
            if item != IDLE:
                yield item 
            if item == IDLE:
                break


    async def read(self) -> str:
        if self._closed and self._queue.empty():
            return ""
        return await self._queue.get()


    def redirect_file(self, path: str, append=False):
        mode = "a" if append else "w"
        self._file = open(path, mode)

    def close(self):
        self._closed = True
        self._queue.put_nowait(IDLE)  # unblock waiting consumers
