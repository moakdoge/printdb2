import asyncio
import sys
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

async def input(prompt: str, history: list[str] | None = None):
    if history == None:
        history = []
    typed = ""
    cursor = 0
    stdout.write("\x1b[?25l")  # hide cursor
    stdout.write("\r" + prompt)
    stdout.flush()
    old_len = 0
    display = ""
    history = [h for h in history if h.strip() != ""]
    ind = len(history)

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
    while True:
        char = await get_character()

        if char == "\x1b[A": #UP
            ind -= 1
            if ind < 0:
                ind = 0
            typed = history[ind]
            char = ""
        if char == "\x1b[B": #DOWN
            ind += 1
            if ind > len(history):
                ind = len(history)
            if ind == len(history):
                typed = ""        # blank line after last history item
            else:
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
                new_disp+=f"[[inverse]]{l}[[reset]]"
            else:
                new_disp+=l
            

        out = prompt + colorize(new_disp)
        stdout.write("\r" + out + "\x1b[K")
        old_len = len(out)
        stdout.flush()
    return typed

