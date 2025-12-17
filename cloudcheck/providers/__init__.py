import importlib
from pathlib import Path
from typing import Dict, Type

from cloudcheck.providers.base import BaseProvider

# Dictionary to store loaded provider classes
_provider_classes: Dict[str, Type[BaseProvider]] = {}


def load_provider_classes() -> Dict[str, Type[BaseProvider]]:
    """Dynamically load all cloud provider classes from the providers directory."""
    global _provider_classes

    if _provider_classes:
        return _provider_classes

    providers_path = Path(__file__).parent

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
                    provider_name = attr.__name__
                    _provider_classes[provider_name] = attr
                    print(f"Loaded provider class: {attr.__name__}")

        except Exception as e:
            print(f"Failed to load provider from {file}: {e}")
            raise

    return _provider_classes


for provider_name, provider_class in load_provider_classes().items():
    globals()[provider_name] = provider_class()
