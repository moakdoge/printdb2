from . import command, context
from printdb.logging import traceback
from .command import Command,CommandDetails
from printdb.parsing import argparser
class CommandManager:

    def __init__(self):
        self._commands: list[Command] = []
        pass

    def register_command(self, command: Command):
        if command not in self._commands:
            self._commands.append(command)
    
    def command(self, name: str, author: str = ""):
        def decorator(func):
            cmd = Command(name,func,None,CommandDetails(author, func.__doc__))
            self.register_command(cmd)
            return func
        return decorator 
    
    def run(self, cmd: str, args):
        for command in self._commands:
            if command.command == cmd:
                command_context = context.CommandContext(command)
                args = argparser.type_check_args(command,args)
                try:
                    if args is not None:
                        command.run(command_context, *args)
                    else:
                        command.run(command_context, None)
                except Exception as e:
                    print(traceback.trace_error(e))
                del command_context
                return
    
    def get_command(self, cmd: str) -> Command:
        for command in self._commands:
            if command.command == cmd:
                return command
        return None