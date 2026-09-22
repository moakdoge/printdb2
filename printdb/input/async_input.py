import asyncio
import sys
from typing import Callable, LiteralString, overload
from printdb.input.autofillrules import BaseAutofillRule
from printdb.logging.colors import *
from printdb.parsing.tokenizer import *
import printdb.api as api
from sys import stdout


if sys.platform == "win32":
    import msvcrt

    async def raw_getch():
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, msvcrt.getwch)

else:
    import termios, tty


    def _blocking_linux_getch():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    async def raw_getch():
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _blocking_linux_getch)


'''
async def input(prompt: str) -> str:
    st = ""
    cursor = -1
    def log():
        nonlocal st, cursor
        cmd, args = tokenize_args(st)
        if len(st) > 1:
            print("\b" * (len(st)-1), end="")
        raw = st
        raw = raw[:cursor] + "[[inverse]]" + raw[cursor] + "[[reset]][[red]]" + raw[cursor+1:]
        if api.manager.get_command(cmd):
            raw = raw.replace(cmd, f"[[green]]{cmd}[[red]]")
        else:
            pass
        print(colorize(f"[[red]]{raw}[[reset]]"), end="", flush=True)
    print(prompt,end="",flush=True)
    while True:
        ch = await raw_getch()
        if ch in ("\r", "\n"): #nl
            print()
            return st
        
        if ch == "\x03":
            print()
            raise KeyboardInterrupt
        
        if ch in ("\x08", "\x7f"): #backspace
            if st:
                st = st[:-1]
                cursor-=1
                print("\b \b", end="", flush=True)
            continue
        if ch == "\x1b[A": #up
            pass
        elif ch == "\x1b[B": #down
            pass
        
        if ch == "\x1b[C": #right
            cursor+= 1
            if cursor > len(st):
                cursor = len(st)
            continue
        if ch == "\x1b[D": #left
            cursor-= 1
            if cursor < 0:
                cursor = 0
            continue
        st += ch
        cursor += len(ch)
        log()
'''

class AutofillRule():
    def __init__(self, on_send=None, on_char=None, text_replacement=False, on_tab=False, cancel_char = False):
        self.on_send = on_send
        self.on_char = on_char
        self.text_replacement = text_replacement
        self.on_tab = on_tab
        self.on_tab_func: Callable|None = None
        self.cancel = cancel_char

    @classmethod
    def regex(cls, regex: str, replacement: str, at_end=False):
        '''Use %s as s'''
        def replace_regex(t):
            def repl(match):
                if "%s" in replacement:
                    return colorize(replacement % match.group(0))
                else:
                    return colorize(replacement)
            return re.sub(regex, repl, t)
        if at_end:
            return AutofillRule(on_send=replace_regex)
        else:
            return AutofillRule(on_char=replace_regex)
    
    @classmethod
    def replace(cls, rep: list | str, replacement: str, replace_text: bool = True):
        def re(inp: str):
            if isinstance(rep, list):
                for i in rep:
                    inp = inp.replace(i, replacement % i)
                return inp
            else:
                return inp.replace(rep, replacement)
        return AutofillRule(on_char=re, text_replacement=replace_text)

    @classmethod
    def autofill(cls, lis: list[str], tab: bool = True):
        def autofill(st):
            if " " in st:
                return st
            for cmd in lis:
                full = cmd
                for i in range(1, len(full)):
                    prefix = full[:i]
                    if st == prefix:
                        return full

            return st
        return AutofillRule(on_char=autofill, text_replacement=True, on_tab=tab,cancel_char=True)

    @classmethod
    def ghost(cls, start: list[str], options: list[str]) -> AutofillRule:
        def on_char(st: str, autofill:bool=False):
            joined = "".join(start)
            formatted = strip_ansi(st.strip(" ").strip("\t"))
            if formatted.startswith(joined):
                parts_after = formatted[len(joined):-1]
                if parts_after == "":
                    return st

                parts_after = parts_after.strip(" ").strip("\t")
                for opt in options:
                    if parts_after.startswith(opt[0:len(parts_after)]):
                        if not autofill:
                            return f"{st[:-2]}\x1b[27m\033[90m{opt[len(parts_after):-1]}\033[0m"
                        else:
                            return f"{st[:-2]}{opt[len(parts_after):-1]}"
            return st

        c = cls(on_char=on_char)
        c.on_tab_func = on_char
        return c
    
