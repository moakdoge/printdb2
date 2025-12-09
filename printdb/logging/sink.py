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
            self._file = open(file)
    
    def __add__(self, other):
        self.logs.append(other)
        if self._is_redirecting:
            self._file.write(other)
            self._file.flush()
        if self._masked:
            return
        print(other,end="")
    
    def read(self):
        return "".join(self.logs)