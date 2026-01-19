import subprocess
import sys

_indent = ""


def output(message: str):
    print(f"{_indent}{message}", file=sys.stderr, flush=True)


def error(message: str):
    print(f"\x1b[38;5;9m{_indent}{message}\x1b[0m", file=sys.stderr, flush=True)


def indent(chars="    "):
    global _indent
    _indent += chars

    return _Indenter()


class _Indenter:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        dedent()


def dedent():
    global _indent
    _indent = _indent[:-4]


def fatal(message: str):
    error(f"FATAL: {message}")
    sys.exit(1)


def check(process: subprocess.CompletedProcess, ignore=False):
    if process.returncode == 0:
        return
    if ignore:
        error(f"Command failed:")
    else:
        error(f"FATAL: Command failed:")

    cmdline = '" "'.join(process.args)
    output(f" - Command: \"{cmdline}\"")
    output(f" - Return code: {process.returncode}")
    output(f" - Output:")
    if process.stdout:
        print(process.stdout.strip(), file=sys.stderr)
    if process.stderr:
        print(process.stderr.strip(), file=sys.stderr)
    if not ignore:
        sys.exit(process.returncode)


def explode(message: str):
    error(f"程序炸了: {message}")
    raise RuntimeError(message)
