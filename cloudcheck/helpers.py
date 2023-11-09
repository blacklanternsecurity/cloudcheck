import json
import ipaddress
from datetime import datetime


def is_ip(d, version=None):
    """
    Checks if the given string or object represents a valid IP address.

    Args:
        d (str or ipaddress.IPvXAddress): The IP address to check.
        version (int, optional): The IP version to validate (4 or 6). Default is None.

    Returns:
        bool: True if the string or object is a valid IP address, False otherwise.

    Examples:
        >>> is_ip('192.168.1.1')
        True
        >>> is_ip('bad::c0de', version=6)
        True
        >>> is_ip('bad::c0de', version=4)
        False
        >>> is_ip('evilcorp.com')
        False
    """
    if isinstance(d, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
        if version is None or version == d.version:
            return True
    try:
        ip = ipaddress.ip_address(d)
        if version is None or ip.version == version:
            return True
    except Exception:
        pass
    return False


def domain_parents(host):
    split_host = str(host).lower().split(".")
    split_host_len = len(split_host)
    for i in range(split_host_len):
        yield ".".join(split_host[split_host_len - i - 1 :])


def ip_network_parents(ip, include_self=False):
    """
    "192.168.1.1" --> [192.168.1.0/31, 192.168.1.0/30 ... 128.0.0.0/1, 0.0.0.0/0]
    """
    net = ipaddress.ip_network(ip, strict=False)
    for i in range(net.prefixlen - (0 if include_self else 1), -1, -1):
        yield ipaddress.ip_network(f"{net.network_address}/{i}", strict=False)


def is_ip_type(i):
    return isinstance(i, ipaddress._BaseV4) or isinstance(i, ipaddress._BaseV6)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_ip_type(obj):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)
