import shlex
from printdb.core.exceptions import *
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
