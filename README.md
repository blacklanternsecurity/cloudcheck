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
    - `org_ids`: A list of organization IDs from ASNDB. These are always preferable to hard-coded ASNs or CIDRs, since they are updated daily from live sources. Big companies like Amazon typically have one organization ID per Regional Internet Registries (ARIN, RIPE, APNIC, LACNIC, AFRINIC), and within that organization ID, there may be multiple ASNs.
    - `asns`: A list of ASNs, e.g. `[12345, 67890]`
    - `cidrs`: A list of CIDRs, e.g. `["1.2.3.4/32", "5.6.7.8/32"]` (it's always preferred to use org_ids or if necessary asns over manually-specified CIDRs)
    - `tags`: A list of tags for the provider. These are used in BBOT to tag IPs, DNS names etc. that match this provider. Examples: `cloud`, `cdn`, `waf`, etc.
    - `regexes`: A dictionary of regexes for the provider. This are used in BBOT to extract / validate cloud resources like storage buckets. Currently valid regexes are:
        - `STORAGE_BUCKET_NAME`: A regex for the name of a storage bucket (useful when brute-forcing bucket names, as you can discard invalid bucket names early).
        - `STORAGE_BUCKET_HOSTNAME`: A regex for the hostname of a storage bucket
    
    In addition to the above attributes, if you have a custom source of CIDRsor domains, you can override the `fetch_cidrs()` or `fetch_domains()` methods (which by default return an empty list) to go fetch your custom TXT/JSON file, etc.

## Supported cloud providers
- Akamai ([source](https://techdocs.akamai.com/property-manager/pdfs/akamai_ipv4_ipv6_CIDRs-txt.zip))
- Amazon ([source](https://ip-ranges.amazonaws.com/ip-ranges.json))
- Arvancloud ([source](https://www.arvancloud.ir/en/ips.txt))
- Azure ([source](https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519))
- Cloudflare ([source](https://api.cloudflare.com/client/v4/ips))
- Cloudfront ([source](https://d7uri8nf7uskq.cloudfront.net/tools/list-cloudfront-ips))
- DigitalOcean ([source](http://digitalocean.com/geo/google.csv))
- Fastly ([source](https://api.fastly.com/public-ip-list))
- Github ([source](https://api.github.com/meta))
- Google ([source](https://www.gstatic.com/ipranges/cloud.json))
- Imperva ([source](https://my.imperva.com/api/integration/v1/ips))
- Oracle Cloud ([source](https://docs.cloud.oracle.com/en-us/iaas/tools/public_ip_ranges.json))
- Zoho ([source](https://github.com/blacklanternsecurity/cloudcheck/blob/master/cloudcheck/providers/zoho.py))
