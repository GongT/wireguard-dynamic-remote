import subprocess
import sys

from ..common.spawn import execute_capture


def parse_timespan(timespan: str) -> int:
    p = execute_capture(
        ["systemd-analyze", "timespan", timespan],
    )

    for line in p.splitlines():
        if line.strip().startswith("μs:"):
            us = int(line.split(":")[1].strip())
            return int(us / 1000 / 1000)  # to seconds

    raise ValueError(f"Cannot parse timespan: {timespan}")
