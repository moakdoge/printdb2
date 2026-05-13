import re, random
import time, asyncio
ABC = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
def randomized_text(le: int) -> str:
    return "".join([random.choice(ABC) for _ in range(le)])
COLOR_ENABLED = True
def colorize(text: str) -> str:
    COLOR_CODES_FG = {
        "reset": "\033[0m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    }
    COLOR_CODES_BG = {
        "reset": "\033[0m",
        "red": "\033[41m",
        "green": "\033[42m",
        "yellow": "\033[43m",
        "blue": "\033[44m",
        "magenta": "\033[45m",
        "cyan": "\033[46m",
        "white": "\033[47m",
    }
    COLOR_CODES_GENERIC = {
        "bold": "\033[1m",     # style, not color
        "no bold": "\x1b[2m",

        "inverse": "\x1b[7m",  # swaps fg/bg
        "no inverse": "\x1b[27m",

        "underline": "\x1b[4m",
        "no underline": "\x1b[24m",
        
        "strike": "\x1b[9m",
        "no_strike": "\x1b[29m",

        "italic": "\x1b[3m",
        "no italic": "\x1b[23m",
        
        "blink": "\x1b[5m",
        "no blink": "\x1b[25m",

        "hidden": "\x1b[8m",
        "reveal": "\x1b[28m",
        "visible": "\x1b[28m",
        "no hidden": "\x1b[28m",
    }

    def replace_tag(match):
        tag = match.group(1)

        if not COLOR_ENABLED:
            return ""
        if not tag:
            return match.group(0)
        tag = tag.lstrip().rstrip()
        if tag.startswith("fg"):
            tag = tag.removeprefix("fg")
            s = "38"
        elif tag.startswith("bg"):
            tag = tag.removeprefix("bg")
            s = "48"
        else:
            s="38"
        tag = tag.lstrip().rstrip()
        if tag.startswith("(") and tag.endswith(")"):
            rgb = tag.replace(" ", "").lstrip("(").rstrip(")").split(",")
            rgb = [max(0, min(255, int(_))) for _ in rgb]
            if len(rgb) < 3:
                return match.group(1)
            else:
                return f"\x1b[{s};2;{rgb[0]};{rgb[1]};{rgb[2]}m"
        if tag.startswith("!"):
            tag=tag.removeprefix("!")
            if tag.startswith("random"):
                try:
                    return randomized_text(int(tag.removeprefix("random").strip().replace("_","").replace(" ","")))
                except ValueError:
                    return randomized_text(int(12))
            elif tag.startswith("delay"): #idk who thought of this lmao
                try:
                    time.sleep(float(tag.removeprefix("delay").strip().replace("_","").replace(" ","")))
                    return ""
                except ValueError:
                    return ""

        if s == "38":
            return COLOR_CODES_FG.get(tag, COLOR_CODES_GENERIC.get(tag, ""))
        elif s == "48":
            return COLOR_CODES_BG.get(tag, COLOR_CODES_GENERIC.get(tag, ""))
        return COLOR_CODES_FG.get(tag, COLOR_CODES_GENERIC.get(tag, '')) 
    
    return re.sub(r'\[\[([^\[\]]+)\]\]', replace_tag, text) # type: ignore


def highlight_tags(text: str, color: str):
    def replace_tag(match):
        nonlocal color
        return f"{colorize(color)}{match.group(0)}{colorize("[[white]]")}"
    return re.sub(r'\[\[([^\[\]]+)\]\]', replace_tag, text)