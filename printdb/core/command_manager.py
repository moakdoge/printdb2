import importlib.util
from types import ModuleType
from . import command, context, command_output
from printdb.logging import traceback
from .command_output import ErrorCode
from .command import Command,CommandDetails
from printdb.parsing import argparser, tokenizer
from .exceptions import *
import os, asyncio
class CommandManager:

    def __init__(self):
        self._commands: list[Command] = []
        self._loaded_plugins: list[ModuleType] = []
        self._tasks: list = []
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


    async def run(self, cmd: str) -> command_output.CommandOutput:
        #tokenize into pipes and redirects
        newcmd,mode,file = tokenizer.tokensize_redirects(cmd)
        pipes = tokenizer.tokenize_pipes(cmd)
        bg= False
        if cmd.endswith("&"):
            bg = True
        out = command_output.CommandOutput(ErrorCode.SUCCESS, "", "")
        m = len(pipes) - 1
        for i, cmd in enumerate(pipes):
            is_at_end = (i >= m)

            if mode is not None and file is not None:
                c, args = tokenizer.tokenize_args(newcmd)
                out= await self._run(c, args, redirect_file=file, redirect_mode=mode, input=out.log, mask_input=not is_at_end, backgound=bg)
            else:
                c, args = tokenizer.tokenize_args(cmd)
                out= await self._run(c, args, input=out.log,mask_input=not is_at_end, backgound=bg)
        return out


    async def _track_task(self, task: asyncio.Task):
        self._tasks.append(task)
        def on_task_finish(t):
            self._tasks = [m for m in self._tasks if not m.done()]
        task.add_done_callback(on_task_finish)

    async def _spawn(self, func):
        await self._track_task(asyncio.create_task(func))

    async def _run(self, cmd: str, args, redirect_file = None, redirect_mode = None, input=None, mask_input = False, backgound=False) -> command_output.CommandOutput:
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
                    command_context.input._masked = True
                    command_context.output._masked = mask_input

                    if input is not None:
                        command_context.input+= input
                    
                    if args is not None:
                        if backgound:
                            await self._spawn(command.run(command_context, *args))
                            print(f"[{len(self._tasks)} / inf]: {cmd}")
                            return_value = command_output.CommandOutput(ErrorCode.SUCCESS, f"Started thread [{len(self._tasks)}]")
                        else:
                            return_value = await command.run(command_context, *args)
                    else:
                        if backgound:
                            self._tasks.append(asyncio.create_task(command.run(command_context, None)))
                            return_value = command_output.CommandOutput(ErrorCode.SUCCESS, f"Started thread [{len(self._tasks)}]")
                        else:
                            return_value = await command.run(command_context, *args)
                    if not isinstance(return_value, command_output.CommandOutput):
                        return command_output.CommandOutput(ErrorCode.SUCCESS, log=command_context.output.read())
                    else:
                        return_value.log = command_context.output.read()
                        return return_value
                except Exception as e:
                    print(traceback.trace_error(e))
        return command_output.CommandOutput(ErrorCode.COMMAND_NOT_FOUND, output="Command not found")
    
    def get_command(self, cmd: str) -> Command | None:
        for command in self._commands:
            if command.command == cmd:
                return command
        return None