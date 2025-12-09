import inspect
from printdb.core.command import Command
from typing import Any

def extract_args(command: Command):

    sig = inspect.signature(command.func)
    params = list(sig.parameters.values())[1:]
    return params

def type_check_args(command: Command, args: list) -> list[Any]:
    a = extract_args(command)
    for arg in args:
        print(arg)