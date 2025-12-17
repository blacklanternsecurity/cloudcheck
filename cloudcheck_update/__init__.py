import importlib
import json
import logging
import traceback
from pathlib import Path
from typing import Dict, Type

from cloudcheck.providers.base import BaseProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("cloudcheck")

# Dictionary to store loaded provider classes
_provider_classes: Dict[str, Type[BaseProvider]] = {}
# Dictionary to store instantiated providers
providers: Dict[str, BaseProvider] = {}


def load_provider_classes() -> Dict[str, Type[BaseProvider]]:
    """Dynamically load all cloud provider classes from the providers directory."""
    global _provider_classes

    if _provider_classes:
        return _provider_classes

    providers_path = Path(__file__).parent.parent / "cloudcheck" / "providers"

    for file in providers_path.glob("*.py"):
        if file.stem in ("base", "__init__"):
            continue

        try:
            import_path = f"cloudcheck.providers.{file.stem}"
            module = importlib.import_module(import_path)

            # Look for classes that inherit from BaseProvider
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseProvider)
                    and attr != BaseProvider
                ):
                    provider_name = attr.__name__.lower()
                    _provider_classes[provider_name] = attr
                    print(f"Loaded provider class: {attr.__name__}")

        except Exception as e:
            log.error(f"Failed to load provider from {file}: {e}")
            raise

    return _provider_classes


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
