"""Network math, IP calculation, and subnet validation utilities for Network Simulator."""

import ipaddress
import re
from dataclasses import dataclass

MAC_REGEX = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")


@dataclass
class SubnetDetails:
    """Detailed IP network metadata."""

    network_address: str
    broadcast_address: str
    netmask: str
    prefix_length: int
    first_usable_ip: str
    last_usable_ip: str
    total_hosts: int
    usable_hosts: int


def is_valid_ipv4(ip_str: str) -> bool:
    """Validate IPv4 address string."""
    if not ip_str:
        return False
    try:
        ip = ipaddress.IPv4Address(ip_str.strip())
        return not ip.is_multicast and not ip.is_reserved
    except (ipaddress.AddressValueError, ValueError):
        return False


def is_valid_ipv6(ip_str: str) -> bool:
    """Validate IPv6 address string."""
    if not ip_str:
        return False
    try:
        ipaddress.IPv6Address(ip_str.strip())
        return True
    except (ipaddress.AddressValueError, ValueError):
        return False


def is_valid_mac(mac_str: str) -> bool:
    """Validate standard 48-bit MAC address format."""
    if not mac_str:
        return False
    return bool(MAC_REGEX.match(mac_str.strip()))


def mask_to_cidr(mask_str: str) -> int:
    """Convert dotted-decimal netmask or CIDR string (e.g. '255.255.255.0' or '/24' or '24') to integer prefix length."""
    cleaned = mask_str.strip().lstrip("/")
    if cleaned.isdigit():
        val = int(cleaned)
        if 0 <= val <= 32:
            return val
        raise ValueError(f"Invalid CIDR prefix length: {val}")
    try:
        net = ipaddress.IPv4Network(f"0.0.0.0/{cleaned}")
        return net.prefixlen
    except Exception as e:
        raise ValueError(f"Invalid IPv4 netmask: {mask_str}") from e


def cidr_to_mask(prefix_len: int) -> str:
    """Convert CIDR prefix length to dotted-decimal netmask."""
    if not (0 <= prefix_len <= 32):
        raise ValueError(f"Prefix length must be between 0 and 32, got {prefix_len}")
    net = ipaddress.IPv4Network(f"0.0.0.0/{prefix_len}")
    return str(net.netmask)


def get_subnet_details(ip_str: str, mask_or_cidr: str | int) -> SubnetDetails:
    """Calculate comprehensive network details for an IP and subnet mask."""
    prefix = mask_to_cidr(str(mask_or_cidr)) if isinstance(mask_or_cidr, (str, int)) else 24
    net = ipaddress.IPv4Network(f"{ip_str.strip()}/{prefix}", strict=False)

    num_hosts = net.num_addresses
    usable = max(0, num_hosts - 2) if prefix < 31 else num_hosts
    first_ip = str(net.network_address + 1) if prefix < 31 else str(net.network_address)
    last_ip = str(net.broadcast_address - 1) if prefix < 31 else str(net.broadcast_address)

    return SubnetDetails(
        network_address=str(net.network_address),
        broadcast_address=str(net.broadcast_address),
        netmask=str(net.netmask),
        prefix_length=prefix,
        first_usable_ip=first_ip,
        last_usable_ip=last_ip,
        total_hosts=num_hosts,
        usable_hosts=usable,
    )


def are_same_subnet(
    ip1: str,
    mask1: str | int,
    ip2: str,
    mask2: str | int | None = None,
) -> bool:
    """Determine whether two IPv4 addresses belong to the same local IP subnet."""
    try:
        prefix1 = mask_to_cidr(str(mask1))
        prefix2 = mask_to_cidr(str(mask2)) if mask2 is not None else prefix1
        net1 = ipaddress.IPv4Network(f"{ip1.strip()}/{prefix1}", strict=False)
        net2 = ipaddress.IPv4Network(f"{ip2.strip()}/{prefix2}", strict=False)

        addr1 = ipaddress.IPv4Address(ip1.strip())
        addr2 = ipaddress.IPv4Address(ip2.strip())

        return (net1 == net2) and (addr2 in net1) and (addr1 in net2)
    except (ValueError, ipaddress.AddressValueError, TypeError):
        return False


def is_valid_gateway(host_ip: str, netmask: str | int, gateway_ip: str) -> tuple[bool, str]:
    """Validate whether a default gateway address is valid and reachable for a host.

    Returns (is_valid, reason).
    """
    if not is_valid_ipv4(host_ip):
        return False, f"Host IP '{host_ip}' is invalid."
    if not is_valid_ipv4(gateway_ip):
        return False, f"Gateway IP '{gateway_ip}' is invalid."

    try:
        prefix = mask_to_cidr(str(netmask))
        net = ipaddress.IPv4Network(f"{host_ip}/{prefix}", strict=False)
        gw_addr = ipaddress.IPv4Address(gateway_ip)
        host_addr = ipaddress.IPv4Address(host_ip)

        if gw_addr == host_addr:
            return False, "Gateway IP cannot be identical to the host's own IP address."
        if gw_addr == net.network_address:
            return False, f"Gateway IP {gateway_ip} cannot be the subnet network address."
        if gw_addr == net.broadcast_address:
            return False, f"Gateway IP {gateway_ip} cannot be the subnet broadcast address."
        if gw_addr not in net:
            return (
                False,
                f"Gateway IP {gateway_ip} is outside host subnet {net.network_address}/{prefix}.",
            )
        return True, "Gateway is valid and reachable on the local subnet."
    except (ValueError, ipaddress.AddressValueError, TypeError) as e:
        return False, f"Gateway validation error: {e}"


def generate_deterministic_mac(device_type: str, device_index: int, iface_index: int = 0) -> str:
    """Generate deterministic, valid locally administered virtual MAC address.

    Format: 02:00:TT:DD:II:00
      02:00 = Locally administered unicast
      TT = Type code (01: PC, 02: Laptop, 03: Server, 04: Switch, 05: Router, 06: Firewall, 07: Internet, 08: DNS, 09: DHCP)
      DD = Device index (1-255)
      II = Interface index (0-255)
    """
    type_map = {
        "PC": 0x01,
        "LAPTOP": 0x02,
        "SERVER": 0x03,
        "SWITCH": 0x04,
        "ROUTER": 0x05,
        "FIREWALL": 0x06,
        "INTERNET": 0x07,
        "DNS_SERVER": 0x08,
        "DHCP_SERVER": 0x09,
    }
    t_code = type_map.get(device_type.upper(), 0x10)
    d_code = max(1, min(255, device_index))
    i_code = max(0, min(255, iface_index))
    return f"02:00:{t_code:02x}:{d_code:02x}:{i_code:02x}:01"
