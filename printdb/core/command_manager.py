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
        return [s.name for s in self._commands]
    
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


    async def run(self, cmd: str, add_to_history: bool = True) -> CommandTask | None:
        #checks for whitespace
        if cmd.strip().replace(" ", "") == "":
            return
        
        if add_to_history:
            self._command_history.append(cmd)

        #tokenize into pipes and redirects
        command,redirect_mode,redirect_file = tokenizer.tokensize_redirects(cmd)
        pipes = tokenizer.tokenize_pipes(cmd)
        background = cmd.endswith("&")

        out = None
        pipes_count = len(pipes) - 1
        other_tasks = []
        last_output = None

        for _, cmd in enumerate(pipes):
            is_at_end = (_ >= pipes_count)
            
            last_output = None
            if out is not None:
                last_output=out.ctx.output
                other_tasks.append(out)

            if redirect_mode is not None and redirect_file is not None:
                out= await self._run(*tokenizer.tokenize_args(command), redirect_file=redirect_file, redirect_mode=redirect_mode, input=last_output, mask_input=not is_at_end, background=background)
            else:
                out= await self._run(*tokenizer.tokenize_args(cmd), input=last_output,mask_input=not is_at_end, background=background)

        last_input = None
        if isinstance(out, CommandTask):
            last_output = out.ctx.output
            last_output._terminal = False

            for tk in other_tasks: #link all the tasks
                out.link_task(tk)
                tk.ctx.input = last_input
                last_input = tk.ctx.output
            
            out.ctx.input= last_input # type: ignore
            return out
        
        return None

    async def cleanup(self):
        '''Removes any complete tasks. Should be handled, but this is a fallback.'''
        self._tasks = [m for m in self._tasks if not m.task.done()]
    
    async def _track_task(self, task: CommandTask):
        if task in self._tasks:
            return #we've already processes this task
    
        self._tasks.append(task)

        def on_task_finish(t: asyncio.Task):
            nonlocal task

            #Clean up CTXs
            if task.ctx.output is not None:
                task.ctx.output.close()

            if task.ctx.input is not None:
                task.ctx.input.close()
            
            #if foreground, let other tasks take control
            if self._fore == task:
                self._fore = None
            
            #cleanup
            del task

        task.task.add_done_callback(on_task_finish)

    async def _spawn(self, command: Command, ctx: context.CommandContext, foreground=False, args: tuple = ()):
        task=asyncio.create_task(command.func(ctx, *args)) #create a task by calling this function
        new_task = CommandTask(command, ctx, task)
        
        #register it
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
            if command.name == cmd:

                #generate ctx to run command and parse args
                command_context:context.CommandContext = context.CommandContext(cmd, inp=input)
                args = argparser.type_check_args(command,args)


                #for redirects
                if redirect_file is not None and redirect_mode is not None:
                    append = (redirect_mode == "a")
                    command_context.output.redirect_file(redirect_file, append=append)
                elif redirect_file is not None:
                    traceback.throw(f"Please provide a redirect file!")
                    return
                elif redirect_mode is not None:
                    traceback.throw(f"Please provide a redirect mode! Options are: a, w, wb")

                #Attempt to run command
                try:
                    args = args or ()
                    command_context.input._terminal = True
                    command_context.output._terminal = (not mask_input)
                    
                    #allows starting.. should be removed
                    if input is not None:
                        import printdb.logging.sink as snk
                        if not isinstance(input, snk.LogSink):
                            await command_context.input.write(input)
                    

                    if background:
                        print(f"[{len(self._tasks)} / inf]: {cmd}")
                        return await self._spawn(command, command_context, foreground=False, args=args) # type: ignore
                    else:
                        return await self._spawn(command, command_context, foreground=True, args=args) #type: ignore
                
                except Exception as e:
                    print(traceback.trace_error(e))
                    return None
            
        traceback.throw("Command [[green]]%s[[red]] is not found! Did you mistype it?" % cmd)
        return None
    
    def get_command(self, cmd: str) -> Command | None:
        for command in self._commands:
            if command.name == cmd:
                return command
        return None