import sys

from ..common import logger
from ..common.context import RunContext
from ..common.networking import ping_each_ip
from ..wireguard import get_runtime_interface, get_static_interface, set_peer_address
from .resolve import resolve
from .service_control import cross_platform_start_service


def main(config: RunContext):
    interfaces = config.interfaces

    if len(interfaces) == 0:
        print("No interfaces specified. Exiting.")
        return

    logger.output(f"Checking {len(interfaces)} interfaces: {', '.join(interfaces)}")

    ok = True
    for interface in interfaces:
        logger.output("")
        logger.output(f"Checking interface {interface}:")
        with logger.indent():
            _ok = check_interface(interface, config)
            ok = ok and _ok

    logger.output("")

    sys.exit(0 if ok else 1)


def check_interface(interface: str, config: RunContext):
    cfg = get_static_interface(interface)
    if not cfg:
        raise RuntimeError(f"Interface config file {interface} does not exist.")

    device = get_runtime_interface(interface)

    if not device:
        logger.output(f"Not exist: starting service and ignoring.")
        cross_platform_start_service(interface)
        return

    if len(device.peers) == 0:
        logger.output(f"No peers configured, skipping.")
        return

    logger.output(f"OnChange is '{cfg.OnChange}'")
    update_by_set = True
    if cfg.OnChange == "restart":
        update_by_set = False
    elif cfg.OnChange != "update" and cfg.OnChange != "":
        logger.output(f"OnChange '{cfg.OnChange}' is invalid")
    logger.output(
        f"Updating endpoints by {'command set' if update_by_set else 'restart'}."
    )

    something_changed = False
    something_errored = False
    for peer in device.peers:
        cfg_peer = cfg.get_peer_by_public_key(peer.PublicKey)
        if cfg_peer is None:
            logger.output(f"Peer {peer.PublicKey} not found in config, ignoring.")
            continue

        logger.output(f"Peer: {peer.PublicKey}")
        with logger.indent():
            # logger.output(f"Checking peer {peer.asdict()} // TODO")
            # logger.output(f"config peer {cfg_peer.asdict()} // TODO")

            correct_endpoint = cfg_peer.endpoint()
            if correct_endpoint is None:
                logger.output(f"Endpoint is passive, ignoring.")
                continue

            if not correct_endpoint.is_hostname:
                logger.output(f"Endpoint is connected to an IP address, ignoring.")
                continue

            current_endpoint = peer.endpoint()

            if not current_endpoint:
                logger.error(f"Endpoint is never connected, ignoring.")
                something_errored = True
                continue

            if current_endpoint.is_hostname:
                logger.explode(f"peer.endpoint_host is a string!")

            correct_address = resolve(correct_endpoint.addr, config.resolver)

            if correct_address is None or len(correct_address) == 0:
                logger.error(f"Failed to resolve domain '{correct_endpoint.addr}'!")
                something_errored = True
                continue

            logger.output(f"Resolved endpoint to {', '.join(correct_address)}")

            if current_endpoint.addr in correct_address:
                logger.output(f"Current endpoint is correct, no action needed.")
                continue

            if len(correct_address) > 1:
                logger.output(
                    "Multiple addresses resolved, pinging to find the best one..."
                )
                working_address = ping_each_ip(correct_address)
                logger.output(f"  * {working_address}")
            else:
                working_address = correct_address[0]

            assert working_address is not None

            if update_by_set:
                new_endpoint = f"{working_address}:{current_endpoint.port}"
                logger.output(f"Updating endpoint to {new_endpoint}")
                set_peer_address(interface, peer.PublicKey, new_endpoint)
            something_changed = True

    if something_changed and not update_by_set:
        logger.output(f"Restarting interface as OnChange is 'restart'")
        cross_platform_start_service(interface, nonce="restart")

    return not something_errored
