import importlib.util
from types import ModuleType

import printdb
from . import command, context, command_output
from printdb.logging import traceback
from .command_output import ErrorCode
from .command import Command,CommandDetails
from .command_task import CommandTask
from printdb.parsing import argparser, tokenizer
from .exceptions import *
import os, asyncio
class CommandManager:

    def __init__(self):
        self._commands: list[Command] = []
        self._loaded_plugins: list[ModuleType] = []
        self._tasks: list[CommandTask] = []
        self._command_history: list[str] = []
        self._fore = None
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
    
    def get_command_names(self):
        return [s.command for s in self._commands]
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


    async def run(self, cmd: str) -> CommandTask | None:
        #tokenize into pipes and redirects
        self._command_history.append(cmd)
        newcmd,mode,file = tokenizer.tokensize_redirects(cmd)
        pipes = tokenizer.tokenize_pipes(cmd)
        bg= False
        if cmd.endswith("&"):
            bg = True
        out = None
        m = len(pipes) - 1

        other_tasks = []
        for i, cmd in enumerate(pipes):
            is_at_end = (i >= m)
            if out is None:
                d = None
            else:
                d=out.ctx.output
                other_tasks.append(out)
            if mode is not None and file is not None:
                c, args = tokenizer.tokenize_args(newcmd)
                out= await self._run(c, args, redirect_file=file, redirect_mode=mode, input=d, mask_input=not is_at_end, background=bg)
            else:
                c, args = tokenizer.tokenize_args(cmd)
                out= await self._run(c, args, input=d,mask_input=not is_at_end, background=bg)
        last_inp = None
        if isinstance(out, CommandTask):
            out.ctx.output._terminal = False
            for tk in other_tasks:
                out.link_task(tk)
                tk.ctx.input = last_inp
                last_inp = tk.ctx.output
            out.ctx.input= last_inp
            return out
        return None


    async def _track_task(self, task: CommandTask):
        self._tasks.append(task)
        def on_task_finish(t: asyncio.Task):
            nonlocal task
            self._tasks = [m for m in self._tasks if not m.task.done()]
            if task.ctx.output is not None:
                task.ctx.output.close()
            if task.ctx.input is not None:
                task.ctx.input.close()
            if self._fore == task:
                self._fore = None
            t.cancel()
        task.task.add_done_callback(on_task_finish)

    async def _spawn(self, cmd: Command, cont: context.CommandContext, foreground=False, args: tuple = ()):
        new_task = CommandTask(cmd, cont, asyncio.create_task(cmd.func(cont, *args)))
        await self._track_task(new_task)
        if foreground and self._fore is None:
            self._fore = new_task
            await new_task.task
        return new_task

    async def stop(self) -> bool:
        if self._fore is not None:
            self._fore.task.cancel()
            self._fore = None
            return True
        else:
            await self.stop_all()
        return False
        
    async def stop_all(self):
        for task in self._tasks:
            task.task.cancel()

    async def _run(self, cmd: str, args, redirect_file = None, redirect_mode = None, input=None, mask_input = False, background=False) -> CommandTask | None:
        '''
            DO NOT CALL! call the normal run instead, unless you are a plugin trying to run a command manually.
        '''
        for command in self._commands:
            if command.command == cmd:
                command_context:context.CommandContext = context.CommandContext(cmd, inp=input)
                try:
                    args = argparser.type_check_args(command,args)
                except InvalidParamType as e:
                    return None
                except MissingParam as e:
                    return None


                if redirect_file is not None and redirect_mode is not None:
                    if redirect_mode == "a" and not os.path.exists(redirect_file):
                        return None #command_output.CommandOutput(ErrorCode.FILE_NOT_FOUND, output=f"Redirect file of '{redirect_file}' does not exist and you are in append mode!")
                    command_context.output.redirect_file(redirect_file, append=True if redirect_mode == "a" else False)
                try:
                    args = args or ()
                    command_context.input._terminal = True
                    command_context.output._terminal = not mask_input
                    if input is not None:
                        import printdb.logging.sink as snk
                        print(type(input))
                        if not isinstance(input, snk.LogSink):
                            await command_context.input.write(input)
                    
                        # Normalize args

                    if background:
                        print(f"[{len(self._tasks)} / inf]: {cmd}")
                        return await self._spawn(command, command_context, foreground=False, args=args)

                    return await self._spawn(command, command_context, foreground=True, args=args)
                except Exception as e:
                    print(traceback.trace_error(e))
        return None
    
    def get_command(self, cmd: str) -> Command | None:
        for command in self._commands:
            if command.command == cmd:
                return command
        return None