async def get_character(): #only used to combine the arrow keys lol
    char = await raw_getch()
    if char == "\x1b":
        new = char
        part2 = await raw_getch()
        if part2 == "[":
            letter = await raw_getch()
            if letter in ("A", "B", "C", "D"):
                return new + part2 + letter
    return char


async def generate_display(typed: list[str]) -> str:
    new = []
    for char in typed:
        match char:
            case "\x1b[A" | "\x1b[B" | "\x1b[C" | "\x1b[D":
                pass
            case _:
                new.append(char)

    return "".join(new)
            
@overload
def strip_ansi(typed: list[str] ) -> list[str]:
    ...
@overload
def strip_ansi(typed: str) -> str:
    ...


def strip_ansi(typed: str | list[str]) -> list[str] | str:
    import re

    ansi = re.compile(
        r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\)|[ -/]*[@-~])"
    )
    value = "".join(typed) if isinstance(typed, list) else typed
    cleaned = ansi.sub("", value).replace("\x7f", "")

    return list(cleaned) if isinstance(typed, list) else cleaned


async def handle_cursor(typed: list[str], display: str) -> int:
    '''Gets the position of the cursor'''
    start = 0
    display_length = len(strip_ansi(display))
    for char in typed:
        match char:
            case "\x1b[A": #UP
                pass

            case "\x1b[B": #DOWN
                pass

            case "\x1b[C": #RIGHT
                start += 1

            case "\x1b[D": #LEFT
                start -= 1

            case "\x08" | "\x7f":
                start -= 1

            case _:
                start += 1
                pass

        start = max(min(start, display_length+1), 0)

    return start

async def handle_backspace(typed: list[str], cursor: int) -> None:
    try:
        backspace_index = len(typed) - 1 - typed[::-1].index("\x7f")
    except ValueError:
        return

    visible_indices = [
        index
        for index, value in enumerate(typed[:backspace_index])
        if not value.startswith("\x1b") and value not in ("\x08", "\x7f")
    ]

    typed.pop(backspace_index)
    if 0 <= cursor < len(visible_indices):
        typed.pop(visible_indices[cursor])
    

async def insert_cursor(full: str, cursor: int) -> str:
    CURSOR_ENABLED = "\x1b[7m"
    CURSOR_DISABLED = "\x1b[27m"

    cursor = max(0, min(cursor, len(full)))
    cursor_character = full[cursor] if cursor < len(full) else " "
    
    return (
        full[:cursor]
        + CURSOR_ENABLED
        + cursor_character
        + CURSOR_DISABLED
        + full[cursor + 1:]
    )

    
async def input(prompt: str, history: list[str] | None = None, rules: list[BaseAutofillRule] | None = None):
    history = history if history is not None else []
    history = [h for h in history if h.strip() != ""]
    rules = rules if rules is not None else []

    #core setup
    stdout.write("\x1b[?25l")  # hide cursor
    stdout.write("\r" + prompt)
    stdout.flush()

    #input
    typed: list[str] = []
    last: int = 0
    skip_next: bool = False
    character = ""

    try:
        while True:
            #character = ""
            if not skip_next:
                character = await get_character()
                typed.append(character)
            skip_next = False

        
            
            display = await generate_display(typed)
            cursor = await handle_cursor(typed, display)
            display = await insert_cursor(display, cursor)

            if character in ("\x08", "\x7f"):
                await handle_backspace(typed, cursor)
                display = await generate_display(typed)
                cursor = await handle_cursor(typed, display)
                display = await insert_cursor(display, cursor)

            if last > 0:
                stdout.write(f"\r{prompt}{" " * last}")


            for rule in rules:
                raw = "".join(strip_ansi(typed))
                new_raw = rule.on_raw_character(character, raw)
                if new_raw != NotImplemented:
                    typed = (list(new_raw))
                    skip_next = True
                    
                output_display = rule.on_character(character, display)
                if output_display != NotImplemented:
                    display = colorize(output_display)

                        
            stdout.write(f"\r{prompt}{display}")
            last = len(display)


            #CHECKING IF WE SHOULD QUIT
            if character in ("\n", "\r"):
                break

    finally:
        stdout.write("\x1b[?25h") #clear
        stdout.write("\x1b[27m") #get rid of cursor
        stdout.flush()


    typed = [t for t in typed if t != "\x1b[7m"]
    final = "".join(strip_ansi(typed))
    for rule in rules:
        new = rule.on_send(final)
        if new is not NotImplemented:
            final = colorize(new)



    return strip_ansi(final)
        
