#!/usr/bin/env python3
"""Check a new cloud_providers_v3.json against the one on stable, and build the file to publish.

Clients download cloud_providers_v3.json from stable at runtime, so the daily push is the release.
This runs in the job that holds the push token, so it uses the standard library only.

Per provider: a provider that fails its checks (shape, values, or losing more than half of a fetched
field) keeps its entry from stable, and the other providers still update. A failing provider that
stable doesn't have yet is left out. Those providers are "held back".

Whole file: the merged result must keep the total of each fetched field within MAX_TOTAL_LOSS and
the file within MIN_BYTES_RATIO of stable's. A failure there means something broader is wrong, so
nothing is published.

Usage: validate_signatures.py --old <stable's file> --new <fetched file> [--out <merged>] [--held <list>]
Exit 0: everything passes. Exit 2: --out written, some providers held back (listed in --held and on
stdout). Exit 1: a whole-file check failed, or the fetched file doesn't load; --out not written.
"""

import argparse
import ipaddress
import json
import re
import sys

# What clients read. Everything else is type-checked only when present.
REQUIRED = {"name": str, "tags": list, "cidrs": list, "domains": list}
OPTIONAL = {
    "short_description": str,
    "long_description": str,
    "v2fly_company": str,
    "org_ids": list,
    "asns": list,
    "regexes": dict,
    "last_updated": (int, float),
}
FETCHED = ("cidrs", "domains", "asns")
DOMAIN = re.compile(r"[a-z0-9*_.-]{1,253}")

# Normal daily churn is well under these: over 44 daily updates the only provider to lose more than
# half of a field did so because its fetch broke.
MAX_FIELD_LOSS = 0.50  # a provider with at least MIN_SIZE entries loses more than half of a fetched field
MIN_SIZE = 20
MAX_TOTAL_LOSS = 0.10  # all CIDRs, all domains or all ASNs together drop by more than 10%
MIN_BYTES_RATIO = 0.80  # the file shrinks below 80% of its previous size


def dump(data):
    """The generator's own format (cloudcheck_update: indent=1, sort_keys=True)."""
    return json.dumps(data, indent=1, sort_keys=True)


def provider_problems(name, data, old):
    """Reasons this provider can't be published as fetched. Empty when it can."""
    if not isinstance(data, dict):
        return ["not an object"]
    problems = []
    for field, kind in REQUIRED.items():
        if not isinstance(data.get(field), kind):
            problems.append(f"{field}: missing or not {kind.__name__}")
    for field, kind in OPTIONAL.items():
        if field in data and not isinstance(data[field], kind):
            problems.append(f"{field}: not {kind}")
    for tag in data.get("tags") if isinstance(data.get("tags"), list) else []:
        if not isinstance(tag, str) or not tag.strip():
            problems.append(f"tags: {tag!r} is not a non-empty string")
    for cidr in data.get("cidrs") if isinstance(data.get("cidrs"), list) else []:
        try:
            ipaddress.ip_network(cidr, strict=False)
        except (TypeError, ValueError):
            problems.append(f"cidrs: bad CIDR {cidr!r}")
    for domain in data.get("domains") if isinstance(data.get("domains"), list) else []:
        if not isinstance(domain, str) or not DOMAIN.fullmatch(domain):
            problems.append(f"domains: bad domain {domain!r}")
    for asn in data.get("asns") if isinstance(data.get("asns"), list) else []:
        if isinstance(asn, bool) or not isinstance(asn, int) or not 0 < asn < 2**32:
            problems.append(f"asns: bad ASN {asn!r}")
    regexes = data.get("regexes") if isinstance(data.get("regexes"), dict) else {}
    for kind, patterns in regexes.items():
        for pattern in patterns if isinstance(patterns, list) else [patterns]:
            try:
                if not isinstance(pattern, str) or len(pattern) > 500:
                    raise ValueError("not a string of at most 500 characters")
                re.compile(pattern)
            except (ValueError, re.error) as e:
                problems.append(f"regexes.{kind}: {pattern!r}: {e}")
    if isinstance(old, dict):
        for field in FETCHED:
            was = {str(x) for x in old.get(field) or []}
            now = {str(x) for x in data.get(field) or []} if isinstance(data.get(field), list) else set()
            if len(was) >= MIN_SIZE:
                loss = len(was - now) / len(was)
                if loss > MAX_FIELD_LOSS:
                    problems.append(f"{field} {len(was)} -> {len(now)} ({loss:.1%} of entries gone)")
    return problems


def merge(old, new):
    """The file to publish, and the held-back providers with their reasons."""
    merged, held = {}, {}
    for name in sorted(set(old) | set(new)):
        if name not in new:
            merged[name] = old[name]
            held[name] = ["missing from the fetched file"]
            continue
        problems = provider_problems(name, new[name], old.get(name))
        if not problems:
            merged[name] = new[name]
        else:
            held[name] = problems
            if name in old:
                merged[name] = old[name]
    return merged, held


def whole_file_problems(old, merged, old_bytes, merged_bytes):
    problems = []
    for field in FETCHED:
        before = sum(len(v.get(field) or []) for v in old.values() if isinstance(v, dict))
        after = sum(len(v.get(field) or []) for v in merged.values() if isinstance(v, dict))
        if before and (before - after) / before > MAX_TOTAL_LOSS:
            problems.append(f"total {field} {before} -> {after} (more than {MAX_TOTAL_LOSS:.0%} lost)")
    if old_bytes and merged_bytes / old_bytes < MIN_BYTES_RATIO:
        problems.append(f"file size {old_bytes} -> {merged_bytes} bytes")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True)
    parser.add_argument("--new", required=True)
    parser.add_argument("--out")
    parser.add_argument("--held")
    args = parser.parse_args(argv)
    with open(args.old) as f:
        old_raw = f.read()
    old = json.loads(old_raw)
    try:
        with open(args.new) as f:
            new = json.load(f)
        if not isinstance(new, dict) or not new:
            raise ValueError("top level is not a non-empty object")
    except (OSError, ValueError) as e:
        print(f"FAIL: fetched file does not load: {e}")
        return 1
    merged, held = merge(old, new)
    merged_raw = dump(merged)
    problems = whole_file_problems(old, merged, len(old_raw.encode()), len(merged_raw.encode()))
    for line in problems:
        print(f"FAIL: {line}")
    if problems:
        return 1
    if args.out:
        with open(args.out, "w") as f:
            f.write(merged_raw)
    if args.held:
        with open(args.held, "w") as f:
            f.write("".join(f"{name}\n" for name in held))
    for name, reasons in held.items():
        print(f"HELD: {name}: {'; '.join(reasons[:3])}")
    print(f"OK: {len(merged)} providers, {sum(len(v['cidrs']) for v in merged.values())} CIDRs, {len(merged_raw)} bytes, {len(held)} held back")
    return 2 if held else 0


if __name__ == "__main__":
    sys.exit(main())
