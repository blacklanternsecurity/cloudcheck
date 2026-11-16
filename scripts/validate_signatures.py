#!/usr/bin/env python3
"""Validate a new cloud_providers_v3.json against the one on stable before it is pushed.

Clients download cloud_providers_v3.json from stable at runtime, so the daily push is the
release. This runs in the job that holds the push token, so it uses the standard library only.

Usage: validate_signatures.py --old <file on stable> --new <candidate>
Exit 0 when every check passes, 1 with one line per failure otherwise.
"""

import argparse
import ipaddress
import json
import re
import sys

FIELDS = {
    "name": str,
    "short_description": str,
    "long_description": str,
    "v2fly_company": str,
    "tags": list,
    "asns": list,
    "cidrs": list,
    "domains": list,
    "org_ids": list,
    "regexes": dict,
    "last_updated": (int, float),
}
TAGS = {"cdn", "cloud", "gov", "security", "waf"}
DOMAIN = re.compile(r"[a-z0-9*_.-]{1,253}")

# Normal daily churn is well under these (worst single-provider loss over 25 days: 18%).
MAX_FIELD_LOSS = 0.50  # a provider with at least MIN_SIZE entries loses more than half of a field
MIN_SIZE = 20
MAX_TOTAL_LOSS = 0.10  # all CIDRs, all domains or all ASNs together drop by more than 10%
MIN_BYTES_RATIO = 0.80  # the file shrinks below 80% of its previous size


def load(path):
    with open(path, "rb") as f:
        raw = f.read()
    return raw, json.loads(raw)


def check_shape(new, errors):
    if not isinstance(new, dict) or not new:
        errors.append("top level is not a non-empty object")
        return
    for provider, data in new.items():
        if not isinstance(data, dict):
            errors.append(f"{provider}: not an object")
            continue
        for field, kind in FIELDS.items():
            if not isinstance(data.get(field), kind):
                errors.append(f"{provider}.{field}: missing or not {kind}")
        for tag in data.get("tags") or []:
            if tag not in TAGS:
                errors.append(f"{provider}.tags: unknown tag {tag!r}")
        for asn in data.get("asns") or []:
            if not isinstance(asn, int) or not 0 < asn < 2**32:
                errors.append(f"{provider}.asns: bad ASN {asn!r}")
        for cidr in data.get("cidrs") or []:
            try:
                ipaddress.ip_network(cidr, strict=False)
            except (TypeError, ValueError):
                errors.append(f"{provider}.cidrs: bad CIDR {cidr!r}")
        for domain in data.get("domains") or []:
            if not isinstance(domain, str) or not DOMAIN.fullmatch(domain):
                errors.append(f"{provider}.domains: bad domain {domain!r}")
        for kind, patterns in (data.get("regexes") or {}).items():
            for pattern in patterns if isinstance(patterns, list) else [patterns]:
                try:
                    if len(pattern) > 500:
                        raise ValueError("longer than 500 characters")
                    re.compile(pattern)
                except (TypeError, ValueError, re.error) as e:
                    errors.append(f"{provider}.regexes.{kind}: {pattern!r}: {e}")


def check_churn(old, new, old_bytes, new_bytes, errors):
    for provider in old:
        if provider not in new:
            errors.append(f"provider removed: {provider}")
    for field in ("cidrs", "domains", "asns"):
        before = sum(len(v.get(field) or []) for v in old.values())
        after = sum(len(v.get(field) or []) for v in new.values() if isinstance(v, dict))
        if before and (before - after) / before > MAX_TOTAL_LOSS:
            errors.append(f"total {field} {before} -> {after} (more than {MAX_TOTAL_LOSS:.0%} lost)")
        for provider, data in old.items():
            was = {str(x) for x in data.get(field) or []}
            now = {str(x) for x in (new.get(provider) or {}).get(field) or []}
            if len(was) >= MIN_SIZE:
                loss = len(was - now) / len(was)
                if loss > MAX_FIELD_LOSS:
                    errors.append(f"{provider}.{field} {len(was)} -> {len(now)} ({loss:.1%} of entries gone)")
    if old_bytes and new_bytes / old_bytes < MIN_BYTES_RATIO:
        errors.append(f"file size {old_bytes} -> {new_bytes} bytes")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True)
    parser.add_argument("--new", required=True)
    args = parser.parse_args()
    errors = []
    old_raw, old = load(args.old)
    try:
        new_raw, new = load(args.new)
    except (OSError, ValueError) as e:
        print(f"FAIL: new file does not load: {e}")
        return 1
    check_shape(new, errors)
    if not errors:
        check_churn(old, new, len(old_raw), len(new_raw), errors)
    for line in errors:
        print(f"FAIL: {line}")
    if errors:
        return 1
    print(f"OK: {len(new)} providers, {sum(len(v['cidrs']) for v in new.values())} CIDRs, {len(new_raw)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
