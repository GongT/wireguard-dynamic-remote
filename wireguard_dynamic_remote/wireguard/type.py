import ipaddress


def make_name_map(object):
    known_keys = {}
    for key in dir(object):
        if key.startswith("_") or callable(getattr(object, key)):
            continue
        known_keys[key.lower()] = key

    return known_keys


class Config:
    def __init__(self, peer: dict):
        self._others = {}
        self._known_keys = dict()

        known_keys = make_name_map(self)

        for key, value in peer.items():
            lkey = key.lower()
            if lkey in known_keys:
                setattr(self, known_keys[lkey], value)
            else:
                self._others[lkey] = value

        self._known_keys = known_keys

    def get(self, key: str) -> str | None:
        lkey = key.lower()
        if lkey in self._known_keys:
            return getattr(self, self._known_keys[lkey], None)

        return self._others.get(lkey, None)

    @classmethod
    def known_keys_list(cls) -> dict[str, str]:
        return make_name_map(cls)

    def __str__(self) -> str:
        max_key_len = max(
            len(k) for k in [*dict.keys(self._others), *self._known_keys.values()]
        )

        r = ""
        for key in self._known_keys.values():
            value = getattr(self, key)
            if value == "":
                continue
            r += f"{key.ljust(max_key_len)} = {value}\n"

        if len(self._others) == 0:
            return r.rstrip()

        r += "# other keys\n"
        for key, value in self._others.items():
            r += f"{key.ljust(max_key_len)} = {value}\n"

        return r.rstrip()


class Endpoint:
    def __init__(self, endpoint: str):
        if endpoint[0] == "[":  # ipv6
            addr = endpoint[1 : endpoint.index("]")]
            port = endpoint[endpoint.index("]") + 2 :]
        else:
            if ":" in endpoint:
                addr, port = endpoint.rsplit(":", 1)
            else:
                addr = endpoint
                port = ""

        if not port:
            raise ValueError(f"Endpoint '{endpoint}' missing port!")

        try:
            ipaddress.ip_address(addr)
            self.is_hostname = False
        except ValueError:
            self.is_hostname = True

        self.addr = addr
        self.port = port


class PeerConfig(Config):
    PublicKey = ""
    AllowedIPs = ""
    Endpoint = ""
    PersistentKeepalive = ""

    def endpoint(self):
        if self.Endpoint == "":
            return None
        else:
            return Endpoint(self.Endpoint)

    def __str__(self) -> str:
        return "[Peer]\n" + super().__str__()


class GlobalConfig(Config):
    peers: list[PeerConfig]  # don't set default value

    ListenPort = ""
    PrivateKey = ""

    # my addition
    OnChange = ""

    # wg-quick
    PostUp = ""
    PostDown = ""
    PreUp = ""
    PreDown = ""
    Address = ""
    DNS = ""
    MTU = ""
    Table = ""
    SaveConfig = ""

    def __init__(self, interface: dict, peers: list[dict]):
        super().__init__(interface)

        self.peers = [PeerConfig(p) for p in peers]

    def get_peer_by_public_key(self, public_key: str) -> PeerConfig | None:
        for peer in self.peers:
            if peer.PublicKey == public_key:
                return peer
        return None

    def __str__(self) -> str:
        r = "[Interface]\n" + super().__str__()

        for peer in self.peers:
            r += "\n\n" + str(peer)

        return r
