from cloudcheck.providers.base import BaseProvider
from typing import List


class Ktcloud(BaseProvider):
    tags: List[str] = ["cloud"]
    short_description: str = "KT Cloud (KT클라우드)"
    long_description: str = (
        "A Korean cloud computing service provided by KT Corporation."
    )
    # {"asn":9947,"asn_name":"KTC-AS-KR","country":null,"org":null,"org_id":"@aut-152232-APNIC","rir":null,"subnets":["61.100.71.0/24","61.100.72.0/24"]}
    org_ids: List[str] = [
        "@aut-152232-APNIC",
    ]
