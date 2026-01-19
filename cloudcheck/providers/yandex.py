from cloudcheck.providers.base import BaseProvider
from typing import List


class Yandex(BaseProvider):
    v2fly_company: str = "yandex"
    short_description: str = "Yandex Cloud"
    long_description: str = "Russian cloud computing and internet services provider, offering infrastructure, storage, and various digital services."
    # {
    #   "org_id": "ORG-YA1-RIPE",
    #   "org_name": "YANDEX LLC",
    #   "country": "RU",
    #   "asns": [
    #     {
    #       "asn": 13238,
    #       "name": "YANDEX"
    #     },
    #     {
    #       "asn": 44534,
    #       "name": "yandex-office"
    #     },
    #     {
    #       "asn": 215109,
    #       "name": "YANDEX-COM"
    #     }
    #   ],
    #   "emails": [
    #     "gbragin@yandex-team.ru",
    #     "noc@yandex.net"
    #   ]
    # },
    # {
    #   "org_id": "ORG-YATR1-RIPE",
    #   "org_name": "Buyuk Reklam Cozumleri LLC",
    #   "country": "TR",
    #   "asns": [
    #     {
    #       "asn": 212066,
    #       "name": "YANDEX-COM-TR"
    #     }
    #   ]
    # },
    # {
    #   "org_id": "ORG-YCTL2-RIPE",
    #   "org_name": "Yandex.Telecom LLC",
    #   "country": "RU",
    #   "asns": [
    #     {
    #       "asn": 202611,
    #       "name": "YCTL"
    #     },
    #     {
    #       "asn": 213952,
    #       "name": "YACLOUDII"
    #     }
    #   ]
    # },
    # {
    #   "org_id": "ORG-YIJL1-RIPE",
    #   "org_name": "Y. Izdeu men Jarnama LLP",
    #   "country": "KZ",
    #   "asns": [
    #     {
    #       "asn": 207304,
    #       "name": "YANDEX-KZ"
    #     }
    #   ]
    # },
    # {
    #   "org_id": "ORG-YL30-RIPE",
    #   "org_name": "Yandex.OFD LLC",
    #   "country": "RU",
    #   "asns": [
    #     {
    #       "asn": 207207,
    #       "name": "YL30"
    #     }
    #   ]
    # },
    # {
    #   "org_id": "ORG-YL62-RIPE",
    #   "org_name": "Yandex.Cloud LLC",
    #   "country": "RU",
    #   "asns": [
    #     {
    #       "asn": 200350,
    #       "name": "YandexCloud"
    #     },
    #     {
    #       "asn": 210656,
    #       "name": "YACLOUDBMS"
    #     },
    #     {
    #       "asn": 215013,
    #       "name": "YACLOUDCDN"
    #     }
    #   ]
    # }
    org_ids: List[str] = [
        "ORG-YA1-RIPE",  # YANDEX LLC, RU
        "ORG-YATR1-RIPE",  # Buyuk Reklam Cozumleri LLC (ASN: 212066, YANDEX-COM-TR)
        "ORG-YCTL2-RIPE",  # Yandex.Telecom LLC, RU
        "ORG-YIJL1-RIPE",  # Y. Izdeu men Jarnama LLP, KZ (ASN: 207304, YANDEX-KZ)
        "ORG-YL30-RIPE",  # Yandex.OFD LLC, RU
        "ORG-YL62-RIPE",  # Yandex.Cloud LLC, RU
    ]
    tags: List[str] = ["cloud"]
