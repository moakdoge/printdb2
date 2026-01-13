import re

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
        "bold": "\033[1m",
        "inverse": "\x1b[7m"
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
        "bold": "\033[1m",     # style, not color
        "inverse": "\x1b[7m",  # swaps fg/bg
    }

    def replace_tag(match):
        tag = match.group(1)
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
        if s == "38":
            return COLOR_CODES_FG.get(tag, match.group(0))
        elif s == "48":
            return COLOR_CODES_BG.get(tag, match.group(0))
        return COLOR_CODES_FG.get(tag, match.group(0)) 
    
    return re.sub(r'\[\[(.*?)\]\]', replace_tag, text) # type: ignore
