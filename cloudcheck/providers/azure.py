from .base import BaseCloudProvider


class Azure(BaseCloudProvider):
    # mostly pulled from https://learn.microsoft.com/en-us/azure/azure-government/compare-azure-government-global-azure
    domains = [
        "azconfig.io",
        "azmk8s.io",
        "azure-api.net",
        "azure-api.us",
        "azure-automation.net",
        "azure-automation.us",
        "azure-devices.net",
        "azure-devices.us",
        "azure-mobile.net",
        "azure.com",
        "azure.net",
        "azure.us",
        "azurecontainer.io",
        "azurecr.io",
        "azurecr.us",
        "azuredatalakestore.net",
        "azureedge.net",
        "azurefd.net",
        "azurehdinsight.net",
        "azurehdinsight.us",
        "azurewebsites.net",
        "botframework.com",
        "cloudapp.net",
        "loganalytics.io",
        "loganalytics.us",
        "microsoft.us",
        "microsoftonline.com",
        "microsoftonline.us",
        "onmicrosoft.com",
        "powerbi.com",
        "powerbigov.us",
        "trafficmanager.net",
        "usgovcloudapi.net",
        "usgovtrafficmanager.net",
        "visualstudio.com",
        "vo.msecnd.net",
        "windows.net",
        "windowsazure.com",
        "windowsazure.us",
    ]
    bucket_name_regex = r"[a-z0-9][a-z0-9-_\.]{1,61}[a-z0-9]"
    regexes = {
        "STORAGE_BUCKET": [r"(" + bucket_name_regex + r")\.(blob\.core\.windows\.net)"]
    }

    ips_url = "https://download.microsoft.com/download/0/1/8/018E208D-54F8-44CD-AA26-CD7BC9524A8C/PublicIPs_20200824.xml"

    def parse_response(self, response):
        ranges = set()
        for line in response.text.splitlines():
            if "IpRange Subnet" in line:
                ip_range = line.split('"')[1]
                ranges.add(ip_range)
        return ranges
