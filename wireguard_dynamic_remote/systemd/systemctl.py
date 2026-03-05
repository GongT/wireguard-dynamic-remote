from ..common.spawn import execute_drop, execute_print


def start(*services: str, restart: bool = False):
    execute_drop(
        ["systemctl", "restart" if restart else "start", *services], error="print"
    )

def stop(*services: str):
    execute_drop(["systemctl", "stop", *services], error="print")

def print_status(*services: str):
    execute_print(["systemctl", "status", "--no-block", *services])


def daemon_reload():
    execute_drop(["systemctl", "daemon-reload"], error="print")


def disable(*services: str, now: bool = True):
    if now:
        services = ("--now", *services)
    execute_drop(["systemctl", "disable", *services], error="ignore")


def reset_failed(*services: str):
    execute_drop(["systemctl", "reset-failed", *services], error="ignore")