async def input_o(prompt: str, history: list[str] | None = None, rules: list[AutofillRule] | None = None):
    if history == None:
        history = []
    if rules == None:
        rules = []
    typed = ""
    cursor = 0
    stdout.write("\x1b[?25l")  # hide cursor
    stdout.write("\r" + prompt)
    stdout.flush()
    old_len = 0
    display = ""
    history = [h for h in history if h.strip() != ""]
    ind = len(history)
    

    try:
        while True:
            char = await get_character()
            for rule in rules:
                if rule.text_replacement and rule.on_char is not None:
                    old_t = len(typed)
                    if not rule.on_tab:
                        typed = rule.on_char(typed)
                    elif rule.on_tab and char == "\t":
                        typed = rule.on_char(typed)
                        char = ""

                    if len(typed) - old_t > 0:
                        if rule.cancel:
                            char = ""
                        cursor += len(typed) + old_t
            if char == "\x1b[A": #UP
                ind -= 1
                if ind < 0:
                    ind = 0
                if (ind > -1 and ind < len(history)):
                    cursor = 9999999999999
                    typed = history[ind]
                char = ""
            if char == "\x1b[B": #DOWN
                ind += 1
                if ind > len(history):
                    ind = len(history)
                if ind == len(history):
                    typed = ""        # blank line after last history item
                else:
                    if (ind > -1 and ind < len(history)):
                        cursor = 9999999999999999
                        typed = history[ind]
                char = ""

            if cursor > len(typed):
                cursor = len(typed)

            if char == "\x1b[C": #RIGHT
                cursor += 1
                if cursor > len(typed):
                    cursor = len(typed)
                char = ""
            if char == "\x1b[D": #LEFT:
                cursor -=1 
                if cursor < 0:
                    cursor = 0
                char = ""
            # ENTER
            if char in ("\r", "\n"):
                for rule in rules:
                    if rule.on_char is not None:
                        display = colorize(rule.on_char(display))
                    if rule.on_send is not None:
                        display = rule.on_send(display)
                stdout.write("\r" + prompt + display + "\x1b[K")
                stdout.write("\x1b[?25h\n")  # show cursor and newline
                stdout.flush()
                break

            # BACKSPACE
            if char in ("\x08", "\x7f"):
                if cursor > 0:
                    typed = typed[:cursor-1] + typed[cursor:]
                    cursor -= 1

            # INSERT NORMAL CHAR
            else:
                typed = typed[:cursor] + char + typed[cursor:]
                cursor += len(char)

            # RENDER FRAME
            display = (
                typed[:cursor] +(typed[cursor] if cursor < len(typed) else " ")+
                typed[cursor + (1 if cursor < len(typed) else 0):]
            )


            new_disp = ""
            for index, l in enumerate(display):
                if index == cursor:
                    new_disp+=f"[[inverse]]{l}[[no inverse]]"
                else:
                    new_disp+=l
                

            for rule in rules:
                if rule.on_char != None:
                    new_disp = rule.on_char(new_disp)
            out = prompt + colorize(new_disp)
            stdout.write("\r" + out + "\x1b[K")
            old_len = len(out)
            stdout.flush()
    finally:
        stdout.write("\x1b[?25h")
        stdout.flush()
    for rule in rules:
        if rule.on_send is not None:
            typed = rule.on_send(typed)
    return typed

