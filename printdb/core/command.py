from dataclasses import dataclass, field
from . import context
from typing import Callable, Any

@dataclass
class CommandFlags:
    debug : bool = False

@dataclass
class CommandDetails:
    author: str = ""
    description: str = ""
    args: list[str] = field(default_factory=list)

class Command:
    def __init__(self, command: str, func: Callable, flags: CommandFlags = None, details: CommandDetails = None):
        self.command = command
        self.func = func
        self.flags = flags if flags is not None else CommandFlags()
        self.details = details if details is not None else CommandDetails()

    def run(self, context: context.CommandContext, *args):
        self.func(context, *args)

    #little bits of helper shit
    def __repr__(self):
        return f"<Command {self.command} ({self.func})>"