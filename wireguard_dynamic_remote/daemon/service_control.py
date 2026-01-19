import sys

from ..common import logger
from ..common.spawn import execute_drop
from ..systemd import systemctl


def start_service_inner(interface: str, nonce: str):
    if sys.platform == "win32":
        win32_service_start(interface, nonce)
    else:
        systemctl.start(f"wg-quick@{interface}.service", nonce == "restart")


def cross_platform_start_service(interface: str, nonce="start"):
    try:
        start_service_inner(interface, nonce)
    except Exception as e:
        logger.output(f"(ignore) Error starting service: {e}")
        pass
    return


def win32_service_start(interface: str, nonce: str):
    if nonce == "restart":
        nonce = 'Restart'
    elif nonce == "start":
        nonce = 'Start'
    else:
        logger.explode("Invalid nonce")
        
    execute_drop(
        ["powershell.exe", "-Command", f"{nonce}-Service 'WireGuardTunnel$vpn{interface}'"],
        error="print",
    )
