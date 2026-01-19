import argparse
import sys

from wireguard_dynamic_remote.common import logger

from .common.context import RunContext


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--interface",
        action="append",
        help="WireGuard (wg-quick) interface names",
    )
    parser.add_argument(
        "--interval",
        type=str,
        default="60s",
        help="Interval (in seconds) to check for IP changes",
    )
    parser.add_argument(
        "--resolver",
        type=str,
        default=None,
        help="Custom DNS resolver to use for domain resolution",
    )
    parser.add_argument(
        "action",
        choices=["start", "install", "uninstall"],
        help="Action to perform",
    )
    args = parser.parse_args()

    # detect interval is number
    input_interval: str = args.interval
    interval = 0
    if input_interval.isdigit():
        interval = int(input_interval)
    else:
        from .systemd.tools import parse_timespan

        interval = parse_timespan(input_interval)

    config = RunContext(args.interface, interval, args.resolver)

    if args.action == "start":
        from .daemon import daemon_main

        config.validate(check_interfaces=True, expand_interfaces=True)
        daemon_main(config)
    elif args.action == "install":
        config.validate(check_interfaces=True, expand_interfaces=False)

        if sys.platform == "linux":
            from .systemd.control import install_service

            install_service(config)

        elif sys.platform == "win32":
            logger.fatal("Win32 service is not supported at this time.")
        else:
            logger.fatal(f"Unsupported platform: {sys.platform}.")

    elif args.action == "uninstall":
        if sys.platform == "linux":
            from .systemd.control import uninstall_service

            uninstall_service()

        elif sys.platform == "win32":
            logger.fatal("Win32 service is not supported at this time.")
        else:
            logger.fatal(f"Unsupported platform: {sys.platform}.")

    else:
        raise ValueError("Invalid action")


if __name__ == "__main__":

    if sys.platform == "linux":
        import os

        if os.geteuid() != 0:
            print("You need to run this command as root to install the service.")
            sys.exit(1)

    main()
