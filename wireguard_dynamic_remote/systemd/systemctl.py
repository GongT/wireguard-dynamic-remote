from ..common.spawn import execute_drop, execute_print


def start(service: str, restart: bool = False):
    execute_drop(
        ["systemctl", "restart" if restart else "start", service], error="print"
    )


def print_status(*service: str):
    execute_print(["systemctl", "status", "--no-block", *service])


def daemon_reload():
    execute_drop(["systemctl", "daemon-reload"], error="print")


def disable(service: str):
    execute_drop(["systemctl", "disable", "--now", service], error="ignore")


def reset_failed(service: str):
    execute_drop(["systemctl", "reset-failed", service], error="ignore")
