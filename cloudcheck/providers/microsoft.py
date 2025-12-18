from cloudcheck.providers.base import BaseProvider
from typing import List, Dict


class Microsoft(BaseProvider):
    v2fly_company: str = "microsoft"
    tags: List[str] = ["cloud"]
    # {"org_id": "MSFT-ARIN", "org_name": "Microsoft Corporation", "country": "US", "asns": [3598,5761,6182,6194,6291,6584,8068,8069,8070,8071,8072,8073,8074,8075,12076,13399,13811,14719,14783,17144,17345,20046,22692,23468,25796,26222,30135,30520,30575,31792,32476,36006,40066,46182,54396,63245,63314,395496,395524,395851,396463,397096,397466,397996,398575,398656,398657,398658,398659,398660,398661,398961,400572,400573,400574,400575,400576,400577,400578,400579,400580,400581,400582,400884]}
    # {"org_id": "ORG-MA42-RIPE", "org_name": "Microsoft Limited", "country": "GB", "asns": [35106]}
    # {"org_id": "ORG-MDMG3-RIPE", "org_name": "Microsoft Deutschland MCIO GmbH", "country": "DE", "asns": [200517]}
    # {"org_id": "ORG-MOPL2-AP-APNIC", "org_name": "Microsoft Operations PTE Ltd", "country": "SG", "asns": [132348]}
    # {"org_id": "ORG-MSPL4-AP-APNIC", "org_name": "Microsoft Singapore Pte. Ltd.", "country": "US", "asns": [45139]}
    org_ids: List[str] = [
        "MSFT-ARIN",
        "ORG-MA42-RIPE",
        "ORG-MDMG3-RIPE",
        "ORG-MOPL2-AP-APNIC",
        "ORG-MSPL4-AP-APNIC",
    ]
    _bucket_name_regex = r"[a-z0-9][a-z0-9-_\.]{1,61}[a-z0-9]"
    regexes: Dict[str, List[str]] = {
        "STORAGE_BUCKET_NAME": [_bucket_name_regex],
        "STORAGE_BUCKET_HOSTNAME": [
            r"(" + _bucket_name_regex + r")\.(blob\.core\.windows\.net)"
        ],
    }

    _ips_url = "https://download.microsoft.com/download/0/1/8/018E208D-54F8-44CD-AA26-CD7BC9524A8C/PublicIPs_20200824.xml"

    def fetch_cidrs(self):
        response = self.request(self._ips_url)
        ranges = set()
        for line in response.text.splitlines():
            if "IpRange Subnet" in line:
                ip_range = line.split('"')[1]
                ranges.add(ip_range)
        return list(ranges)
