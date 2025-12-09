import os
from pathlib import Path
class OSFunctions():
    def __init__(self) -> None:
        pass
    
    def _path_to_str(self, file: Path | str):
        if isinstance(file, Path):
            return file.absolute()
        else:
            return file
    
    def read(self, file: Path | str, byt: bool = False) -> str | bytes:
        file = self._path_to_str(file)
        content = ""
        if os.path.exists(file):
            _file = open(file, "r" if not byt else "rb")
            content = _file.read()
            _file.close()
        return content

    pass

OSLib = OSFunctions()