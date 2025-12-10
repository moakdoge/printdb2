import asyncio
import sys
from printdb.logging.colors import *


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
    def log():
        if len(st) > 1:
            print("\b" * (len(st)-1), end="")
        print(colorize(f"[[red]]{st}[[reset]]"), end="", flush=True)
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

        st += ch
        log()
