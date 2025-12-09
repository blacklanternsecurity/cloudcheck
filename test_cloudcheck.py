"""
Test script for cloudcheck functionality.
"""

import sys
import ipaddress
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from cloudcheck.providers.amazon import Amazon
from cloudcheck.helpers import defrag_cidrs, cidrs_to_strings, strings_to_cidrs


def test_v2fly_domains():
    # Create Amazon provider instance
    amazon = Amazon()

    # Fetch domains from v2fly
    domains, errors = amazon.fetch_v2fly_domains()

    assert domains, "No domains fetched from v2fly"
    assert not errors, "Failed to fetch domains from v2fly"
    print(f"Successfully fetched {len(domains)} domains")

    assert "kindle" in domains, "Kindle domain not found in fetched domains"

    # fetch cidrs from asndb


def test_cidr_defragmentation():
    """Test CIDR defragmentation with multiple iterations required."""
    print("Testing CIDR defragmentation...")

    # Create a complex set of CIDRs that requires multiple iterations to defragment
    # Start with /30 networks that should merge into /28, then /24, then /16
    cidr_strings = [
        # These /30s should merge into /27s (8 consecutive /30s = 1 /27)
        "192.168.1.0/30",  # 192.168.1.0-3
        "192.168.1.4/30",  # 192.168.1.4-7
        "192.168.1.8/30",  # 192.168.1.8-11
        "192.168.1.12/30",  # 192.168.1.12-15
        "192.168.1.16/30",  # 192.168.1.16-19
        "192.168.1.20/30",  # 192.168.1.20-23
        "192.168.1.24/30",  # 192.168.1.24-27
        "192.168.1.28/30",  # 192.168.1.28-31
        # These /30s should merge into another /27
        "192.168.2.0/30",  # 192.168.2.0-3
        "192.168.2.4/30",  # 192.168.2.4-7
        "192.168.2.8/30",  # 192.168.2.8-11
        "192.168.2.12/30",  # 192.168.2.12-15
        "192.168.2.16/30",  # 192.168.2.16-19
        "192.168.2.20/30",  # 192.168.2.20-23
        "192.168.2.24/30",  # 192.168.2.24-27
        "192.168.2.28/30",  # 192.168.2.28-31
        # Some /28s that should merge into /24s (16 consecutive /28s = 1 /24)
        "192.168.3.0/28",  # 192.168.3.0-15
        "192.168.3.16/28",  # 192.168.3.16-31
        "192.168.3.32/28",  # 192.168.3.32-47
        "192.168.3.48/28",  # 192.168.3.48-63
        "192.168.3.64/28",  # 192.168.3.64-79
        "192.168.3.80/28",  # 192.168.3.80-95
        "192.168.3.96/28",  # 192.168.3.96-111
        "192.168.3.112/28",  # 192.168.3.112-127
        "192.168.3.128/28",  # 192.168.3.128-143
        "192.168.3.144/28",  # 192.168.3.144-159
        "192.168.3.160/28",  # 192.168.3.160-175
        "192.168.3.176/28",  # 192.168.3.176-191
        "192.168.3.192/28",  # 192.168.3.192-207
        "192.168.3.208/28",  # 192.168.3.208-223
        "192.168.3.224/28",  # 192.168.3.224-239
        "192.168.3.240/28",  # 192.168.3.240-255
        # Some isolated networks that shouldn't merge
        "10.0.0.0/24",
        "172.16.0.0/16",
    ]

    print(f"Starting with {len(cidr_strings)} CIDR blocks")

    # Convert to network objects
    networks = strings_to_cidrs(cidr_strings)
    print(f"Converted to {len(networks)} network objects")

    # Defragment
    defragmented = defrag_cidrs(networks)
    defragmented_strings = cidrs_to_strings(defragmented)

    print(f"After defragmentation: {len(defragmented)} CIDR blocks")
    print("Defragmented CIDRs:")
    for cidr in sorted(defragmented_strings):
        print(f"  {cidr}")

    # Verify the results
    assert len(defragmented) < len(networks), (
        "Defragmentation should reduce the number of networks"
    )

    # Check that we have the expected merged networks
    expected_networks = {
        "192.168.1.0/27",  # Merged from 4 /30s
        "192.168.2.0/27",  # Merged from 4 /30s
        "192.168.3.0/24",  # Merged from 16 /28s
        "10.0.0.0/24",  # Unchanged
        "172.16.0.0/16",  # Unchanged
    }

    actual_networks = set(defragmented_strings)
    assert actual_networks == expected_networks, (
        f"Expected {expected_networks}, got {actual_networks}"
    )

    print("CIDR defragmentation test passed!")


