# CloudCheck

A simple Python utility to check whether an IP address belongs to a cloud provider.

`cloud_providers.json` contains up-to-date lists of CIDRs for each cloud provider (updated weekly via CI/CD).

## Installation
~~~bash
pip install cloudcheck
~~~

## Usage - CLI
~~~bash
$ cloudcheck 168.62.20.37
168.62.20.37 belongs to Azure (168.62.0.0/19)
~~~

## Usage - Python
~~~python
import cloudcheck

provider, subnet = cloudcheck.check("168.62.20.37")
print(provider) # "Azure"
print(subnet) # IPv4Network('168.62.0.0/19')
~~~

## Supported cloud providers
- Amazon ([source](https://ip-ranges.amazonaws.com/ip-ranges.json)) 
- Azure ([source](https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519))
- Google ([source](https://www.gstatic.com/ipranges/cloud.json))
- Oracle Cloud ([source](https://docs.cloud.oracle.com/en-us/iaas/tools/public_ip_ranges.json))
- DigitalOcean ([source](http://digitalocean.com/geo/google.csv))
