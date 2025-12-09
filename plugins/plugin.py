from printdb.api import *

@manager.command("example_func", author="moakdoge")
def example_func(ctx: CommandContext, core: int):
    ctx.pprint(f"[[red]]Example of prettified text / content. [[bold]]Isn't it pretty?[[reset]] [[reset]]")
    ctx.print("by default has a newline but can be anything")
    return CommandOutput(ErrorCode.GENERIC_ERROR,output="Example test")

@manager.command("cat", author="moakdoge")
def cat(ctx: CommandContext, file: Path = None, content: str = ""): # type: ignore
    if file is not None:
        ctx.print(OSLib.read(file))
    else:
        ctx.print(content)