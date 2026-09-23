from pathlib import Path

from printdb.api import manager, ErrorCode
from printdb.api.frontend import tokenizer, colorize, input_prompt
import readline,os,asyncio
from printdb.input.async_input import BaseAutofillRule, ainput
import sys

from printdb.input.autofillrules import HintAutofillRule, RegexAutofillRule
manager.load_plugin_folder(Path(__file__).parent / "plugins")
prefetch = manager.get_prefetch()
FIRST_RUN = True

autofill_rules: list[BaseAutofillRule] = [
    RegexAutofillRule(r'(?<!")\b\d+(?:\.\d+)?\b(?!")(?=(?:[^"]*"[^"]*")*[^"]*$)', "[[red]]%s[[reset]]"),
    HintAutofillRule("help", ["option1", "command1"])
]

for command_name in manager.get_command_names():
    autofill_rules.append(HintAutofillRule("", [command_name]))

ON_INPUT= False
async def main():
    global FIRST_RUN
    if FIRST_RUN:
        await manager.run_file(manager.get_prefetch())
        FIRST_RUN = False
    await manager.stop()
    global ON_INPUT
    while True:
        ON_INPUT = True
        content = await ainput(input_prompt.input_prompt(), history=manager._command_history, rules=autofill_rules)
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
                sys.exit(0)
                break
