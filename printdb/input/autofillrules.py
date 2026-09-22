import re

from printdb.api import colorize



class BaseAutofillRule:
    def on_character(self, char: str, full: str) -> str:
        '''
            Returns: the display text.
        '''
        return NotImplemented

    def on_raw_character(self, char: str, full: str) -> str:
        '''
            Returns: the raw text, so what the user typed.
        '''
        return NotImplemented

    def on_send(self, full: str) -> str:
        '''
            Returns: the FINAL text sent back to the user
        '''
        return NotImplemented


class RegexAutofillRule(BaseAutofillRule):
    def __init__(self, regex: str | re.Pattern, replacement: str, send: bool = False) -> None:
        self.send = send
        self.regex = regex if isinstance(regex, re.Pattern) else re.compile(regex)
        self.replacement = replacement

    def on_character(self, char: str, full: str) -> str:
        from printdb.input.async_input import strip_ansi

        full = strip_ansi(full)

        def repl(match):
            if "%s" in self.replacement:
                return self.replacement % match.group(0)
            else:
                return self.replacement

        subbed = re.sub(self.regex, repl, full) 
        if subbed == full:
            return NotImplemented
        return subbed
    

class HintAutofillRule(BaseAutofillRule):
    def __init__(self, start: str, options: list[str]) -> None:
        self.start = start
        self.options = options

        self._last_autofilled: str | None = None

    def on_character(self, char: str, full: str) -> str:
        from printdb.input.async_input import strip_ansi
        raw = strip_ansi(full).rstrip(" \t")
        start = "".join(self.start)

        if not raw.startswith(start):
            self._last_autofilled = None
            return NotImplemented

        typed_option = raw[len(start):]


        if typed_option == "":
            self._last_autofilled = None
            return NotImplemented

        typed_option = typed_option.strip()
        for option in self.options:
            if option.startswith(typed_option) and typed_option != option:
                self._last_autofilled = option
                return f"{raw}\x1b[90m{option[len(typed_option):]}\033[0m"

        self._last_autofilled = None
        return NotImplemented

    def on_raw_character(self, char: str, full: str) -> str:
        if char == "\t" and self._last_autofilled:
            start = self.start
            o = full[len(self.start):]

            space_count = len(o) - len(o.lstrip(" "))
            return f"{start}{" "*space_count}{self._last_autofilled}"
        return NotImplemented