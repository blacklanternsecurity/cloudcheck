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
            self.cidrs.add(ipaddress.ip_network(r))

    def __contains__(self, ip):
        if isinstance(ip, ipaddress._BaseNetwork):
            return ip in self.cidrs
        ip = ipaddress.ip_address(ip)
        for p in ip_network_parents(ip):
            if p in self.cidrs:
                return True
        return False
