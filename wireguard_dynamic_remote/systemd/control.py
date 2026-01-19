import subprocess
import sys
from os import environ
from pathlib import Path

from ..common import logger
from ..common.context import RunContext
from ..common.spawn import execute_drop
from . import systemctl

SYSTEMD_SERVICE_NAME = "wireguard-dynamic-remote"
SYSTEMD_LOCAL_SERVICE_LOCATION = "/usr/local/lib/systemd/system"


IS_STARTED_BY_SYSTEMD = environ.get("INVOCATION_ID") is not None
STATE_DIR = (
    IS_STARTED_BY_SYSTEMD
    and environ.get("STATE_DIRECTORY")
    or f"/var/lib/{SYSTEMD_SERVICE_NAME}"
)


def make_service(config: RunContext) -> str:
    service_args = ""
    for arg in config.rebuild_arguments():
        service_args += f' \\\n\t\t"{arg}"'

    return f"""[Unit]
Description=WireGuard Dynamic Remote Change Detecter
After=network.target
Requires={SYSTEMD_SERVICE_NAME}.timer

[Service]
Type=oneshot
User=root
ExecStart={sys.executable} -m wireguard_dynamic_remote.binary start {service_args}
Restart=no
RemainAfterExit=no
NotifyAccess=all
ProtectSystem=strict
ProtectHome=read-only
StateDirectory={SYSTEMD_SERVICE_NAME}
"""


def make_timer(config: RunContext) -> str:
    return f"""[Unit]
Description=WireGuard Dynamic Remote Change Detecter Timer
After=network.target

[Install]
WantedBy=timers.target

[Timer]
OnBootSec=5min
OnUnitActiveSec={str(config.interval)}s
"""


def write_on_change(path: Path, content: str) -> bool:
    if path.exists():
        existing_content = path.read_text()
        if existing_content == content:
            return False
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return False

    path.write_text(content)
    return True


def _services():
    output_file = Path(SYSTEMD_LOCAL_SERVICE_LOCATION, SYSTEMD_SERVICE_NAME)
    service_file = output_file.with_suffix(".service")
    timer_file = output_file.with_suffix(".timer")
    return service_file, timer_file


def install_service(config: RunContext):
    service_file, timer_file = _services()

    something_modified = False

    logger.output(f"Installing service to {service_file.parent}")

    something_modified |= write_on_change(service_file, make_service(config))
    something_modified |= write_on_change(timer_file, make_timer(config))

    logger.output(f"Service files installed successfully")

    if not something_modified:
        logger.output("No changes made")
    else:
        logger.output("Reloading systemd daemon")
        systemctl.daemon_reload()

    logger.output("Enabling and starting timer")
    execute_drop(
        ["systemctl", "enable", f"{SYSTEMD_SERVICE_NAME}.timer"],
    )

    systemctl.start(f"{SYSTEMD_SERVICE_NAME}.timer", True)
    systemctl.print_status(
        f"{SYSTEMD_SERVICE_NAME}.service", f"{SYSTEMD_SERVICE_NAME}.timer"
    )


def uninstall_service():
    service_file, timer_file = _services()

    systemctl.reset_failed(service_file.name)
    systemctl.disable(timer_file.name)

    changed = False
    if service_file.exists():
        service_file.unlink()
        changed = True
    if timer_file.exists():
        timer_file.unlink()
        changed = True

    if changed:
        systemctl.daemon_reload()

    logger.output("Service files uninstalled successfully")
