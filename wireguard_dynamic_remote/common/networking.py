import platform
import subprocess


def ping_each_ip(addresses: list[str]) -> str | None:
    """Ping each IP address in the list and return the first one that responds in 5 seconds."""

    if platform.system() == "Windows":
        ping_cmd = ["ping", "-n", "1", "-w", "5000"]  # Windows ping command
    else:
        ping_cmd = ["ping", "-c", "1", "-W", "5"]  # Unix-like ping command

    ps: dict[str, subprocess.Popen] = {}
    for address in addresses:
        # run pings in parallel, race them
        process = subprocess.Popen(
            ping_cmd + [address],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
        ps[address] = process

    found = wait_for_processes(ps)
    kill_all(ps)

    return found


def wait_for_processes(ps: dict[str, subprocess.Popen]):
    # 检查已完成的进程
    while True:
        for address, process in ps.items():
            return_code = process.poll()
            if return_code is None:  # 进程还在运行时，poll() 返回 None
                continue

            # 如果成功 ping 通，则返回地址
            if return_code == 0:
                return address

            # 否则，检查下一个

        # 检查是全不通还是有进程没结束
        all_done = all(p.poll() is not None for p in ps.values())
        if all_done:  # 全不通
            return None


def kill_all(ps: dict[str, subprocess.Popen]):
    # kill 其他仍在运行的进程
    for p in ps.values():
        if p.poll() is not None:
            continue

        try:
            p.kill()
        except ProcessLookupError:
            pass  # 进程可能已经结束
