#!/usr/bin/env python3
"""Update README.md with a provider table generated from cloud_providers_v2.json"""

import json
import re
from pathlib import Path


def load_providers(json_path: Path):
    """Load providers from cloud_providers_v2.json"""
    with open(json_path, "r") as f:
        return json.load(f)


def format_tags(tags: list) -> str:
    """Format tags list as comma-separated string"""
    return ", ".join(tags) if tags else "-"


def generate_table(providers: dict) -> str:
    """Generate markdown table from providers data"""
    rows = []
    count = len(providers)

    # Sort providers by name
    for name in sorted(providers.keys()):
        provider = providers[name]

        # Get name with short description
        short_desc = provider.get("short_description", "")
        if short_desc:
            name_col = short_desc
        else:
            name_col = name

        # Get long description
        long_desc = provider.get("long_description", "")
        if not long_desc:
            long_desc = "-"

        # Get tags
        tags = format_tags(provider.get("tags", []))

        # Count domains and subnets
        domains = provider.get("domains", [])
        cidrs = provider.get("cidrs", [])
        num_domains = len(domains)
        num_subnets = len(cidrs)

        rows.append(
            f"| {name_col} | {long_desc} | {tags} | {num_domains} | {num_subnets} |"
        )

    # Build table with heading
    heading = f"## Cloud Providers ({count})\n\n"
    header = "| Name | Description | Tags | Domains | Subnets |\n"
    separator = "|------|-------------|------|---------|----------|\n"
    table = heading + header + separator + "\n".join(rows) + "\n"

    return table


def update_readme(readme_path: Path, table: str):
    """Update README.md by replacing content between markers"""
    with open(readme_path, "r") as f:
        content = f.read()

    # Pattern to match content between markers
    pattern = r"(<!--PROVIDERTABLE-->).*?(<!--ENDPROVIDERTABLE-->)"
    replacement = r"\1\n" + table + r"\2"

    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    else:
        # If markers don't exist, add them before "## Supported cloud providers"
        marker = "<!--PROVIDERTABLE-->\n" + table + "<!--ENDPROVIDERTABLE-->"
        pattern = r"(## Supported cloud providers)"
        new_content = re.sub(pattern, marker + "\n\n" + r"\1", content)

    with open(readme_path, "w") as f:
        f.write(new_content)


def main():
    project_root = Path(__file__).parent.parent
    json_path = project_root / "cloud_providers_v2.json"
    readme_path = project_root / "README.md"

    if not json_path.exists():
        print(f"Error: {json_path} not found")
        return 1

    if not readme_path.exists():
        print(f"Error: {readme_path} not found")
        return 1

    providers = load_providers(json_path)
    table = generate_table(providers)
    update_readme(readme_path, table)

    print(f"Updated {readme_path} with provider table")
    return 0


if __name__ == "__main__":
    exit(main())
