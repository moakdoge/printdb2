import printdb
from printdb.core import command,command_manager,context
from printdb.parsing import tokenizer,argparser
manager=command_manager.CommandManager()


@manager.command("example_func", "moakdoge")
def example_func(ctx: context.CommandContext, core: int):
    ctx.pprint(f"[[red]]Example of prettified text / content. [[bold]]Isn't it pretty?[[reset]] [[reset]]")
    ctx.print("by default has a newline but can be anything")
    pass



while True:
    content = input(">")
    cmd, args = tokenizer.tokenize_args(content)
    manager.run(cmd, args)