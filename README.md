# CloudCheck

A simple Python utility to check whether an IP address belongs to a cloud provider.

`cloud_providers.json` contains up-to-date lists of CIDRs for each cloud provider (updated weekly via CI/CD).

Used by [Bighuge BLS OSINT Tool (BBOT)](https://github.com/blacklanternsecurity/bbot).

## Installation
~~~bash
pip install cloudcheck
~~~

## Usage - CLI
~~~bash
$ cloudcheck 168.62.20.37
168.62.20.37 belongs to Azure (cloud) (168.62.0.0/19)

$ cloudcheck 104.16.0.1
104.16.0.1 belongs to Cloudflare (cdn) (104.16.0.0/13)
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
- Amazon ([source](https://ip-ranges.amazonaws.com/ip-ranges.json)) 
- Azure ([source](https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519))
- Google ([source](https://www.gstatic.com/ipranges/cloud.json))
- Oracle Cloud ([source](https://docs.cloud.oracle.com/en-us/iaas/tools/public_ip_ranges.json))
- DigitalOcean ([source](http://digitalocean.com/geo/google.csv))
- Cloudflare ([source](https://api.cloudflare.com/client/v4/ips))
- Akami ([source](https://techdocs.akamai.com/property-manager/pdfs/akamai_ipv4_ipv6_CIDRs-txt.zip))
