import printdb
from printdb.core import command,command_manager,context
from printdb.parsing import tokenizer,argparser
manager=command_manager.CommandManager()


@manager.command("example_func", "moakdoge")
def example_func(ctx: context.CommandContext, core: int):
    print(f"Hello, world!. Core is: {core}")
    pass



while True:
    content = input(">")
    cmd, args = tokenizer.tokenize_args(content)
    print(argparser.type_check_args(manager.get_command(cmd), args))
    manager.run(cmd, *args)