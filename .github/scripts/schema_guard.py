#!/usr/bin/env python3
"""Guard the store schema against changes an older lerd cannot read.

A store definition reaches every install within a day, whatever version of lerd
it runs, so the schema may only grow. This compares the YAML in a pull request
against what is already published and refuses the two changes that break a
binary older than the definition: a key that disappeared, and a key whose type
moved under it. A value never before seen for a key that has always held a small
closed set is reported as a warning, since widening an enum breaks an old
binary's switch exactly as retyping does, but only the definition's author can
say whether the binary already knows the new value.

Usage: schema_guard.py <published-dir> <candidate-dir> [glob]
"""

import sys
import pathlib
import yaml

# A key whose published values number no more than this across the whole store
# is treated as a closed set, so a value outside it is worth a second look.
CLOSED_SET_MAX = 8


def type_name(value):
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, dict):
        return "map"
    if isinstance(value, list):
        return "list"
    if isinstance(value, (int, float)):
        return "number"
    if value is None:
        return "null"
    return "string"


def walk(node, prefix, types, values):
    """Flatten a document into path -> type and path -> observed scalar values.

    List elements collapse onto one `[]` path: the store cares that a list holds
    maps or strings, not what sits at index three.
    """
    kind = type_name(node)
    if prefix:
        types.setdefault(prefix, set()).add(kind)
    if isinstance(node, dict):
        for key, child in node.items():
            walk(child, f"{prefix}.{key}" if prefix else str(key), types, values)
    elif isinstance(node, list):
        for child in node:
            walk(child, f"{prefix}[]", types, values)
    elif prefix and kind in ("string", "bool", "number"):
        values.setdefault(prefix, set()).add(str(node))


def load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def profile(root, pattern):
    """Map every YAML file under root to its flattened type and value profile."""
    out = {}
    for path in sorted(pathlib.Path(root).rglob(pattern)):
        rel = str(path.relative_to(root))
        types, values = {}, {}
        try:
            walk(load(path), "", types, values)
        except yaml.YAMLError as err:
            out[rel] = ("unparseable", err)
            continue
        out[rel] = (types, values)
    return out


def closed_sets(profiles):
    """Union every file's observed values per path, keeping the small ones."""
    merged = {}
    for entry in profiles.values():
        if entry[0] == "unparseable":
            continue
        for path, vals in entry[1].items():
            merged.setdefault(path, set()).update(vals)
    return {p: v for p, v in merged.items() if len(v) <= CLOSED_SET_MAX}


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    published_dir, candidate_dir = sys.argv[1], sys.argv[2]
    pattern = sys.argv[3] if len(sys.argv) > 3 else "*.yaml"

    published = profile(published_dir, pattern)
    candidate = profile(candidate_dir, pattern)
    enums = closed_sets(published)

    failures, warnings = [], []

    for rel, entry in published.items():
        if rel not in candidate:
            warnings.append(f"{rel}: no longer published, an install that refetches it gets a 404")
            continue
        if entry[0] == "unparseable" or candidate[rel][0] == "unparseable":
            continue
        old_types, _ = entry
        new_types, new_values = candidate[rel]

        for path, kinds in sorted(old_types.items()):
            if path not in new_types:
                failures.append(f"{rel}: key `{path}` was removed, an older lerd still reads it")
                continue
            if kinds != new_types[path] and not kinds & new_types[path]:
                failures.append(
                    f"{rel}: key `{path}` changed type from {'/'.join(sorted(kinds))} "
                    f"to {'/'.join(sorted(new_types[path]))}"
                )

        for path, vals in sorted(new_values.items()):
            if path not in enums:
                continue
            for value in sorted(vals - enums[path]):
                warnings.append(
                    f"{rel}: key `{path}` takes the new value `{value}`; published values are "
                    f"{', '.join(sorted(enums[path]))}. Confirm every supported lerd understands it"
                )

    for line in warnings:
        print(f"warning: {line}")
    for line in failures:
        print(f"error: {line}")

    if failures:
        print(f"\n{len(failures)} change(s) an older lerd cannot read.")
        return 1
    print(f"\nschema guard passed ({len(published)} published file(s) checked, {len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
