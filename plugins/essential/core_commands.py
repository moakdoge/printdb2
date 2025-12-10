from printdb.api import *

@manager.command("help", author="moakdoge")
async def help(ctx: CommandContext, command: str = ""):
    '''
        Provides a list of every command and details about them.
    '''
    if manager is not None: #im lazy
        for cmd in manager.get_commands():
            if command != "":
                if command != cmd.command:
                    continue
            des=  cmd.details.description if cmd.details.description is not None else "N/A"
            aut = cmd.details.author if cmd.details.author is not None else "N/A" 
            des = des.strip()
            args = cmd.details.args
            pretty_args = []
            for arg in args:
                pretty_args.append(f"{arg.name}: [[yellow]]{arg.type.__name__}[[cyan]]{" [[green]](optional)[[cyan]]" if arg.optional else ""}")
            ctx.pprint(f"\t[[bold]][[cyan]]{cmd.command}:[[reset]]")
            ctx.pprint(f"\t\t[[red]][[bold]]Args:[[reset]][[cyan]] {", ".join(pretty_args)}")
            ctx.pprint(f"\t\t[[red]][[bold]]Author:[[reset]][[cyan]] {aut}")
            ctx.pprint(f"\t\t[[red]][[bold]]Description:[[reset]][[cyan]] {des}")
            ctx.print("")


@manager.command("wait", author="moakdoge")
async def wait(ctx: CommandContext, seconds: float):
    '''
    Waits a certain amount of seconds.
    '''
    await delay(seconds)