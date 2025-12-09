from . import colors
from typing import Any

def prettyify(content: Any):
    if isinstance(content, str):
        content = colors.colorize(content)
    return content