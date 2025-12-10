import asyncio
import sys
from printdb.logging.colors import *
from printdb.parsing.tokenizer import *
import printdb.api as api


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

async def input(prompt: str) -> str:
    st = ""
    cursor = -1
    def log():
        nonlocal st, cursor
        cmd, args = tokenize_args(st)
        if len(st) > 1:
            print("\b" * (len(st)-1), end="")
        if api.manager.get_command(cmd):
            raw = st.replace(cmd, f"[[green]]{cmd}[[red]]")
        else:
            raw = st
        cursor = len(st) -1
       # raw = raw[:cursor] + "[[inverse]]" + raw[cursor] + "[[reset]][[red]]" + raw[cursor+1:]
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
                print("\b \b", end="", flush=True)
            continue
        if ch == "\x1b[A": #up
            pass
        elif ch == "\x1b[B": #down
            pass
        
        if ch == "\x1b[C": #right
            cursor+= 1
            if cursor > len(ch):
                cursor = len(ch)
            continue
        if ch == "\x1b[D": #left
            cursor-= 1
            if cursor < 0:
                cursor = 0
            continue
        st += ch
        cursor += len(ch)
        log()
