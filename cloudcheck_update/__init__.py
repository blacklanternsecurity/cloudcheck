import json
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from cloudcheck.providers import load_provider_classes

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("cloudcheck")


project_root = Path(__file__).parent.parent
json_path = project_root / "cloud_providers_v2.json"


def _update_provider(provider_class):
    """Update a single provider and return (name, provider, errors)."""
    provider = provider_class()
    try:
        provider_errors = provider.update()
        return (provider.name, provider, provider_errors or [])
    except Exception as e:
        print(
            f"Failed to update provider {provider_class.name}: {e}\n{traceback.format_exc()}"
        )
        return (None, None, [])


def update():
    provider_classes = load_provider_classes()
    providers = {}
    errors = []

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(_update_provider, provider_class): provider_class
            for provider_class in provider_classes.values()
        }
        for future in as_completed(futures):
            name, provider, provider_errors = future.result()
            if name and provider:
                providers[name] = provider
                errors.extend(provider_errors)

    new_json = {n: p.model_dump() for n, p in providers.items()}
    existing_json = json.load(open(json_path)) if json_path.exists() else {}

    # instead of directly dumping the new data, we merge it with the existing
    for name, provider in new_json.items():
        if name not in existing_json:
            existing_json[name] = provider
            continue
        existing_provider = existing_json[name]
        for k, v in provider.items():
            if v and not existing_provider.get(k, None):
                existing_provider[k] = v

    with open(json_path, "w") as f:
        json.dump(existing_json, f, indent=1)
    return errors
