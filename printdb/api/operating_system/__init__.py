import os
from pathlib import Path
class OSFunctions():
    def __init__(self) -> None:
        self._path = Path(os.getcwd())
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

    def list_dir(self, path: Path | None = None) -> list[Path]:
        if path is None:
            path = self._path
        return [Path(f) for f in os.listdir(path.expanduser().resolve().absolute())]
    
    def list_files(self, path: Path | None = None):
        return sorted([f for f in self.list_dir(path) if f.is_file()])

    def list_folders(self, path: Path | None = None):
        return sorted([f for f in self.list_dir(path) if f.is_dir()])
    
    def is_executable(self, path: Path | None = None):
        if path is None:
            path = self._path

        if not path.exists():
            return False
        
        return (path.is_file() and os.access(str(path.absolute()), os.X_OK))

    pass

OSLib = OSFunctions()