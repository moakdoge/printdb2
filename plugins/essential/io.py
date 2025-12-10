from printdb.api import *

@manager.command("cat", author="moakdoge")
async def cat(ctx: CommandContext, file: Path = None, content: str = ""): # type: ignore
    '''
        Reads out the contents of a file / string to print.
    '''
    if file is not None:
        await ctx.print(OSLib.read(file))
    else:
        await ctx.print(content)


@manager.command("output", author="moakdoge")
async def output(ctx: CommandContext):
    '''Echos back anything being sent to the pipe'''
    last_log = ""
    while True:
        o = await ctx.input.read()
        await ctx.pprint(o)
        if o != last_log:
            last_log = o
        await delay(0.25)

@manager.command("yes", author="moakdoge")
async def yes(ctx:CommandContext):
    '''Constantly sends a stream of yesses until killed'''
    while True:
        await ctx.output.write("y")
        await delay(0.01)

@manager.command("echo",author="moakdoge")
async def echo(ctx: CommandContext, *args: str):
    '''
        Repeats any file, argument, or pipe input passed in.
    '''
    if len(args) < 1:
        if ctx.input.read() != "":
            await ctx.pprint(ctx.input.read())
            return CommandOutput(ErrorCode.SUCCESS, "Logged input")
    await ctx.pprint(" ".join(args))