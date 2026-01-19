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
        process = subprocess.Popen(ping_cmd + [address], stdout=subprocess.PIPE)
        ps[address] = process

    found: str | None = None
    # 检查已完成的进程
    while ps:
        for address, process in ps.items():
            return_code = process.poll()
            if return_code is None:  # 进程还在运行时，poll() 返回 None
                continue

            # 从ps删除
            ps.pop(address)

            # 如果成功 ping 通，则返回地址
            if return_code == 0:
                found = address
                break

    # kill 其他仍在运行的进程
    for p in ps.values():
        if p.poll() is not None:
            continue

        try:
            p.kill()
        except ProcessLookupError:
            pass  # 进程可能已经结束

    return found
