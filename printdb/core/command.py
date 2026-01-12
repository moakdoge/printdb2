from dataclasses import dataclass, field
from . import context
from .args import Arg
from typing import Callable, Any
import inspect

@dataclass
class CommandFlags:
    debug : bool = False

@dataclass
class CommandDetails:
    author: str = ""
    description: str = ""
    args: list[Arg] = field(default_factory=list)

class Command:
    def __init__(self, command: str, func: Callable, flags: CommandFlags | None = None, details: CommandDetails | None = None):
        self.command = command
        self.name = command 
        self.func = func
        self.flags = flags if flags is not None else CommandFlags()
        self.details = details if details is not None else CommandDetails()
        self._parse_args()
    
    def _parse_args(self):
        sig = inspect.signature(self.func)

        for name, param in sig.parameters.items():
            if param.annotation == context.CommandContext:
                continue
            opt = (param.default != inspect._empty)
            defu = param.default if not param.default == inspect._empty else None
            self.details.args.append(Arg(name, param.annotation, defu, opt))

    async def run(self, context: context.CommandContext, *args):
        try:
            await self.func(context, *args)
        except KeyboardInterrupt:
            return

    #little bits of helper shit
    def __repr__(self):
        return f"<Command {self.name} ({self.func})>"