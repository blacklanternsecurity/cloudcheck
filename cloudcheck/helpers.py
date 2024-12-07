import json
import ipaddress
from datetime import datetime


def is_ip_type(i):
    return isinstance(i, ipaddress._IPAddressBase)


def make_ip_type(host):
    if not host:
        raise ValueError("Invalid host")
    try:
        host = ipaddress.ip_network(host, strict=False)
    except Exception:
        host = str(host).lower()
    return host


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_ip_type(obj):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)
