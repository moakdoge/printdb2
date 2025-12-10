from printdb.api import manager, ErrorCode
from printdb.api.frontend import tokenizer, colorize, input_prompt
import readline,os,asyncio
from aioconsole import ainput
from printdb.input.async_input import input, AutofillRule
import sys

def resource_path(rel_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):  
        base = sys._MEIPASS  # type: ignore
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, rel_path)
manager.load_plugin_folder(f"{resource_path("plugins")}")


def autofill_func(st):
    for cmd in manager.get_commands():
        st = st.replace(cmd.command, f"[[green]]{cmd.command}[[reset]]")
    return st

def autofill(st):
    # Only autofill the *first* token
    if " " in st:
        return st  # stop autofill once args start

    for cmd in manager.get_commands():
        full = cmd.command

        # generate prefixes: h, he, hel, help
        for i in range(1, len(full)):
            prefix = full[:i]

            if st == prefix:
                return full

    return st


autofill_rules = [
    AutofillRule.regex(r'(?<!")\b\d+(?:\.\d+)?\b(?!")(?=(?:[^"]*"[^"]*")*[^"]*$)', "[[red]]%s[[reset]]",at_end=False),
    AutofillRule(on_char=autofill_func),
    AutofillRule(on_char=autofill,text_replacement=True, cancel_char=True, on_tab=True),
]
ON_INPUT= False
async def main():
    await manager.stop()
    global ON_INPUT
    while True:
        if True:
            ON_INPUT = True
            content = await input(input_prompt.input_prompt(), history=manager._command_history, rules=autofill_rules)
            ON_INPUT = False
            await manager.run(content)



if __name__ == "__main__":

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            loop.run_until_complete(main())
        except KeyboardInterrupt:
            if ON_INPUT:
                sys.exit(1)
                break
