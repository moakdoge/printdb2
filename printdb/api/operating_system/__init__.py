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
    
    def chunked_read(self, file: Path | str, mode: str = "r", size: int = 1024):
        with open(file, mode) as f:
            while True:
                data = f.read(size)
                if not data:
                    break
                yield data


    def read(self, file: Path | str, byt: bool = False) -> str | bytes:
        file = self._path_to_str(file)
        content = ""
        if os.path.exists(file):
            _file = open(file, "r" if not byt else "rb")
            content = _file.read()
            _file.close()
        return content


    def change_dir(self, path: Path):
        target = path.expanduser().resolve()

        if not target.exists():
            raise FileNotFoundError(f"Path {target} does not exist.")
        if not target.is_dir():
            raise NotADirectoryError(f"{target} is not a directory.")

        os.chdir(target)
        self._path = target

    def list_dir(self, path: Path | None = None) -> list[Path]:
        if path is None:
            path = self._path
        return [Path(f) for f in os.listdir(path.expanduser().resolve().absolute())]
    
    def list_files(self, path: Path | None = None):
        files = []
        for f in self.list_dir(path):
            try:
                if f.is_file():
                    files.append(f)
            except PermissionError:
                continue
        return sorted(files)

    def list_folders(self, path: Path | None = None):
        folders = []
        for f in self.list_dir(path):
            try:
                if f.is_dir():
                    folders.append(f)
            except PermissionError:
                continue
        return sorted(folders)

    
    def is_executable(self, path: Path):
        if not path.exists():
            return False
        
        return (path.is_file() and os.access(str(path.absolute()), os.X_OK))

    pass

OSLib = OSFunctions()