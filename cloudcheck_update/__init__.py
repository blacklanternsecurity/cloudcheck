import json
import logging
import traceback
from pathlib import Path

from cloudcheck.providers import load_provider_classes

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("cloudcheck")


project_root = Path(__file__).parent.parent
json_path = project_root / "cloud_providers_v2.json"


def update():
    provider_classes = load_provider_classes()
    providers = {}
    errors = []
    for provider_class in provider_classes.values():
        provider = provider_class()
        try:
            errors = provider.update()
            errors.extend(errors)
            providers[provider.name] = provider
        except Exception as e:
            print(
                f"Failed to update provider {provider_class.name}: {e}\n{traceback.format_exc()}"
            )

    new_json = {n: p.model_dump() for n, p in providers.items()}
    existing_json = json.load(open(json_path)) if json_path.exists() else {}

    for name, provider in new_json.items():
        if name not in existing_json:
            existing_json[name] = provider
            continue
        existing_provider = existing_json[name]
        for k, v in provider.items():
            if v and not existing_provider.get(k, None):
                existing_provider[k] = v

    with open(json_path, "w") as f:
        json.dump({n: p.model_dump() for n, p in providers.items()}, f, indent=1)
    return errors
