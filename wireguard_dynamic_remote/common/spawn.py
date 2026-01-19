import subprocess
import sys
from tabnanny import check
from typing import Literal

from . import logger

type ErrorBehavior = Literal["ignore", "print", "raise", "fatal"]


def execute_print(
    commandline: list[str],
) -> None:
    subprocess.run(
        commandline,
        check=False,
        stdout=sys.stderr,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
    )


def execute_drop(commandline: list[str], error: ErrorBehavior = "fatal") -> None:
    _execute(commandline, capture=False, error=error)


def execute_capture(commandline: list[str], error: ErrorBehavior = "fatal") -> str:
    """
    运行命令并返回结果

    如果失败:
        如果error为"fatal", 则输出错误并退出程序
        如果error为"print", 则输出错误并继续（返回空字符串）
        如果error为"ignore", 则继续（返回空字符串）
        如果error为"raise", 则抛异常

    """
    output = _execute(commandline, capture=True, error=error)
    assert output is not None
    return output


def _execute(commandline: list[str], capture=False, error: ErrorBehavior = "fatal"):
    p = subprocess.run(
        commandline,
        check=error == "raise",
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE if capture else subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
    )

    if error == "fatal":
        logger.check(p)
    elif error == "print":
        logger.check(p, ignore=True)

    if capture:
        if p.returncode == 0:
            return p.stdout.strip()
        else:
            return ""

    return None
