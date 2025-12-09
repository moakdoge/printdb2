import printdb
from printdb.core import command,command_manager,context,command_output
from printdb.parsing import tokenizer,argparser
manager=command_manager.CommandManager()


@manager.command("example_func", author="moakdoge")
def example_func(ctx: context.CommandContext, core: int):
    ctx.pprint(f"[[red]]Example of prettified text / content. [[bold]]Isn't it pretty?[[reset]] [[reset]]")
    ctx.print("by default has a newline but can be anything")
    return command_output.CommandOutput(command_output.ErrorCode.GENERIC_ERROR,output="Example test")



while True:
    content = input(">")
    cmd, args = tokenizer.tokenize_args(content)
    output = manager.run(cmd, args)
    print(output.error_code)