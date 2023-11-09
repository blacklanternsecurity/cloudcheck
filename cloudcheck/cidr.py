import ipaddress
from .helpers import ip_network_parents


class CidrRanges:
    """
    Todo: implement a faster lookup scheme, something like:
        https://github.com/jsommers/pytricia
        https://github.com/yl2chen/cidranger
    """

    def __init__(self, ranges):
        self.cidrs = set()
        for r in ranges:
            self.cidrs.add(ipaddress.ip_network(r, strict=False))

    def __iter__(self):
        yield from self.cidrs

    def __bool__(self):
        return bool(self.cidrs)

    def __repr__(self):
        return repr(self.cidrs)

    def __str__(self):
        return str(self.cidrs)

    def __len__(self):
        return len(self.cidrs)

    def __contains__(self, ip):
        if isinstance(ip, ipaddress._BaseNetwork):
            return ip in self.cidrs
        ip = ipaddress.ip_address(ip)
        for p in ip_network_parents(ip):
            if p in self.cidrs:
                return True
        return False
