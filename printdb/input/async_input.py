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

    
async def ainput(prompt: str, history: list[str] | None = None, rules: list[BaseAutofillRule] | None = None):
    '''
       An async, fully autofill-compatible input system. 
    '''
    
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
    index = len(history)

    while True:
        #character = ""
        if not skip_next:
            character = await get_character()
            typed.append(character)
        skip_next = False

        
        #CHECKING IF WE SHOULD QUIT
        if character in ("\n", "\r"):
            typed.pop(-1)
            display = await generate_display(typed)
            new = "".join(strip_ansi(typed))
            display = display.strip("\x1b[7m")
            stdout.write(f"\r\x1b[27m")
            stdout.write(prompt + display)
            stdout.write(" ")
            break

        match character:
            case "\x1b[A": #UP 
                index -= 1

                if index < 0:
                    index = 0

                if history:
                    typed = list(history[index])
                    character = ""
                    skip_next = True
                    continue
            case "\x1b[B": #DOWN
                index += 1
                if index > len(history):
                    index = len(history)
                typed = list(history[index]) if index < len(history) else []
                character = ""
                skip_next = True
                continue

            case _:
                pass
                
        
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
                character = ""
                skip_next = True
                
            output_display = rule.on_character(character, display)
            if output_display != NotImplemented:
                display = colorize(output_display)

                    
        stdout.write(f"\r{prompt}{display}")
        last = len(display)


    stdout.write("\x1b[?25l") #keep cursor hidden
    stdout.write("\x1b[27m\n") #get rid of cursor
    stdout.flush()


    typed = [t for t in typed if t != "\x1b[7m"]
    final = "".join(strip_ansi(typed))
    for rule in rules:
        new = rule.on_send(final)
        if new is not NotImplemented:
            final = colorize(new)
            
    return strip_ansi(final).strip("\n")