def test_cidr_defragmentation_ipv6():
    """Test IPv6 CIDR defragmentation with multiple iterations required."""
    print("Testing IPv6 CIDR defragmentation...")

    # Create a complex set of IPv6 CIDRs that requires multiple iterations to defragment
    # Start with /126 networks that should merge into /125, then /124, then /120
    cidr_strings = [
        # These /126s should merge into a single /123
        "2001:db8::/126",  # 2001:db8::0-3
        "2001:db8::4/126",  # 2001:db8::4-7
        "2001:db8::8/126",  # 2001:db8::8-11
        "2001:db8::c/126",  # 2001:db8::c-f
        "2001:db8::10/126",  # 2001:db8::10-13
        "2001:db8::14/126",  # 2001:db8::14-17
        "2001:db8::18/126",  # 2001:db8::18-1b
        "2001:db8::1c/126",  # 2001:db8::1c-1f
        # These /126s should merge into another /123
        "2001:db8:1::/126",  # 2001:db8:1::0-3
        "2001:db8:1::4/126",  # 2001:db8:1::4-7
        "2001:db8:1::8/126",  # 2001:db8:1::8-11
        "2001:db8:1::c/126",  # 2001:db8:1::c-f
        "2001:db8:1::10/126",  # 2001:db8:1::10-13
        "2001:db8:1::14/126",  # 2001:db8:1::14-17
        "2001:db8:1::18/126",  # 2001:db8:1::18-1b
        "2001:db8:1::1c/126",  # 2001:db8:1::1c-1f
        # Some /124s that should merge into /120s (16 consecutive /124s = 1 /120)
        "2001:db8:2::/124",  # 2001:db8:2::0-f
        "2001:db8:2::10/124",  # 2001:db8:2::10-1f
        "2001:db8:2::20/124",  # 2001:db8:2::20-2f
        "2001:db8:2::30/124",  # 2001:db8:2::30-3f
        "2001:db8:2::40/124",  # 2001:db8:2::40-4f
        "2001:db8:2::50/124",  # 2001:db8:2::50-5f
        "2001:db8:2::60/124",  # 2001:db8:2::60-6f
        "2001:db8:2::70/124",  # 2001:db8:2::70-7f
        "2001:db8:2::80/124",  # 2001:db8:2::80-8f
        "2001:db8:2::90/124",  # 2001:db8:2::90-9f
        "2001:db8:2::a0/124",  # 2001:db8:2::a0-af
        "2001:db8:2::b0/124",  # 2001:db8:2::b0-bf
        "2001:db8:2::c0/124",  # 2001:db8:2::c0-cf
        "2001:db8:2::d0/124",  # 2001:db8:2::d0-df
        "2001:db8:2::e0/124",  # 2001:db8:2::e0-ef
        "2001:db8:2::f0/124",  # 2001:db8:2::f0-ff
        # Some isolated networks that shouldn't merge
        "2001:db8:3::/120",
        "2001:db8:4::/112",
    ]

    print(f"Starting with {len(cidr_strings)} IPv6 CIDR blocks")

    # Convert to network objects
    networks = strings_to_cidrs(cidr_strings)
    print(f"Converted to {len(networks)} network objects")

    # Defragment
    defragmented = defrag_cidrs(networks)
    defragmented_strings = cidrs_to_strings(defragmented)

    print(f"After defragmentation: {len(defragmented)} IPv6 CIDR blocks")
    print("Defragmented IPv6 CIDRs:")
    for cidr in sorted(defragmented_strings):
        print(f"  {cidr}")

    # Verify the results
    assert len(defragmented) < len(networks), (
        "Defragmentation should reduce the number of networks"
    )

    # Check that we have the expected merged networks
    expected_networks = {
        "2001:db8::/123",  # Merged from 8 /126s (4 pairs -> 4 /125s -> 2 pairs -> 2 /124s -> 1 pair -> 1 /123, but actually 8 /126s = 1 /124)
        "2001:db8:1::/123",  # Merged from 8 /126s (4 pairs -> 4 /125s -> 2 pairs -> 2 /124s -> 1 pair -> 1 /123, but actually 8 /126s = 1 /124)
        "2001:db8:2::/120",  # Merged from 16 /124s (8 pairs -> 8 /123s -> 4 pairs -> 4 /122s -> 2 pairs -> 2 /121s -> 1 pair -> 1 /120)
        "2001:db8:3::/120",  # Unchanged
        "2001:db8:4::/112",  # Unchanged
    }

    actual_networks = set(defragmented_strings)
    assert actual_networks == expected_networks, (
        f"Expected {expected_networks}, got {actual_networks}"
    )

    print("IPv6 CIDR defragmentation test passed!")


