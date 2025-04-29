# CloudCheck

A simple Python utility to check whether an IP address or hostname belongs to a cloud provider.

`cloud_providers.json` contains lists of domains and up-to-date CIDRs for each cloud provider (updated daily via CI/CD).

Used by [BBOT](https://github.com/blacklanternsecurity/bbot) and [BBOT Server](https://github.com/blacklanternsecurity/bbot-server).

## Installation
~~~bash
pip install cloudcheck
~~~

## Usage - CLI
~~~bash
$ cloudcheck 168.62.20.37
168.62.20.37 belongs to Azure (cloud) (168.62.0.0/19)

$ cloudcheck test.evilcorp.azurewebsites.net
test.evilcorp.azurewebsites.net belongs to Azure (cloud) (azurewebsites.net)
~~~

## Usage - Python
~~~python
import cloudcheck

provider, provider_type, subnet = cloudcheck.check("168.62.20.37")
print(provider) # "Azure"
print(provider_type) # "cloud"
print(subnet) # IPv4Network('168.62.0.0/19')
~~~

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
