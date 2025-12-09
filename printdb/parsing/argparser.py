import inspect
import os
import pathlib
from printdb.core.exceptions import *
import json5
from printdb.core.command import Command
from typing import Any


def convert_str(s: str):
    nones = ["none", "null", "NaN"]
    allowed_trues = ["true", "yes"]
    allowed_falses = ["false", "no"]
    def is_float(s: str) -> bool:
        try:
            float(s)
            return True
        except ValueError:
            return False
    def is_int(s: str) -> bool:
        try:
            int(s)
            return True
        except ValueError:
            return False
    def is_bool(s: str) -> bool:
        if s.lower() in allowed_trues or s.lower() in allowed_falses:
            return True
        return False

    def is_none(s: str) -> bool:
        return s in nones
    
    def is_json(s: str) -> bool:
        try:
            m = json5.loads(s)   
            return True
        except Exception as e:
            return False 
    def is_path(s: str) -> bool:
        if os.path.exists(s):
            return True
        return False

        
    if is_int(s):
        return int(s)
    if is_float(s):
        return float(s)
    if is_bool(s):
        if s.lower() in allowed_trues:
            return True
        else:
            return False
    if is_none(s):
        return None
    if is_json(s):
        return json5.loads(s)
    if is_path(s):
        return pathlib.Path(s)
    
    
    return s
def type_check_args(command: Command, args: list) -> list[Any]:
    new_args = []
    for arg in args:
        new_args.append(convert_str(arg))
    args = new_args

    sig = inspect.signature(command.func)


    params = list(sig.parameters.values())[1:]  # skip self, ctx

    typed = []
    provided = args
    pi = 0
    ai = 0

    while pi < len(params):
        p = params[pi]
        name = p.name
        annotation = p.annotation
        default = p.default
        variadic = (p.kind == inspect.Parameter.VAR_POSITIONAL)

        if annotation is inspect._empty:
            annotation = str

        if variadic:
            typed.extend(provided[ai:])
            ai = len(provided)
            break

        if ai >= len(provided):
            if default is not inspect._empty:
                typed.append(default)
                pi += 1
                continue
            raise MissingParam(f"Missing required argument '{name}'")

        val = provided[ai]

        try:
            if not isinstance(val, annotation):
                if default is inspect._empty:
                    raise InvalidParamType(
                        f"Argument '{name}' expected {annotation}, "
                        f"got {type(val)} ({val})"
                    )
                else:  # optional param
                    pi += 1
                    typed.append(default)
                    continue
        except TypeError:
            pass

        typed.append(val)
        ai += 1
        pi += 1

    return typed
