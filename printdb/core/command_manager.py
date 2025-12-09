import importlib.util
from types import ModuleType
from . import command, context, command_output
from printdb.logging import traceback
from .command_output import ErrorCode
from .command import Command,CommandDetails
from printdb.parsing import argparser, tokenizer
from .exceptions import *
import os
class CommandManager:

    def __init__(self):
        self._commands: list[Command] = []
        self._loaded_plugins: list[ModuleType] = []
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
    
    def load_plugin(self, path):
        spec = importlib.util.spec_from_file_location("plugin_" + path, path)
        module = importlib.util.module_from_spec(spec) # type: ignore
        spec.loader.exec_module(module) # type: ignore
        self._loaded_plugins.append(module)
        return module
    
    def get_commands(self) -> list[Command]:
        return self._commands
    
    def load_plugin_folder(self, path: str):
        if not os.path.exists(path):
            raise OSError(f"Can't find plugin folder {path}!")
            return
        for dirpath, dirnames, filenames in os.walk(path):
            for file in filenames:
                if os.path.splitext(file)[1] == ".py":
                    self.load_plugin(os.path.join(dirpath, file))


    def run(self, cmd: str) -> command_output.CommandOutput:
        #tokenize into pipes and redirects
        redirects = tokenizer.tokensize_redirects(cmd)
        pass

    def _run(self, cmd: str, args) -> command_output.CommandOutput:
        '''
            DO NOT CALL! call the normal run instead, unless you are a plugin trying to run a command manually.
        '''
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