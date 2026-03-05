#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

cwd = Path(__file__).parent


def poetry_install():
    p = subprocess.run(
        ["poetry", "install"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
    )
    if p.returncode == 0:
        print("Poetry dependencies installed successfully.", file=sys.stderr)
    else:
        print(p.stderr, file=sys.stderr)
        print("Error installing Poetry dependencies", file=sys.stderr)
        sys.exit(1)


def find_poetry_env_path():
    result = subprocess.run(
        ["poetry", "env", "info", "-e"],
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        text=True,
        cwd=cwd,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    print(result.stderr, file=sys.stderr)
    print("Error finding Poetry environment path:", file=sys.stderr)
    sys.exit(1)


def spawn_process(command: list[str]):
    p = subprocess.run(
        [python_bin, "-m", "wireguard_dynamic_remote.binary", *command],
        stdout=sys.stdout,
        stderr=sys.stderr,
        cwd=cwd,
    )
    if p.returncode != 0:
        print(
            f"Error running the main process (return {p.returncode})", file=sys.stderr
        )
        sys.exit(1)


poetry_install()
python_bin = find_poetry_env_path()
print(f"using python: {python_bin}", file=sys.stderr)

spawn_process(sys.argv[1:])
