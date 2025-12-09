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
        newcmd,mode,file = tokenizer.tokensize_redirects(cmd)
        pipes = tokenizer.tokenize_pipes(cmd)

        out = None
        m = len(pipes) - 1
        for i, cmd in enumerate(pipes):
            is_at_end = (i >= m)
            if mode is not None and file is not None:
                c, args = tokenizer.tokenize_args(newcmd)
                out= self._run(c, args, redirect_file=file, redirect_mode=mode, input=out, mask_input=not is_at_end)
            else:
                c, args = tokenizer.tokenize_args(cmd)
                out= self._run(c, args, input=out,mask_input=not is_at_end)
        return out
        pass

    def _run(self, cmd: str, args, redirect_file = None, redirect_mode = None, input=None, mask_input = False) -> command_output.CommandOutput:
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


                if redirect_file is not None and redirect_mode is not None:
                    if redirect_mode == "a" and not os.path.exists(redirect_file):
                        return command_output.CommandOutput(ErrorCode.FILE_NOT_FOUND, output=f"Redirect file of '{redirect_file}' does not exist and you are in append mode!")
                    command_context.output.redirect_file(redirect_file, append=True if redirect_mode == "a" else False)
                try:
                    if mask_input:
                        command_context.output._masked = mask_input
                    if input is not None:
                        command_context.input+= input
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