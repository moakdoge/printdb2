from typing import Any
class Arg():
    def __init__(self, name: str, ty: type, default: Any, optional: bool = False) -> None:
        self.name = name
        self.type = ty
        self.default = default
        self.optional = optional
        pass