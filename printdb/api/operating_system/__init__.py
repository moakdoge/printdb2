import os
class OSFunctions():
    def __init__(self) -> None:
        pass
    def read(self, file: str, byt: bool = False) -> str | bytes:
        content = ""
        if os.path.exists(file):
            _file = open(file, "r" if not byt else "rb")
            content = _file.read()
            _file.close()
        return content

    pass

OSLib = OSFunctions()