from printdb.api import *

@manager.command("cat", author="moakdoge")
def cat(ctx: CommandContext, file: Path = None, content: str = ""): # type: ignore
    '''
        Reads out the contents of a file / string to print.
    '''
    if file is not None:
        ctx.print(OSLib.read(file))
    else:
        ctx.print(content)


@manager.command("echo",author="moakdoge")
def echo(ctx: CommandContext, *args: str):
    if len(args) < 1:
        if ctx.input.read() != "":
            ctx.pprint(ctx.input.read())
            return CommandOutput(ErrorCode.SUCCESS, "Logged input")
    ctx.pprint(" ".join(args))