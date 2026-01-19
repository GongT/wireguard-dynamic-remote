from pathlib import Path

from ..wireguard import get_static_config_file, list_config_files
from . import logger


class RunContext:
    def __init__(
        self, interfaces: list[str], interval: int, resolver: None | str = None
    ):
        self.interfaces = interfaces or []
        self.interval = interval
        self.resolver = resolver

    def validate(self, check_interfaces: bool = False, expand_interfaces: bool = False):
        if self.interval < 30:
            logger.fatal(f"Interval must be at least 30 seconds, got {self.interval}")
        elif self.interval > 30 * 60:
            logger.fatal(f"Interval must be at most 30 minutes, got {self.interval}")

        if not self.interfaces or len(self.interfaces) == 0:
            if expand_interfaces:
                self.interfaces = list_config_files()
        else:
            if check_interfaces:
                self.check_interfaces()

    def check_interfaces(self):
        for interface in self.interfaces:
            path = get_static_config_file(interface)
            if not path.exists():
                logger.fatal(f"Missing file: {path}")

    def rebuild_arguments(self):
        args = []
        for interface in self.interfaces:
            args.extend(["--interface", interface])

        if self.resolver:
            args.extend(["--resolver", self.resolver])
        return args
