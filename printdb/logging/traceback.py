
import linecache
from . import colors


def trace_error(er):
    tb = er.__traceback__
    while tb.tb_next:
        tb = tb.tb_next
    filename = tb.tb_frame.f_code.co_filename
    lineno = tb.tb_lineno
    linecache.checkcache(filename) #fuck you.
    code = linecache.getline(filename, lineno).strip()
    ty = type(er).__name__
    return colors.colorize(f"[[red]]{ty} raised @ Line {lineno}\n\tFile {filename}\n\t{code} <--- [HERE]\n{er}[[reset]]")
