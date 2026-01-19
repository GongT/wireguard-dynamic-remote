import ipaddress
import shutil
import sys

from ..common import logger
from ..common.spawn import execute_capture


class Resolver:
    pwsh = ""

    def __init__(self) -> None:
        if sys.platform == "win32":
            self.pwsh = "pwsh" if shutil.which("pwsh") else "powershell.exe"
            self.resolver = self.resolve_powershell
            self.kind = f"{self.pwsh} Resolve-DnsName"
        else:
            self.resolver = self.resolve_dig
            self.kind = "dig"

    def resolve_powershell(self, host: str, resolver: str | None = None):
        cmd = [
            self.pwsh,
            "-Command",
            f"Resolve-DnsName -Name '{host}'",
        ]
        if resolver:
            cmd[2] += f" -Server '{resolver}'"
        cmd[2] += " | Select-Object -ExpandProperty IPAddress"

        p = execute_capture(cmd)
        s = set()
        for line in p.splitlines():
            line = line.strip()
            if line:
                s.add(line)

        return list(s)

    def resolve_dig(self, host: str, resolver: str | None = None):
        cmd = [
            "dig",
            "+short",
        ]
        if resolver:
            cmd.append(f"@{resolver}")
        cmd.extend([host, "A", host, "AAAA"])

        p = execute_capture(cmd)
        s = set()

        for line in p.splitlines():
            line = line.strip()
            if not line:
                continue

            if self.is_valid_ip(line):
                s.add(line)

        return list(s)

    def is_valid_ip(self, ip: str) -> bool:
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False


def resolve(host: str, resolver: str | None = None):
    resolver_instance = Resolver()
    addresses = resolver_instance.resolver(host, resolver)

    if len(addresses) == 0:
        logger.error(
            f"{resolver_instance.kind} did not return any addresses for host '{host}':\n{p}"
        )

    return addresses
