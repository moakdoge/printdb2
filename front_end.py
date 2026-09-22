from printdb.api import manager, ErrorCode
from printdb.api.frontend import tokenizer, colorize, input_prompt
import readline,os,asyncio
from printdb.input.async_input import input, AutofillRule
import sys

from printdb.input.autofillrules import HintAutofillRule, RegexAutofillRule

def resource_path(rel_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):  
        base = sys._MEIPASS  # type: ignore
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, rel_path)
manager.load_plugin_folder(f"{resource_path("plugins")}")
prefetch = manager.get_prefetch()
FIRST_RUN = True

test_rule = AutofillRule(on_tab=True)


def test(c):
    return c

test_rule.on_char = test
autofill_rules = [
    RegexAutofillRule(r'(?<!")\b\d+(?:\.\d+)?\b(?!")(?=(?:[^"]*"[^"]*")*[^"]*$)', "[[red]]%s[[reset]]"),
   # AutofillRule.autofill(manager.get_command_names()),
   # AutofillRule.replace(manager.get_command_names(), "[[bold]]%s[[reset]]", replace_text=False),
   # AutofillRule.regex(r'"(?:\\.|[^"\\])*"',"[[yellow]]%s[[reset]]", at_end=False),
    HintAutofillRule("help", ["option1", "command1"])
]

ON_INPUT= False
async def main():
    global FIRST_RUN
    if FIRST_RUN:
        await manager.run_file(manager.get_prefetch())
        FIRST_RUN = False
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
