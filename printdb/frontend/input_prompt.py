from printdb.logging.colors import colorize
from printdb.core.command_output import CommandOutput
import os

def input_prompt() -> str:
    return colorize(f"[[green]]({os.getcwd()})[[reset]] > ")

def error(output: CommandOutput) -> str:
    code: str =colorize(f"[[red]][[bold]][ERROR {output.error_code.name}][[reset]][[red]]: {output.output}[[reset]]")
    return code