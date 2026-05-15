from dataclasses import dataclass


@dataclass(slots=True)
class BaseOperand:
    symbol: str = ""
    slot1: str = ""
    slot2: str = ""

@dataclass(slots=True)
class ANDOperand(BaseOperand):
    symbol: str = "and"
    
@dataclass(slots=True)
class OROperand(BaseOperand):
    symbol: str = "or"

@dataclass(slots=True)
class NOTOperand(BaseOperand):
    symbol: str = "not"
    
    
OPERANDS = BaseOperand.__subclasses__()

def get_operand(op: str, slot1: str, slot2: str) -> BaseOperand | None:
    for _o in BaseOperand.__subclasses__():
        if _o.symbol == op:
            return _o(_o.symbol, slot1, slot2)
    return None

class BaseBool:
    content: str


