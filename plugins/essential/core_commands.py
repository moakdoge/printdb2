import os_utils

from printdb.api import *
import sys

from printdb.core.command_task import CommandTask
@manager.command("help", author="moakdoge")
async def help(ctx: CommandContext, command: str = ""):
    '''
        Provides a list of every command and details about them.
    '''
    if manager is not None: #im lazy
        for cmd in manager.get_commands():
            if command != "":
                if command != cmd.command and not command in cmd.aliases:
                    continue
            des=  cmd.details.description if cmd.details.description is not None else "N/A"
            aut = cmd.details.author if cmd.details.author is not None else "N/A" 
            des = des.strip()
            args = cmd.details.args
            pretty_args = []
            for arg in args:
                pretty_args.append(f"\t\t{arg.name}: [[yellow]]{arg.type.__name__}[[cyan]]{" [[green]](optional)[[cyan]]" if arg.optional else ""}")
            await ctx.pprint(f"[[bold]][[cyan]]{cmd.command}:[[reset]]", tabs=1)
            await ctx.pprint(f"[[red]][[bold]]Args:[[reset]][[cyan]]\n {"\n".join(pretty_args)}",tabs=2)
            await ctx.pprint(f"[[red]][[bold]]Author:[[reset]][[cyan]] {aut}",tabs=2)
            await ctx.pprint(f"[[red]][[bold]]Aliases:[[reset]][[cyan]] {",".join(cmd.aliases) if len(cmd.aliases) > 0 else "N/A"}",tabs=2)
            await ctx.pprint(f"[[red]][[bold]]Description:[[reset]][[cyan]] {des.replace("\n", "\n\t\t")}",tabs=2)
            await ctx.print("")

@manager.command("wait", author="moakdoge")
async def wait(ctx: CommandContext, seconds: float):
    '''
    Waits a certain amount of seconds.
    '''
    await delay(seconds)

@manager.command("exit", author="moakdoge")
async def exi_t(ctx: CommandContext, exit_code: int = 1):
    '''
    Immediately exits using the exit code provided.
    '''
    sys.exit(exit_code)

@manager.command("task", author="moakdoge")
async def control_tasks(ctx: CommandContext, mode: str = "", target: str = "all"):
    '''
    Allows you to manage tasks.
    mode: must be list/stop/info
    target: all OR a specific proccess ID
    '''
    allowed_modes = ["list", "info", "kill"]
    def generate_task_info(task: CommandTask, i="N/A"):
        lines = [
                    f"[[cyan]][[bold]]{task.task.get_name()}:[[reset]]",
                    f"\t[[red]][[bold]]Complete: [[reset]][[cyan]]{task.complete}[[reset]]",
                    f"\t[[red]][[bold]]Command: [[reset]][[cyan]]{task.command.name}[[reset]]",
                    f"\t[[red]][[bold]]Runtime:[[reset]][[cyan]]{task.runtime: .3f}s[[reset]]"
        ]
        return "\n".join(lines)
    
    match mode:
        case "list":
            for i, task in enumerate(manager._tasks):
                await ctx.pprint(generate_task_info(task))
        case "kill":
            if target == "all":
                result = True
                await manager.stop_all()
            else:
                result = await manager.kill(target)

            if result:
                await ctx.pprint(f"[[green]]Successfully killed task [[bold]]{target}[[reset]]")
            else:
                await ctx.pprint(f"[[red]]Unable to kill task [[bold]]{target}[[reset]]. [[red]]Is the task still alive?")
        case "info":
            if target == "all":
                await control_tasks(ctx, mode="list")
            else:
                for task in manager._tasks:
                    if task.task.get_name() == target:
                        await ctx.pprint(generate_task_info(task))
                        return
                await ctx.pprint(f"[[red]]Could not find task [[bold]]{target}[[reset]]")
        case _:        
            await ctx.pprint(f"[[red]]Please choose one of the following: {"/".join(allowed_modes)}")


@manager.command("test-exception", author="moakdoge")
async def test_exception(ctx: CommandContext, message: str = "Example execption raised by test-exception"):
    raise Exception(message)
    return CommandOutput(ErrorCode.SUCCESS)

@manager.command("exec", author="moakdoge")
async def execute(ctx: CommandContext, file: Path):
    '''Executes the commands inside of a file.'''
    file = file.expanduser()
    if not file.exists():
        raise FileNotFoundError(file)
    await manager.run_file(file)
    
@manager.command(name="config", author="moakdoge", aliases=["configuration", "conf"])
async def update_conf(ctx: CommandContext, options: str = "refresh"):
    '''Changes setting about your configuration'''
 
    file = manager.get_prefetch()
    match options:
        case "refresh":
            file = file.expanduser()
            if not file.exists():
                raise FileNotFoundError(file)
            await manager.run_file(file)
        case "delete":
            OSLib.remove_file(file)
            await ctx.pprint(f"Deleted file [[magenta]]{file.absolute()}[[reset]] successfully.")
        case "create":
            OSLib.remove_file(file)
            manager.get_prefetch() #creates a prefetch
            await ctx.pprint(f"Recreated file [[magenta]]{file.absolute()}[[reset]] successfully.")
        case "open":
            await OSLib.open(file)
        case "watch":
            async with OSLib.watch_file(file, full=True) as file:
                pass
            await manager.run_file(file)
        case _:
            return CommandOutput(ErrorCode.GENERIC_ERROR, f"Please choose a valid type: refresh, delete, create, open.")