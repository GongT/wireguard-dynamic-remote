from .type import GlobalConfig, PeerConfig


def parse_seems_like_comment_config(line: str, known_keys: dict[str, str]):
    if not line.startswith("#"):
        raise ValueError("Not a comment")

    line = line[1:].strip()
    if "=" not in line:
        return None

    key, value = line.split("=", 1)
    key = key.strip()
    lkey = key.lower()

    if lkey not in known_keys:
        return None

    key = known_keys[lkey]

    value = value.strip()
    return key, value


def parse_key_values(lines: list[str], keymap: dict[str, str]):
    result: dict[str, str] = {}

    for line in lines:
        if line.startswith("#"):
            extension = parse_seems_like_comment_config(line, keymap)
            if extension is None:
                continue
            key, value = extension
        else:
            line = line.strip()

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            lkey = key.lower()

            key = keymap[lkey] if lkey in keymap else key
            value = value.strip()

        result[key] = value

    return result


def parse_config_content(content: str):
    stage = 0  # 0 = global(ignore), 1 = interface, 2 = peer
    cache_lines: list[str] = []

    interface: list[str] = []
    peers: list[list[str]] = []

    def commit():
        nonlocal stage, cache_lines, interface, peers

        if len(cache_lines) == 0:
            return

        if stage == 1:
            interface = cache_lines
        elif stage == 2:
            peers.append(cache_lines)

        cache_lines = []

    for line in content.splitlines():
        if line.startswith("[Interface]"):
            commit()
            if len(interface) > 0:
                raise ValueError("Multiple [Interface] sections found")
            stage = 1

        elif line.startswith("[Peer]"):
            commit()
            stage = 2
            continue

        line = line.strip()
        cache_lines.append(line)

    commit()
    
    if len(interface) == 0:
        raise ValueError("No [Interface] section found")

    interface_dict = parse_key_values(interface, GlobalConfig.known_keys_list())
    peers_dict_list = [parse_key_values(p, PeerConfig.known_keys_list()) for p in peers]

    return GlobalConfig(interface_dict, peers_dict_list)
