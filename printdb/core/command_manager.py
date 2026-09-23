import importlib.util
from pathlib import Path
import token
from types import ModuleType

import printdb
from printdb.logging.sink import LogSink
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
    
    def command(self, name: str, author: str = "", aliases:list[str] | None =None):
        def decorator(func):
            cmd = Command(name,func,None,CommandDetails(author, func.__doc__))
            cmd.aliases = aliases if aliases is not None else []
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
        l = [s.name for s in self._commands]
        for s in self._commands:
            for _ in s.aliases:
                l.append(_)
        return l
    
    def get_commands(self) -> list[Command]:
        return self._commands
    
    def load_plugin_folder(self, path: Path):
        if not os.path.exists(path):
            raise OSError(f"Can't find plugin folder {path}!")
            return
        for dirpath, dirnames, filenames in os.walk(path):
            for file in filenames:
                if os.path.splitext(file)[1] == ".py":
                    self.load_plugin(os.path.join(dirpath, file))

   
    async def run(self, cmd: str, add_to_history: bool = True) -> CommandTask | None:

        try:
            #checks for whitespace
            if cmd.strip().replace(" ", "") == "":
                return
                
            #checks if its a command
            if cmd.strip().startswith("#"):
                return 


            
            if add_to_history:
                self._command_history.append(cmd)
                
            cmd = argparser.strip_comments(cmd)
            
            
            #process tokens
            embedded =tokenizer._extract_embedded(cmd)
            async def _to_str(token: tokenizer.EmbeddedToken | str, typ: str = "text") -> str | None:
                if isinstance(token, str):
                    return token
                
                
            async def _to_list_str(token: list[tokenizer.EmbeddedToken]):
                ls = []
                for tok in token:
                    l = tok.contents
                    if isinstance(l, list):
                        l = await _to_list_str(l)

                    if tok.type == "template":
                        if isinstance(tok.contents, list):
                            new_st = await _to_list_str(tok.contents)
                        else:
                            new_st = tok.contents
                        if not isinstance(new_st, str) or new_st.strip() == "":
                            continue
                        _new, _args = tokenizer.tokenize_args(new_st)
                        out = await self._run(_new, _args, mask_input=True)
                        if not out:
                            continue
                        ctx = "".join(out.ctx.output._copy_queue)
                        if ctx.endswith("\n"):
                            ctx = ctx[:-1]
                        ctx = (
                            ctx.replace("\\", "\\\\")
                            .replace("\"", "\\\"")
                            .replace("\n", "\\n")
                            .replace("\r", "\\r")
                            .replace("\t", "\\t")
                        )
                        ls.append(f'"{ctx}"')
                        continue
                    st = await _to_str(l, tok.type)
                    ls.append(st)
                
                return "".join(ls)
        
            
            cmd = await _to_list_str(embedded)
            #print(list)
            #print(cmd)
            #tokenize into pipes and redirects
            command,redirect_mode,redirect_file = tokenizer.tokensize_redirects(cmd)
            
                        

                    
            
            pipes = tokenizer.tokenize_pipes(cmd)
            background = cmd.endswith("&")

            out = None
            pipes_count = len(pipes) - 1
            other_tasks: list[CommandTask] = []
            _tmp_outs: list[CommandTask] = []
            last_output = None
            _pipes = pipes_count > 0

            for _, cmd in enumerate(pipes):
                is_at_end = (_ >= pipes_count)
                b=background or (not is_at_end and pipes_count > 0)
                if out is not None:
                    last_output=out.ctx.output
                    other_tasks.append(out)
                try:
                    if is_at_end:
                        for task in other_tasks:
                            task.ctx.output._terminal = False
                    out= await self._run(*tokenizer.tokenize_args(cmd), 
                                         input=last_output,
                                         mask_input=not is_at_end, 
                                         background=b, 
                                         piped=_pipes and is_at_end, 
                                         linked_tasks = other_tasks if (_pipes and is_at_end) else None,
                                         redirect_file=redirect_file if is_at_end else None,
                                         redirect_mode=redirect_mode if is_at_end else None)
                    if b and pipes_count > 0:
                        last_output = out.ctx.output # type: ignore         
                except Exception as e:
                    traceback.throw(e.args[0])
                    return
                


            return None
        except Exception as e:
            traceback.throw(e.args[0])
        
        

    def cleanup(self):
        '''Removes any complete tasks. Should be handled, but this is a fallback.'''
        self._tasks = [m for m in self._tasks if not m.task.done()]
    
    async def _track_task(self, task: CommandTask):
        if task in self._tasks:
            return #we've already processes this task
    
        self._tasks.append(task)

        def on_task_finish(t: asyncio.Task):
            nonlocal task

            self.cleanup()
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

    async def _spawn(self, command: Command, ctx: context.CommandContext, foreground=False, args: tuple = (), link: list[CommandTask] | None = None):
        task=asyncio.create_task(command.func(ctx, *args)) #create a task by calling this function
        new_task = CommandTask(command, ctx, task)
        if link:
            for tk in link:
                new_task.link_task(tk)
        
        #register it
        await self._track_task(new_task)
        if foreground and self._fore is None:
            self._fore = new_task
            await new_task.task
        
        return new_task

    async def stop(self) -> bool:
        if self._fore is not None:
            await self._fore.stop()
            self._fore = None
            return True
        else:
            await self.stop_all()

        return False
        
    async def stop_all(self):
        for task in self._tasks[:]:
            await task.stop()
    
    async def kill(self, task_id: str) -> bool:
        for task in self._tasks:
            if task.task.get_name() == task_id:
                task.task.cancel()
                return True
        return False

    async def _run(self, cmd: str, args, redirect_file = None, redirect_mode = None, input=None, mask_input = False, background=False, piped: bool = False, linked_tasks: list[CommandTask] | None = None) -> CommandTask | None:
        '''
            DO NOT CALL! call the normal run instead, unless you are a plugin trying to run a command manually.
        '''
        for command in self._commands:
            if command.name == cmd or cmd in command.aliases:
                cmd = command.name
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
                    command_context.input._terminal = not piped
                    command_context.output._terminal = (not mask_input)

                    #allows starting.. should be removed
                    if input is not None:
                        import printdb.logging.sink as snk
                        if not isinstance(input, snk.LogSink):
                            await command_context.input.write(input)
                    
                    #link tasks
                    

                            
                    if background:
                        print(f"[{len(self._tasks)} / inf]: {cmd}")
                        return await self._spawn(command, command_context, foreground=False, args=args, link=linked_tasks) # type: ignore
                    else:
                        return await self._spawn(command, command_context, foreground=True, args=args, link=linked_tasks) #type: ignore
                
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
    
    def get_prefetch(self) -> Path:
        home = Path.home() / "printdb.cmd"
        stock = Path(__file__).parent.parent / "STOCK.cmd"
        if not home.exists():
            if stock.exists():
                home.write_text(stock.read_text())
            else:
                home.write_text("")
        return home

    async def run_file(self, fi: Path):
        if not fi.exists():
            raise FileNotFoundError(fi)
        
        #attempt to split by line
        text = fi.read_text()
        lines = text.splitlines()

        result = []
        current = ""

        for line in lines:
            stripped = line.rstrip()

            if stripped.endswith("\\"):
                current += stripped[:-1] + " "
            else:
                current += line
                result.append(current)
                current = ""

        result = [r for r in result if r.strip("") != ""]
        for command in result:
            await self.run(command, False)