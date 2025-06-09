import json
import ipaddress
from datetime import datetime


def is_ip_type(i):
    return isinstance(i, ipaddress._IPAddressBase)


def make_ip_type(host):
    if not host:
        raise ValueError(f'Invalid host: "{host}" ({type(host)})')
    try:
        host = ipaddress.ip_network(host, strict=False)
    except Exception:
        if not isinstance(host, str):
            raise ValueError(f'Invalid host: "{host}" ({type(host)})')
        host = host.lower()
    return host


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_ip_type(obj):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)
