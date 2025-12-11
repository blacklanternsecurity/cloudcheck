# CloudCheck

A simple Python utility to check whether an IP address or hostname belongs to a cloud provider.

`cloud_providers.json` contains lists of domains and up-to-date CIDRs for each cloud provider (updated daily via CI/CD).

Used by [BBOT](https://github.com/blacklanternsecurity/bbot) and [BBOT Server](https://github.com/blacklanternsecurity/bbot-server).

## Installation
~~~bash
pip install cloudcheck
~~~

## Update the JSON database

```bash
export BBOT_IO_API_KEY=<your-api-key>

cloudcheck-update
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
    
    In addition to the above attributes, if you have a custom source of CIDRsor domains, you can override the `fetch_cidrs()` or `fetch_domains()` methods (which by default return an empty list) to go fetch your custom TXT/JSON file, etc.

## Supported cloud providers
- Akamai ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/akamai.py))
- Alibaba ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/alibaba.py))
- Amazon ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/amazon.py))
- Arvancloud ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/arvancloud.py))
- Azure ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/azure.py))
- Backblaze ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/backblaze.py))
- Cisco ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/cisco.py))
- Cloudflare ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/cloudflare.py))
- Cloudfront ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/cloudfront.py))
- Dell ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/dell.py))
- DigitalOcean ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/digitalocean.py))
- Fastly ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/fastly.py))
- GitHub ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/github.py))
- Google ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/google.py))
- Heroku ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/heroku.py))
- Hetzner ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/hetzner.py))
- HPE ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/hpe.py))
- Huawei ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/huawei.py))
- IBM ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/ibm.py))
- Imperva ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/imperva.py))
- Kamatera ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/kamatera.py))
- Oracle Cloud ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/oracle.py))
- OVH ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/ovh.py))
- Rackspace ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/rackspace.py))
- Salesforce ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/salesforce.py))
- Scaleway ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/scaleway.py))
- Tencent ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/tencent.py))
- Wasabi ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/wasabi.py))
- Zoho ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/zoho.py))
