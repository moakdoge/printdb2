import printdb
from printdb.core import command,command_manager,context

manager=command_manager.CommandManager()


@manager.command("example_func", "moakdoge")
def example_func(core):
    print("Hello, world!")
    pass


manager.run("example_func")