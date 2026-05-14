import shlex, re
from typing import Literal
from printdb.core.exceptions import *

from dataclasses import dataclass

@dataclass
class EmbeddedToken:
    contents: list["EmbeddedToken"] | str
    type: Literal["text", "template"]

    @classmethod
    def text(cls, cnts: str):
        return cls(cnts, "text")

    @classmethod
    def template(cls, cnts: str):
        # cnts should ONLY be the inner contents,
        # not the surrounding ${ ... }
        return cls(_extract_embedded(cnts), "template")


def _extract_embedded(text: str) -> list[EmbeddedToken]:
    tokens: list[EmbeddedToken] = []

    i = 0
    buf: list[str] = []

    def flush_text():
        if buf:
            tokens.append(EmbeddedToken.text("".join(buf)))
            buf.clear()

    while i < len(text):
        ch = text[i]

        # Handle quoted strings outside templates
        if ch in ("'", '"'):
            quote = ch
            buf.append(ch)
            i += 1

            escape = False

            while i < len(text):
                c = text[i]
                buf.append(c)

                if escape:
                    escape = False

                elif c == "\\":
                    escape = True

                elif c == quote:
                    i += 1
                    break

                i += 1

            continue

        # Template start
        if text[i:i + 2] == "${":
            flush_text()

            start = i
            i += 2
            depth = 1

            while i < len(text) and depth:
                ch = text[i]

                # Skip quoted strings INSIDE templates
                if ch in ("'", '"'):
                    quote = ch
                    i += 1

                    escape = False

                    while i < len(text):
                        c = text[i]

                        if escape:
                            escape = False

                        elif c == "\\":
                            escape = True

                        elif c == quote:
                            i += 1
                            break

                        i += 1

                    continue

                # Nested template
                if text[i:i + 2] == "${":
                    depth += 1
                    i += 2
                    continue

                # Closing brace
                if ch == "}":
                    depth -= 1

                i += 1

            # Extract ONLY inner contents
            inner = text[start + 2:i - 1]

            tokens.append(EmbeddedToken.template(inner))
            continue

        buf.append(ch)
        i += 1

    flush_text()
    return tokens
def tokensize_redirects(s: str):
    split = shlex.split(s)
    if ">" in split:
        c= ">"
    elif ">>" in split:
        c= ">>"
    else:
        return (s, None, None)
     
    if split.index(c)+1 > len(split):
        raise InvalidRedirect("Please provide a file!")
    file = split[split.index(c)+1]
    append = "a" if c == ">>" else "w"
    return (" ".join(split[0:split.index(c)]), append, file)

def tokenize_pipes(s: str):
    split = shlex.split(s)
    if not "|" in split: 
        return [s]
    pipes = []
    current_st = ""
    for v in split:
        if v == "|":
            pipes.append(current_st.rstrip(" "))
            current_st = ""
        else:
            if " " in v: #meaning we need an embedded quote
                v = f'"{v}"'
            current_st += v + ' '
    pipes.append(current_st.rstrip(" "))
    return pipes

def tokenize_args(s: str) -> tuple[str, list[str]]:
    if s.startswith('"') and s.endswith('"'):
        s = s.lstrip('"').rstrip('"')
    tokens = []
    current = []
    depth = 0
    in_single = False
    in_double = False

    for c in s:

        if c == "'" and not in_double:
            in_single = not in_single
            current.append(c)
            continue


        if c == '"' and not in_single:
            in_double = not in_double
            current.append(c)
            continue


        if not in_single and not in_double:
            if c in "{[":
                depth += 1
            elif c in "}]":
                depth -= 1


        if c.isspace() and depth == 0 and not in_single and not in_double:
            if current:
                tokens.append("".join(current))
                current = []
            continue

        current.append(c)

    if current:
        tokens.append("".join(current))

    if not tokens:
        return ("", [])
    return tokens[0], tokens[1:]
