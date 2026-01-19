import os

import sdnotify

_notify = sdnotify.SystemdNotifier()


def sd_notify(message: str):
    _notify.notify(message)


def ready():
    sd_notify("READY=1")


def status(message: str):
    sd_notify(f"STATUS={message}")

def watchdog():
    sd_notify("WATCHDOG=1")
