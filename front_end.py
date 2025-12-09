import printdb
from printdb.core import command,command_manager,context
from printdb.parsing import tokenizer
manager=command_manager.CommandManager()


@manager.command("example_func", "moakdoge")
def example_func(ctx: context.CommandContext, core: int):
    print(f"Hello, world!. Core is: {core}")
    pass



while True:
    content = input(">")
    command, args = tokenizer.tokenize_args(content)
    manager.run(command, *args)