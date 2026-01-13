from printdb.api import *
import re
from datetime import datetime

from printdb.parsing import tokenizer

@manager.command("welcome", author="moakdoge")
async def welcome(ctx: CommandContext):
    '''Welcomes you. Ported from printdb v1.'''
    import time
    from datetime import datetime
    import re

    TAGS = re.compile(r'\[\[[^\]]+\]\]')

    def strip_tags(s: str) -> str:
        return TAGS.sub("", s)

    def visible_len(s: str) -> int:
        return len(strip_tags(s))

    def fmt_time(sec: float) -> str:
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = sec % 60
        return f"{h:02}:{m:02}:{s:05.2f}"

    runtime = time.time()
    now = datetime.now()

    lines = [
        f"Welcome, @[[red]]moakdoge[[reset]]!",
        f"Today is [[cyan]]{now:%Y/%m/%d}[[reset]] [[white]]and it's currently[[reset]] [[cyan]]{now:%H:%M:%S}[[reset]]",
        f"Currently, there are [[fg red]]{len(manager.get_commands())}[[reset]] commands loaded.",
        "[dash]",
        f"Aliases: [[magenta]]{len(manager.get_command_names())- len(manager.get_commands())}[[reset]]",
        f"Uptime: [[cyan]]{fmt_time(runtime)}[[reset]]",
        "[dash]",
        "Thanks for using [[yellow]]printdb[[bold]]v2[[reset]][[yellow]]![[reset]]",
    ]

    max_width = max(
        visible_len(line)
        for line in lines
        if line != "[dash]"
    )

    border = "-" * (max_width + 4)
    output = [border]

    for line in lines:
        if line == "[dash]":
            output.append("||" + "-" * max_width + "||")
            continue

        pad = max_width - visible_len(line)
        left = pad // 2
        right = pad - left

        output.append(f"||{' ' * left}{line}{' ' * right}||")

    output.append(border)

    await ctx.pprint("\n".join(output))

@manager.command("grep", author="moakdoge")
async def grep(ctx:CommandContext, pattern: str, file:Path = None, input:str = ""): # type: ignore
    '''Search for a pattern in an input or files. 
    Example: grep pattern file.txt
    '''
    lines: list[str] = []
    if file is not None:
        with open(file, "r") as f:
            lines = f.read().splitlines()
    elif input != "":
        lines = input.splitlines()
    elif ctx.input.read() != "":
        lines = ctx.input.read().splitlines()

    results = 0
    for line in lines:
        if pattern in line:
            await ctx.pprint(f"{line.replace(pattern, f"[[red]]{pattern}[[reset]]")}")
            results+=1
    if results < 1:
        await ctx.pprint("[[red]]grep: no results found")

@manager.command("time", author="moakdoge")
async def time(ctx: CommandContext, c: str):
    '''
        Times a command.
    '''
    import time
    f=""
    start = time.time()

    cmd, args = tokenizer.tokenize_args(c)
    #TODO: make a better api then relying on _run
    t = await manager._run(cmd, args, background=False)
    if t is None:
        await ctx.pprint(f"[[red]]Failed to run command!")
        return
    
    await t.task # type: ignore
    end = time.time()
    await ctx.pprint(f"Command {1} took {end - start:.4f}s.")