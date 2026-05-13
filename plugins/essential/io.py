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
        await ctx.print(f"reading: {o}")
        await delay(0.1)

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

    await ctx.pprint(" ".join([arg.__repr__() if not isinstance(arg, str) else arg for arg in args]))
    return CommandOutput(ErrorCode.SUCCESS, "Logged input")

@manager.command("ls", author="moakdoge", aliases=["dir"])
async def ls(ctx: CommandContext, hidden: bool = False):
    '''Prints all files in the current directory.'''
    files = OSLib.list_files()
    folders = OSLib.list_folders()

    for folder in folders:
        if folder.name.startswith(".") and not hidden:
            continue
        await ctx.pprint(f"[[blue]][[bold]]{folder.name}[[reset]]")

    for file in files:
        if file.name.startswith(".") and not hidden:
            continue
        if OSLib.is_executable(file):
            await ctx.pprint(f"[[green]]{file.name}[[reset]]")
            continue
        await ctx.pprint(f"{file.name}")
    
@manager.command("cd", author="moakdoge")
async def cd(ctx: CommandContext, path: Path):
    OSLib.change_dir(path)