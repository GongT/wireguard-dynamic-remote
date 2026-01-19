import os
import shutil
import subprocess
import sys
from logging import error
from pathlib import Path

from ..common import logger
from ..common.spawn import execute_capture, execute_drop
from .config_parser import parse_config_content


def get_runtime_interface(interface: str):
    try:
        output = execute_capture(
            commandline=["wg", "showconf", interface],
            error="raise",
        )
    except subprocess.CalledProcessError as p:
        stderr = p.stderr.strip()
        if "No such device" in stderr:
            return None
        raise RuntimeError(f"Failed to get WireGuard interface config:\n{stderr}")

    return parse_config_content(output)


if sys.platform == "win32":
    CONFIG_FILES_DIR = Path(os.environ["ProgramData"]).joinpath("WireGuard")
else:
    CONFIG_FILES_DIR = Path("/etc/wireguard")


def get_static_interface(interface: str):
    file = CONFIG_FILES_DIR.joinpath(interface).with_suffix(".conf")
    if not file.exists():
        return None

    return parse_config_content(file.read_text())


def get_static_config_file(interface: str):
    return CONFIG_FILES_DIR.joinpath(interface).with_suffix(".conf")


def list_config_files() -> list[str]:
    logger.output(f"Listing config files in {CONFIG_FILES_DIR}")
    return [file.stem for file in CONFIG_FILES_DIR.glob("*.conf")]


def set_peer_address(interface: str, peer_public_key: str, address: str):
    execute_drop(
        ["wg", "set", interface, "peer", peer_public_key, "endpoint", address],
    )
