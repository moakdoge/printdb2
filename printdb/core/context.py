from typing import Any
from printdb.logging import sink, prettyify
class CommandContext:
    def __init__(self, command: str):
        self.output = sink.LogSink()
        self.input = sink.LogSink()
        pass
    def pprint(self, content: Any):
        self.output += f"{prettyify.prettyify(content)}\n"
    def print(self, content: Any, end:str = "\n"):
        self.output += f"{content}{end}"