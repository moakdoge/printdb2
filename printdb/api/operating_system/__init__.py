import os, asyncio
from pathlib import Path
class OSFunctions():
    def __init__(self) -> None:
        pass
    
    def _path_to_str(self, file: Path | str) -> str:
        if isinstance(file, Path):
            return str(file.absolute())
        else:
            return file
    

    def _read(self, file: str, by: bool = False):
        with open(file, "r" if not by else "rb") as m:
            return m.read(1_000_000_000)
        
    async def read(self, file: Path | str, byt: bool = False) -> str | bytes:
        fi = self._path_to_str(file)
        content = ""
        if os.path.exists(fi):
            content = await asyncio.to_thread(self._read, fi, byt)
        return content
    
    async def read_chunks(self, fi: Path | str, by: bool = False, chunk_size: int = 4096, max_bytes: int | None = None):
        mode = "rb" if by else "r"
        read = 0
        file = self._path_to_str(fi)
        if not os.path.exists(fi):
            raise FileNotFoundError("File not found")
        with open(file, mode) as m:
            while True:
                if max_bytes is not None:
                    remaining = max_bytes - read
                    if remaining <= 0:
                        break
                    data = m.read(min(chunk_size, remaining))
                else:
                    data = m.read(chunk_size)

                if not data:
                    break

                read += len(data)
                yield data


    pass

OSLib = OSFunctions()