def test_cidr_defragmentation_mixed_ipv4_ipv6():
    """Test that both IPv4 and IPv6 addresses are defragmented correctly when mixed."""
    print("Testing mixed IPv4/IPv6 CIDR defragmentation...")

    # Create a list with both IPv4 and IPv6 CIDRs that should be defragmented
    cidr_strings = [
        # IPv4 networks that should merge
        "192.168.1.0/30",
        "192.168.1.4/30",
        "192.168.1.8/30",
        "192.168.1.12/30",
        # IPv6 networks that should merge
        "2001:db8::/126",
        "2001:db8::4/126",
        "2001:db8::8/126",
        "2001:db8::c/126",
        # IPv4 and IPv6 networks with same number of network bits (same prefix length)
        # IPv4 /30 = 30 network bits, IPv6 /30 = 30 network bits
        "172.16.0.0/30",
        "172.16.0.4/30",
        "2001:db8::/30",
        "2001:dbc::/30",
        # Isolated networks that shouldn't merge
        "10.0.0.0/24",
        "2001:db8:4::/120",
    ]

    print(f"Starting with {len(cidr_strings)} mixed CIDR blocks")

    # Convert to network objects
    networks = strings_to_cidrs(cidr_strings)
    print(f"Converted to {len(networks)} network objects")

    # Verify we have both IPv4 and IPv6
    ipv4_count = sum(1 for n in networks if isinstance(n, ipaddress.IPv4Network))
    ipv6_count = sum(1 for n in networks if isinstance(n, ipaddress.IPv6Network))
    assert ipv4_count > 0, "Should have IPv4 networks"
    assert ipv6_count > 0, "Should have IPv6 networks"
    print(f"Found {ipv4_count} IPv4 and {ipv6_count} IPv6 networks")

    # Defragment
    defragmented = defrag_cidrs(networks)
    defragmented_strings = cidrs_to_strings(defragmented)

    print(f"After defragmentation: {len(defragmented)} CIDR blocks")
    print("Defragmented CIDRs:")
    for cidr in sorted(defragmented_strings):
        print(f"  {cidr}")

    # Verify the results
    assert len(defragmented) < len(networks), (
        "Defragmentation should reduce the number of networks"
    )

    # Verify we still have both IPv4 and IPv6 after defragmentation
    defrag_ipv4_count = sum(
        1 for n in defragmented if isinstance(n, ipaddress.IPv4Network)
    )
    defrag_ipv6_count = sum(
        1 for n in defragmented if isinstance(n, ipaddress.IPv6Network)
    )
    assert defrag_ipv4_count > 0, (
        "Should still have IPv4 networks after defragmentation"
    )
    assert defrag_ipv6_count > 0, (
        "Should still have IPv6 networks after defragmentation"
    )

    # Check that we have the expected merged networks
    expected_networks = {
        "192.168.1.0/28",  # Merged from 4 /30s
        "172.16.0.0/29",  # Merged from 2 IPv4 /30s (same prefix length as IPv6 /30)
        "10.0.0.0/24",  # Unchanged
        "2001:db8::/124",  # Merged from 4 /126s
        "2001:db8::/29",  # Merged from 2 IPv6 /30s (same prefix length as IPv4 /30)
        "2001:db8:4::/120",  # Unchanged
    }

    actual_networks = set(defragmented_strings)
    assert actual_networks == expected_networks, (
        f"Expected {expected_networks}, got {actual_networks}"
    )

    print("Mixed IPv4/IPv6 CIDR defragmentation test passed!")
