from printdb.api import *

@manager.command("example_func", author="moakdoge")
def example_func(ctx: CommandContext, core: int):
    ctx.pprint(f"[[red]]Example of prettified text / content. [[bold]]Isn't it pretty?[[reset]] [[reset]]")
    ctx.print("by default has a newline but can be anything")
    return CommandOutput(ErrorCode.GENERIC_ERROR,output="Example test")

