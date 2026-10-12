# printdb2
## An attempt to recreate a POSIX compliant shell in pure python.

# Overview
printdb2 is a CLI designed to where all commands are plugin-focused. Plugins are written in Python.

# Features
* All commands are written in fully async, thread-safe Python.
* Allows on-the-fly loading of plugins.
* Supports creating a `~/.printdb.cmd` file, similar to `~/.bashrc` or `~/.zshrc`.
* Full syntax highlighting and autofill.
* Fully supports piping, redirecting to a file, and background tasks.
* No reliance on any non-standard Python libraries.

# Disclaimer
This program is in **early development**. There almost certainly be bugs or major issues. Please report these to me as a pull requests or issue.

# Install
```bash
> git clone https://github.com/moakdoge/printdb2.git
> cd printdb2
> python3 front_end.py
```
