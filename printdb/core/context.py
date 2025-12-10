from typing import Any
from printdb.logging import sink, prettyify
class CommandContext:
    def __init__(self, command: str, inp: sink.LogSink | None =None):
        self.output = sink.LogSink()
        self.input = inp if inp is not None else sink.LogSink()
        pass
    async def pprint(self, content: Any):
        await self.output.write(f"{prettyify.prettyify(content)}\n")
    async def print(self, content: Any, end:str = "\n"):
        await self.output.write(f"{content}{end}")
