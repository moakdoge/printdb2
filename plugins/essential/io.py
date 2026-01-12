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
        print(o)
        
@manager.command("yes", author="moakdoge")
async def yes(ctx:CommandContext):
    '''Constantly sends a stream of yesses until killed'''
    while True:
        await ctx.output.write("y\n")
        await delay(0.1)

@manager.command("echo",author="moakdoge")
async def echo(ctx: CommandContext, *args: str):
    '''
        Repeats any file, argument, or pipe input passed in.
    '''
    if len(args) < 1:
        async for i in ctx.input.read_chunks():
            await ctx.print(i)

    await ctx.pprint(" ".join(args))
    return CommandOutput(ErrorCode.SUCCESS, "Logged input")