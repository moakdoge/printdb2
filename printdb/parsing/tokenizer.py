
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
