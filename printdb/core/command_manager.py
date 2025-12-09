from . import command, context, command_output
from printdb.logging import traceback
from .command_output import ErrorCode
from .command import Command,CommandDetails
from printdb.parsing import argparser
from .exceptions import *
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
    
    def run(self, cmd: str, args) -> command_output.CommandOutput:
        for command in self._commands:
            if command.command == cmd:
                command_context:context.CommandContext = context.CommandContext(cmd)
                try:
                    args = argparser.type_check_args(command,args)
                except InvalidParamType as e:
                    return command_output.CommandOutput(ErrorCode.INVALID_PARAM_TYPE, output=str(e))
                except MissingParam as e:
                    return command_output.CommandOutput(ErrorCode.MISSING_PARAM, output=str(e))

                try:
                    if args is not None:
                        return_value = command.run(command_context, *args)
                    else:
                        return_value = command.run(command_context, None)

                    if not isinstance(return_value, command_output.CommandOutput):
                        return command_output.CommandOutput(ErrorCode.SUCCESS, log=command_context.output.read())
                    else:
                        return_value.log = command_context.output.read()
                        return return_value
                except Exception as e:
                    traceback.trace_error(e)
        return command_output.CommandOutput(ErrorCode.COMMAND_NOT_FOUND, output="Command not found")
    
    def get_command(self, cmd: str) -> Command | None:
        for command in self._commands:
            if command.command == cmd:
                return command
        return None