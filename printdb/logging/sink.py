import os


class LogSink:
    def __init__(self, masked = False):
        self.logs = []
        self._is_redirecting = False
        self._file = None
        self._masked = masked
        pass
    def redirect_file(self, file: str, append: bool = False):
        if os.path.exists(file):
            self._is_redirecting = True
            self._file = open(file, "w" if not append else "a")
    
    def __add__(self, other):
        self.logs.append(other)
        if self._is_redirecting:
            self._file.write(other)
            self._file.flush()
        if not self._masked:
            print(other,end="")
        return self
    
    def __iadd__(self,other):
        return self.__add__(other)
    
    def read(self):
        return "".join(self.logs)