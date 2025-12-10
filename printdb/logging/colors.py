import re

def colorize(text: str) -> str:
    COLOR_CODES = {
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
    def replace_tag(match):
        tag = match.group(1)
        return COLOR_CODES.get(tag, match.group(0)) 
    return re.sub(r'\[\[(.*?)\]\]', replace_tag, text)
