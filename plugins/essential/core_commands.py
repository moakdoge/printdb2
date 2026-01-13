from printdb.api import *
import sys
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
async def control_tasks(ctx: CommandContext, mode: str = "list", target: str = "all"):
    '''
    Allows you to manage tasks.
    mode: must be list/stop/info
    target: all OR a specific proccess ID
    '''
    allowed_modes = ["list", "stop", "info"]
    await ctx.pprint("")
    if mode.lower() not in allowed_modes:
        await ctx.pprint("[[red]]Please choose one of the following: list/stop/info")
        return CommandOutput(ErrorCode.GENERIC_ERROR, "Invalid mode")
    if mode == "list":
        for i, task in enumerate(manager._tasks):
            lines = [
                f"[[red]][[bold]]{task.task.get_name()} (PID: {i}) :[[reset]]",
                f"\t[[red]]Complete:[[cyan]]{task.complete}[[reset]]",
                f"\t[[red]]Command:[[cyan]]{task.command.command}[[reset]]",
                f"\t[[red]]Runtime:[[cyan]]{task.runtime}[[reset]]"
            ]
            await ctx.pprint("\n".join(lines))


@manager.command("test-exception", author="moakdoge")
async def test_exception(ctx: CommandContext, message: str = "Example execption raised by test-exception"):
    raise Exception(message)
    return CommandOutput(ErrorCode.SUCCESS)