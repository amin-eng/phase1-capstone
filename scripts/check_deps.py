#!/usr/bin/env python3
"""
check_deps.py — Verify every package in requirements.txt is installed
                at the exact version listed.

Exits with code 0 if everything matches, 1 if anything is missing or mismatched.
"""

import sys
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path


def parse_requirements(path: Path) -> list[tuple[str, str]]:
    """
    Read requirements.txt and return a list of (package_name, expected_version).
    Skips blank lines and comments.
    Only supports the simple 'name==version' format — that's all we use.
    """
    deps = []
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()

        # Skip blank lines and comments
        if not line or line.startswith("#"):
            continue

        # We expect 'name==version'. Anything else is a problem we want to see.
        if "==" not in line:
            print(f"  ⚠️  Skipping unsupported line: {raw_line!r}")
            continue

        name, expected = line.split("==", 1)
        deps.append((name.strip(), expected.strip()))
    return deps


def check_one(name: str, expected: str) -> bool:
    """
    Check that `name` is installed and at version `expected`.
    Return True on success, False on any problem.
    """
    try:
        installed = version(name)
    except PackageNotFoundError:
        print(f"  ❌ {name}: NOT INSTALLED (expected {expected})")
        return False

    if installed == expected:
        print(f"  ✅ {name}=={installed}")
        return True
    else:
        print(f"  ❌ {name}: installed {installed}, expected {expected}")
        return False


def main() -> int:
    req_file = Path(__file__).resolve().parent.parent / "requirements.txt"

    print("=" * 50)
    print(f"  Dependency check: {req_file.name}")
    print("=" * 50)

    if not req_file.exists():
        print(f"  ❌ {req_file} not found")
        return 1

    deps = parse_requirements(req_file)
    if not deps:
        print("  ⚠️  No dependencies found in requirements.txt")
        return 1

    print(f"  Checking {len(deps)} package(s)...\n")

    failures = 0
    for name, expected in deps:
        if not check_one(name, expected):
            failures += 1

    print()
    print("=" * 50)
    if failures == 0:
        print("  ✅ All dependencies match.")
        print("=" * 50)
        return 0
    else:
        print(f"  ❌ {failures} mismatch(es). Run: pip install -r requirements.txt")
        print("=" * 50)
        return 1


if __name__ == "__main__":
    sys.exit(main())

