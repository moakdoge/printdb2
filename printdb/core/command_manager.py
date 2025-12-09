from . import command, context
from .command import Command,CommandDetails
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
    
    def run(self, cmd: str, *args):
        for command in self._commands:
            if command.command == cmd:
                command_context = context.CommandContext(command)
                command.run(command_context, *args)
                del command_context
