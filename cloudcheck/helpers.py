import ipaddress
import os
import requests
from pathlib import Path
from typing import List, Set, Union


def defrag_cidrs(
    cidrs: List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]],
) -> List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
    """
    Defragment a list of CIDR blocks by merging adjacent networks.

    Algorithm:
    1. Sort by network bits (prefix length)
    2. Iterate through pairs of adjacent networks
    3. If networks have equal network bits and can be merged into a larger network,
       replace them with the merged network
    4. Repeat until no more merges are possible

    Args:
        cidrs: List of IPv4 or IPv6 network objects

    Returns:
        List of defragmented network objects
    """
    if not cidrs:
        return []

    # Convert to list and remove duplicates
    networks = list(set(cidrs))

    # Keep iterating until no more merges happen
    changed = True
    while changed:
        changed = False

        # Sort by network address
        networks.sort(key=lambda x: (x.prefixlen, x.network_address.packed))

        i = 0
        while i < len(networks) - 1:
            current = networks[i]
            next_net = networks[i + 1]

            # Check if we can merge these two networks
            if _can_merge_networks(current, next_net):
                # Create the merged network
                merged = _merge_networks(current, next_net)

                # Replace the two networks with the merged one
                networks[i] = merged
                networks.pop(i + 1)
                changed = True
            else:
                i += 1

    return networks


def _can_merge_networks(
    net1: Union[ipaddress.IPv4Network, ipaddress.IPv6Network],
    net2: Union[ipaddress.IPv4Network, ipaddress.IPv6Network],
) -> bool:
    """
    Check if two networks can be merged into a larger network.

    Two networks can be merged if:
    1. They have the same prefix length
    2. They are adjacent (one starts where the other ends)
    3. They can be combined into a network with prefix length - 1
    """
    # Must be same type (IPv4 or IPv6)
    if net1.version != net2.version:
        return False

    # Must not be the same network
    if net1 == net2:
        return False

    # Must have same prefix length
    if net1.prefixlen != net2.prefixlen:
        return False

    # Must be adjacent networks
    if not _are_adjacent_networks(net1, net2):
        return False

    return True


def _are_adjacent_networks(
    net1: Union[ipaddress.IPv4Network, ipaddress.IPv6Network],
    net2: Union[ipaddress.IPv4Network, ipaddress.IPv6Network],
) -> bool:
    """
    Check if two networks are adjacent by creating two networks with sub-1 CIDR
    and checking if they are equal.
    """
    # Must have same prefix length
    if net1.prefixlen != net2.prefixlen:
        return False

    # Create two networks with sub-1 CIDR
    new_prefixlen = net1.prefixlen - 1
    if new_prefixlen < 0:
        return False

    # Create the two networks with the reduced prefix length using supernet
    net1_parent = net1.supernet(prefixlen_diff=1)
    net2_parent = net2.supernet(prefixlen_diff=1)

    # If they are equal, the networks are adjacent
    return net1_parent == net2_parent


def _merge_networks(
    net1: Union[ipaddress.IPv4Network, ipaddress.IPv6Network],
    net2: Union[ipaddress.IPv4Network, ipaddress.IPv6Network],
) -> Union[ipaddress.IPv4Network, ipaddress.IPv6Network]:
    """
    Merge two adjacent networks into a larger network.
    """
    if net1 == net2:
        raise ValueError("Networks must be different")

    if not net1.version == net2.version:
        raise ValueError("Networks must be the same version")

    snet1 = net1.supernet(prefixlen_diff=1)
    snet2 = net2.supernet(prefixlen_diff=1)
    if not snet1 == snet2:
        raise ValueError("Networks must be adjacent")

    # Find the smaller network address
    min_addr = min(net1.network_address, net2.network_address)

    # Create the merged network with prefix length - 1
    new_prefixlen = net1.prefixlen - 1
    try:
        return ipaddress.ip_network(f"{min_addr}/{new_prefixlen}")
    except ValueError:
        raise ValueError(
            f"Failed to merge networks: {net1} (type: {type(net1)}) and {net2} (type: {type(net2)})"
        )


def cidrs_to_strings(
    cidrs: List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]],
) -> List[str]:
    """
    Convert a list of network objects to string representations.

    Args:
        cidrs: List of network objects

    Returns:
        List of CIDR strings
    """
    return [str(cidr) for cidr in cidrs]


def strings_to_cidrs(
    cidr_strings: List[str],
) -> List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
    """
    Convert a list of CIDR strings to network objects.

    Args:
        cidr_strings: List of CIDR strings

    Returns:
        List of network objects
    """
    networks = []
    for cidr_str in cidr_strings:
        try:
            networks.append(ipaddress.ip_network(cidr_str, strict=False))
        except ValueError:
            # Skip invalid CIDR strings
            continue
    return networks


browser_base_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "referer": "https://www.google.com/",
    "sec-ch-ua": '"Chromium";v="127", "Not)A;Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
}


def request(url, include_api_key=False, browser_headers=False, **kwargs):
    headers = kwargs.get("headers", {})
    if browser_headers:
        headers.update(browser_base_headers)
    bbot_io_api_key = os.getenv("BBOT_IO_API_KEY")
    if include_api_key and bbot_io_api_key:
        headers["Authorization"] = f"Bearer {bbot_io_api_key}"
    kwargs["headers"] = headers
    return requests.get(url, **kwargs)


def parse_v2fly_domain_file(file_path: Path) -> Set[str]:
    """Parse a domain list file and extract domains."""
    print(f"Parsing {file_path}")
    domains = set()
    if not file_path.exists():
        print(f"File {file_path} does not exist")
        return domains

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Handle inline comments by splitting on # and taking the first part
            line = line.split("#")[0].strip()
            if not line:
                continue

            if line.startswith("include:"):
                include_file = line[8:]
                include_path = file_path.parent / include_file
                domains.update(parse_v2fly_domain_file(include_path))
                continue

            if line.startswith("domain:"):
                domain = line[7:]
            elif line.startswith("full:"):
                domain = line[5:]
            elif line.startswith("keyword:") or line.startswith("regexp:"):
                continue
            else:
                domain = line

            domain = domain.split("@")[0].strip()
            if domain:
                domains.add(domain.lower())
    return domains
