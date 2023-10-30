import json
import ipaddress
from datetime import datetime


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
