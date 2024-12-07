# check_last_updated.py

import json
from datetime import datetime, timedelta

def check_last_updated():
    with open('cloud_providers.json', 'r') as file:
        data = json.load(file)

    one_week_ago = datetime.now() - timedelta(weeks=1)

    outdated_providers = []
    for provider, details in data.items():
        last_updated = datetime.fromisoformat(details['last_updated'])
        if last_updated < one_week_ago:
            outdated_providers.append((provider, last_updated))
    
    if outdated_providers:
        print("### Outdated Providers ###")
        outdated_providers.sort(key=lambda x: x[1])
        for provider, last_updated in outdated_providers:
            days_ago = (datetime.now() - last_updated).days
            friendly_last_updated = last_updated.strftime("%Y-%m-%d")
            print(f"- {provider}: last updated on {friendly_last_updated} ({days_ago} days ago).")
        if outdated_providers:
            return 1
    return 0

if __name__ == "__main__":
    exit(check_last_updated())
