# CloudCheck

[![Python Version](https://img.shields.io/badge/python-3.9+-blue)](https://www.python.org)
[![PyPI](https://img.shields.io/pypi/v/cloudcheck)](https://pypi.org/project/cloudcheck/)
[![Rust Version](https://img.shields.io/badge/rust-1.70+-orange)](https://www.rust-lang.org)
[![Crates.io](https://img.shields.io/crates/v/cloudcheck?color=orange)](https://crates.io/crates/cloudcheck)
[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://github.com/blacklanternsecurity/cloudcheck/blob/stable/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Rust Tests](https://github.com/blacklanternsecurity/cloudcheck/actions/workflows/rust-tests.yml/badge.svg?branch=stable)](https://github.com/blacklanternsecurity/cloudcheck/actions/workflows/rust-tests.yml)
[![Python Tests](https://github.com/blacklanternsecurity/cloudcheck/actions/workflows/python-tests.yml/badge.svg?branch=stable)](https://github.com/blacklanternsecurity/cloudcheck/actions/workflows/python-tests.yml)
[![Pipeline Tests](https://github.com/blacklanternsecurity/cloudcheck/actions/workflows/pipeline-tests.yml/badge.svg?branch=stable)](https://github.com/blacklanternsecurity/cloudcheck/actions/workflows/pipeline-tests.yml)
[![Docker Tests](https://github.com/blacklanternsecurity/cloudcheck/actions/workflows/docker-tests.yml/badge.svg?branch=stable)](https://github.com/blacklanternsecurity/cloudcheck/actions/workflows/docker-tests.yml)

### UPDATE 01-2026: Now supports REST API!

### UPDATE 12-2025: Now supports government agencies (DoD, FBI, UK MoD, RU FSO)!

### UPDATE 12-2025: Now rewritten in Rust!

CloudCheck is a simple Rust tool to check whether an IP address or hostname belongs to a cloud provider. It includes:

- A Rust CLI
- A Rust library
- Python bindings

## Cloud Provider Signatures

The latest cloud provider signatures are available in [`cloud_providers_v2.json`](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloud_providers_v2.json), which is updated daily via CI/CD. Domains associated with each cloud provider are fetched dynamically from the [v2fly community repository](https://github.com/v2fly/domain-list-community), and CIDRs are fetched from [ASNDB](https://asndb.api.bbot.io/).

Used by [BBOT](https://github.com/blacklanternsecurity/bbot) and [BBOT Server](https://github.com/blacklanternsecurity/bbot-server).

## CLI Usage

```bash
# installation
cargo install cloudcheck

# lookup command
cloudcheck lookup 8.8.8.8
# output:
[
  {
    "name": "Google",
    "tags": ["cloud"],
    "short_description": "A suite of cloud computing services provided by Google",
    "long_description": "Google Cloud Platform provides infrastructure, platform, and software services for businesses and developers"
  }
]

cloudcheck lookup asdf.amazon.com
# output:
[
  {
    "name": "Amazon",
    "tags": ["cloud"],
    "short_description": "A comprehensive cloud computing platform provided by Amazon",
    "long_description": "Amazon Web Services offers infrastructure services, storage, and computing power"
  }
]

# serve command - start REST API server
cloudcheck serve
# Server listening on http://127.0.0.1:8080
# Swagger UI available at http://127.0.0.1:8080/swagger-ui
# OpenAPI spec available at http://127.0.0.1:8080/api-docs/openapi.json

# serve with custom host and port
cloudcheck serve --host 0.0.0.0 --port 3000
```

## REST API

```bash
curl http://127.0.0.1:8080/lookup/8.8.8.8
```

## Python Library Usage

```bash
# installation
pip install cloudcheck
```

```python
import asyncio
from cloudcheck import CloudCheck

async def main():
    cloudcheck = CloudCheck()
    results = await cloudcheck.lookup("8.8.8.8")
    print(results) # [{'name': 'Google', 'tags': ['cloud']}]

asyncio.run(main())
```

## Rust Library Usage

```toml
# Add to Cargo.toml
[dependencies]
cloudcheck = "8.0"
tokio = { version = "1", features = ["full"] }
```

```rust
use cloudcheck::CloudCheck;

#[tokio::main]
async fn main() {
    let cloudcheck = CloudCheck::new();
    let results = cloudcheck.lookup("8.8.8.8").await.unwrap();
    println!("{:?}", results); // [CloudProvider { name: "Google", tags: ["cloud"] }]
}
```

## Update the JSON database

```bash
export BBOT_IO_API_KEY=<your-api-key>

uv sync
uv run cloudcheck_update/cli.py
```

## Adding a new cloud provider

When adding a new cloud provider:

1. Create a new file in the `cloudcheck/providers` directory and name it whatever you want, e.g. `amazon.py`.
2. Inside that file, create a new class that inherits from `BaseProvider`.
3. Inside that class, fill out any of the following attributes that are relevant to your provider:
    - `v2fly_company`: The company name for v2fly domain fetching. This will dynamically fetch domains from the v2fly community repository, whose purpose is to keep track of domain ownership across different companies.
    - `org_ids`: A list of organization IDs from ASNDB. These are always preferable to hard-coded ASNs or CIDRs, since they are updated daily from live sources. Big companies like Amazon typically have one organization ID per Regional Internet Registries (ARIN, RIPE, APNIC, LACNIC, AFRINIC), and within that organization ID, they may have multiple ASNs.
    - `asns`: A list of ASNs, e.g. `[12345, 67890]`
    - `cidrs`: A list of CIDRs, e.g. `["1.2.3.4/32", "5.6.7.8/32"]` (it's always preferred to use `org_ids` or if necessary `asns` over manually-specified CIDRs)
    - `domains`: A list of domains, e.g. `["amazon.com", "amazon.co.uk"]` (it's always preferred to use `v2fly_company` instead of hard-coding domains)
    - `tags`: A list of tags for the provider. These are used in BBOT to tag IPs, DNS names etc. that match this provider. Examples: `cloud`, `cdn`, `waf`, etc.
    - `regexes`: A dictionary of regexes for the provider. These are used in BBOT to extract / validate cloud resources like storage buckets. Currently valid regexes are:
        - `STORAGE_BUCKET_NAME`: A regex for the name of a storage bucket (useful when brute-forcing bucket names, as you can discard invalid bucket names early).
        - `STORAGE_BUCKET_HOSTNAME`: A regex for the hostname of a storage bucket
    
    In addition to the above attributes, if you have a custom source of CIDRs or domains, you can override the `fetch_cidrs()` or `fetch_domains()` methods (which by default return an empty list) to go fetch your custom TXT/JSON file, etc.

<!--PROVIDERTABLE-->
## Cloud Providers (55)

| Name | Description | Tags | Domains | Subnets |
|------|-------------|------|---------|----------|
| Akamai | A content delivery network and cloud services provider that delivers web and internet security services. | cloud | 81 | 6376 |
| Alibaba Cloud | A Chinese cloud computing company and subsidiary of Alibaba Group, providing cloud services and infrastructure. | cloud | 394 | 81 |
| Amazon Web Services | A comprehensive cloud computing platform provided by Amazon, offering infrastructure services, storage, and computing power. | cloud | 231 | 14090 |
| Arvancloud | An Iranian cloud computing and content delivery network provider offering cloud infrastructure and CDN services. | cdn | 1 | 20 |
| Backblaze | A cloud storage and backup service provider offering data backup and cloud storage solutions. | cloud | 2 | 26 |
| Baidu Cloud Acceleration (百度云加速) | A Chinese content delivery network and cloud acceleration service provided by Baidu. | cdn | 134 | 0 |
| CacheFly | A content delivery network provider offering global CDN services. | cdn | 0 | 23 |
| CDNetworks (씨디네트웍스) | A Korean content delivery network provider offering CDN and cloud services. | cdn | 0 | 3 |
| Cisco | A multinational technology corporation that designs, manufactures, and sells networking hardware, software, and telecommunications equipment. | cloud | 121 | 629 |
| Cloudflare | A web infrastructure and security company providing content delivery network services, DDoS mitigation, and web security solutions. | cdn | 60 | 2674 |
| Amazon CloudFront | A content delivery network service provided by Amazon Web Services that delivers data, videos, applications, and APIs to customers globally. | cdn | 0 | 172 |
| DDoS Guard | A DDoS protection and content delivery network service provider. | cdn | 0 | 19 |
| Dell | A multinational technology company that develops, sells, repairs, and supports computers and related products and services. | cloud | 236 | 104 |
| DigitalOcean | A cloud infrastructure provider offering virtual private servers, managed databases, and other cloud services for developers and businesses. | cloud | 4 | 265 |
| Department of Defense | A U.S. government agency responsible for coordinating and supervising all agencies and functions of the government directly related to national security and the United States Armed Forces. | gov | 3 | 9226 |
| Federal Bureau of Investigation | A U.S. government agency that serves as the domestic intelligence and security service, responsible for investigating federal crimes and protecting national security. | gov | 3 | 21 |
| Fastly | A content delivery network and edge cloud platform that provides edge computing, security, and performance services. | cdn | 8 | 1026 |
| Gabia (가비아) | A Korean cloud hosting and infrastructure provider. | cloud | 0 | 48 |
| G-Core Labs | A content delivery network and cloud infrastructure provider offering CDN, cloud computing, and edge services. | cdn | 0 | 1405 |
| GitHub | A web-based platform for version control and collaboration using Git, providing hosting for software development and code repositories. | cdn | 33 | 4277 |
| GoCache | A Brazilian content delivery network provider offering CDN services. | cdn | 0 | 28 |
| Google Cloud | A suite of cloud computing services provided by Google, including infrastructure, platform, and software services for businesses and developers. | cloud | 1095 | 1863 |
| Hewlett Packard Enterprise | A multinational enterprise information technology company that provides servers, storage, networking, and cloud services. | cloud | 16 | 38 |
| Heroku | A cloud platform as a service that enables developers to build, run, and operate applications entirely in the cloud. | cloud | 12 | 0 |
| Hetzner | A German cloud hosting provider offering dedicated servers, cloud instances, and storage solutions. | cloud | 14 | 126 |
| Hostway (호스트웨이) | A Korean cloud hosting and infrastructure provider. | cloud | 0 | 59 |
| Huawei | A Chinese multinational technology corporation that designs, develops, and sells telecommunications equipment, consumer electronics, and cloud services. | cloud | 338 | 270 |
| IBM | A multinational technology corporation that provides hardware, software, cloud computing, and consulting services. | cloud | 20 | 394 |
| Imperva | A cybersecurity company that provides web application firewall, DDoS protection, and data security solutions. | waf | 1 | 23 |
| Kamatera | A cloud infrastructure provider offering virtual private servers, cloud servers, and managed cloud services. | cloud | 1 | 163 |
| KINX (한국인터넷인프라) | A Korean content delivery network and cloud infrastructure provider. | cdn | 0 | 136 |
| KT Cloud (KT클라우드) | A Korean cloud computing service provided by KT Corporation. | cloud | 0 | 8 |
| Leaseweb | A global hosting and cloud infrastructure provider offering dedicated servers, cloud hosting, and CDN services. | cloud | 0 | 1487 |
| LG U+ (LG유플러스) | A Korean telecommunications company offering CDN services. | cdn | 0 | 168 |
| Microsoft | A multinational technology corporation that develops, manufactures, licenses, supports and sells computer software, consumer electronics and personal computers. Known for products like Windows, Office, Azure cloud services, and Xbox. | cloud | 689 | 2452 |
| Microsoft 365 | A cloud-based productivity suite provided by Microsoft, including Office applications and cloud services. | cloud | 0 | 82 |
| Naver Cloud Platform (네이버 클라우드 플랫폼) | A Korean cloud computing platform provided by Naver Corporation. | cloud | 0 | 73 |
| NHN Cloud (NHN클라우드) | A Korean cloud computing platform provided by NHN Corporation. | cloud | 0 | 122 |
| OVHcloud | A French cloud computing company that provides web hosting, dedicated servers, and cloud infrastructure services. | cloud | 3 | 517 |
| Oracle | A multinational technology corporation that provides database software, cloud engineering systems, and enterprise software products. | cloud | 18 | 2329 |
| Qrator | A DDoS protection and content delivery network service provider. | cdn | 0 | 19 |
| Quic.cloud | A content delivery network and edge computing platform providing CDN services. | cdn | 0 | 151 |
| Russian Federal Security Service | A Russian federal executive body responsible for counterintelligence, internal and border security, counterterrorism, and surveillance. | gov | 0 | 17 |
| Rackspace | A managed cloud computing company that provides hosting, cloud services, and managed infrastructure solutions. | cloud | 1 | 199 |
| Salesforce | A cloud-based software company that provides customer relationship management services and enterprise cloud computing solutions. | cloud | 39 | 48 |
| Scaleway | A French cloud computing company that provides virtual private servers, bare metal servers, and cloud infrastructure services. | cloud | 1 | 40 |
| SK Broadband (SK브로드밴드) | A Korean telecommunications company offering CDN services. | cdn | 0 | 22 |
| StormWall | A DDoS protection and web application firewall service provider. | cdn | 0 | 20 |
| Sucuri | A website security and web application firewall service provider. | waf | 0 | 16 |
| Tencent Cloud | A Chinese cloud computing service provider and subsidiary of Tencent, offering cloud infrastructure and platform services. | cloud | 580 | 368 |
| United Kingdom Ministry of Defence | A U.K. government department responsible for implementing the defence policy of the United Kingdom and managing the British Armed Forces. | gov | 1 | 0 |
| Wasabi | A cloud storage provider offering hot cloud storage services with high performance and low cost. | cloud | 1 | 20 |
| X4B | A DDoS protection and content delivery network service provider. | cdn | 0 | 3 |
| Zoho | An Indian software company that provides cloud-based business software and productivity tools including CRM, email, and office suites. | cloud | 13 | 91 |
| Zscaler | A cloud security company providing secure internet access, cloud security, and zero trust network access services. | cloud | 0 | 247 |
<!--ENDPROVIDERTABLE-->

## Development

### Python

#### Setup
```bash
uv sync
uv run maturin develop --release
```

#### Running Tests
```bash
# python tests
uv run pytest test_cloudcheck.py -v

# docker tests
python test_docker.py
```

#### Linting
```bash
# Check for linting issues
uv run ruff check && uv run ruff format .
```

### Rust

#### Running Tests
```bash
cargo test --verbose --all-features
```

#### Formatting
```bash
cargo fmt --all

cargo clippy --all-targets --all-features -- -D warnings
```
