"""Tests for scripts/validate_signatures.py: what the daily update may publish to stable.

Small hand-built fixtures, no network. The script is standard library only and is loaded by path,
the way the daily-update workflow runs it.
"""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("validate_signatures", ROOT / "scripts" / "validate_signatures.py")
vs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vs)


def provider(name, cidrs, domains=None, tags=None, **extra):
    data = {
        "name": name,
        "tags": tags if tags is not None else ["cloud"],
        "cidrs": cidrs,
        "domains": domains if domains is not None else [f"{name.lower()}.example"],
    }
    data.update(extra)
    return data


def cidrs(second_octet, count):
    return [f"10.{second_octet}.{i}.0/24" for i in range(count)]


def stable():
    return {
        "Alpha": provider("Alpha", cidrs(1, 40)),
        "Beta": provider("Beta", cidrs(2, 40)),
        "Gamma": provider("Gamma", cidrs(3, 40)),
    }


def run(tmp_path, old, new, new_raw=None):
    (tmp_path / "old.json").write_text(vs.dump(old))
    (tmp_path / "new.json").write_text(new_raw if new_raw is not None else vs.dump(new))
    out, held = tmp_path / "out.json", tmp_path / "held.txt"
    code = vs.main(["--old", str(tmp_path / "old.json"), "--new", str(tmp_path / "new.json"), "--out", str(out), "--held", str(held)])
    merged = json.loads(out.read_text()) if out.exists() else None
    held_list = held.read_text().split() if held.exists() else None
    return code, merged, held_list


def test_collapse_keeps_stable_entry_and_others_update(tmp_path):
    # The 11-16 shape: one provider's fetch breaks (GitHub 6737 -> 12), the rest are real updates.
    old = stable()
    new = stable()
    new["Alpha"]["cidrs"] = cidrs(1, 1)
    new["Beta"]["cidrs"] = cidrs(2, 45)
    code, merged, held = run(tmp_path, old, new)
    assert code == 2
    assert held == ["Alpha"]
    assert merged["Alpha"] == old["Alpha"]
    assert merged["Beta"]["cidrs"] == cidrs(2, 45)


@pytest.mark.parametrize(
    "field, value",
    [
        ("cidrs", cidrs(2, 39) + ["300.1.1.0/24"]),
        ("tags", ["cloud", ""]),
        ("tags", ["cloud", 7]),
        ("domains", ["Not A Domain"]),
        ("name", None),
    ],
)
def test_shape_failure_holds_back_only_that_provider(tmp_path, field, value):
    old = stable()
    new = stable()
    new["Beta"][field] = value
    new["Gamma"]["cidrs"] = cidrs(3, 41)
    code, merged, held = run(tmp_path, old, new)
    assert code == 2
    assert held == ["Beta"]
    assert merged["Beta"] == old["Beta"]
    assert merged["Gamma"]["cidrs"] == cidrs(3, 41)


def test_new_tag_is_accepted(tmp_path):
    new = stable()
    new["Alpha"]["tags"] = ["hosting"]
    code, merged, held = run(tmp_path, stable(), new)
    assert code == 0
    assert held == []
    assert merged["Alpha"]["tags"] == ["hosting"]


def test_optional_fields_are_checked_only_when_present(tmp_path):
    new = stable()
    new["Alpha"]["asns"] = [64512]
    new["Beta"]["asns"] = ["not-an-asn"]
    code, merged, held = run(tmp_path, stable(), new)
    assert code == 2
    assert held == ["Beta"]
    assert merged["Alpha"]["asns"] == [64512]


def test_failing_new_provider_is_left_out(tmp_path):
    new = stable()
    new["Delta"] = provider("Delta", ["not-a-cidr"])
    code, merged, held = run(tmp_path, stable(), new)
    assert code == 2
    assert held == ["Delta"]
    assert "Delta" not in merged


def test_provider_missing_from_fetch_keeps_stable_entry(tmp_path):
    old = stable()
    new = stable()
    del new["Gamma"]
    code, merged, held = run(tmp_path, old, new)
    assert code == 2
    assert held == ["Gamma"]
    assert merged["Gamma"] == old["Gamma"]


def test_total_loss_fails_the_whole_file(tmp_path):
    # Each provider loses 40%: under the per-provider bound, over the 10% total bound.
    new = stable()
    for name, octet in (("Alpha", 1), ("Beta", 2), ("Gamma", 3)):
        new[name]["cidrs"] = cidrs(octet, 24)
    code, merged, held = run(tmp_path, stable(), new)
    assert code == 1
    assert merged is None


def test_file_size_bound_fails_the_whole_file(tmp_path):
    old = stable()
    for data in old.values():
        data["long_description"] = "x" * 20000
    new = json.loads(vs.dump(old))
    for data in new.values():
        data["long_description"] = "short"
    code, merged, held = run(tmp_path, old, new)
    assert code == 1
    assert merged is None


def test_unloadable_fetch_fails_the_whole_file(tmp_path):
    code, merged, held = run(tmp_path, stable(), None, new_raw="{not json")
    assert code == 1
    assert merged is None


def test_current_file_passes_against_itself(tmp_path):
    path = ROOT / "cloud_providers_v3.json"
    current = json.loads(path.read_text())
    code, merged, held = run(tmp_path, current, current, new_raw=path.read_text())
    assert code == 0
    assert held == []
    # Byte for byte what the generator writes (cloudcheck_update: indent=1, sort_keys=True).
    assert (tmp_path / "out.json").read_text() == path.read_text()
