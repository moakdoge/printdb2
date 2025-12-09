from enum import IntEnum

class ErrorCode(IntEnum):
    SUCCESS=0
    GENERIC_ERROR=1
    MISSING_PARAM=2
    INVALID_PARAM_TYPE=3
    COMMAND_NOT_FOUND=4


class CommandOutput():
    def __init__(self, output: str, error_code: ErrorCode) -> None:
        self.output = output
        self.error_code = error_code
