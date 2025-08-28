#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Any, Dict, Set, Iterable

def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def find_all_refs(obj: Any) -> Iterable[str]:
    """Yield every $ref URI found anywhere in a JSON object."""
    if isinstance(obj, dict):
        if "$ref" in obj and isinstance(obj["$ref"], str):
            yield obj["$ref"].split("#", 1)[0]  # strip fragment
        for v in obj.values():
            yield from find_all_refs(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from find_all_refs(v)

def main() -> None:
    repo = Path(__file__).resolve().parents[2]  # <repo>/
    spec = repo / "spec"
    registry_file = spec / "registry.json"
    if not registry_file.exists():
        print(f"ERROR: missing {registry_file}", file=sys.stderr)
        sys.exit(2)

    reg = load_json(registry_file)
    schema_entries = reg.get("schemas", [])
    if not schema_entries:
        print("ERROR: spec/registry.json has no 'schemas' entries", file=sys.stderr)
        sys.exit(2)

    # Load schemas and build id -> contents map
    id2schema: Dict[str, dict] = {}
    for entry in schema_entries:
        sid = entry["id"]
        spath = spec / entry["path"]
        if not spath.exists():
            print(f"ERROR: listed schema not found: {spath}", file=sys.stderr)
            sys.exit(2)
        id2schema[sid] = load_json(spath)

    # Preflight: ensure every $ref target base URI is covered by registry
    unknown: Set[str] = set()
    for sid, sdict in id2schema.items():
        for ref_base in set(find_all_refs(sdict)):
            if ref_base and ref_base not in id2schema:
                unknown.add(ref_base)
    if unknown:
        print("ERROR: The following $ref targets are not present in spec/registry.json:", file=sys.stderr)
        for u in sorted(unknown):
            print("  -", u, file=sys.stderr)
        print("Fix: add these IDs to spec/registry.json (or update your $ref to use the registered $id).", file=sys.stderr)
        sys.exit(2)

    # Require modern offline resolver so no network is used
    try:
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource
    except Exception:
        print("ERROR: Missing offline resolver. Install:", file=sys.stderr)
        print("  pip install \"jsonschema>=4.21\" \"referencing>=0.30\"", file=sys.stderr)
        sys.exit(2)

    # Build a referencing.Registry with all known schemas
    from referencing import Registry, Resource

    pairs = [(sid, Resource.from_contents(s)) for sid, s in id2schema.items()]

    # Robust across versions of 'referencing'
    registry = Registry()
    for uri, resource in pairs:
        registry = registry.with_resource(uri, resource)


    total = 0
    failed = 0
    skipped_dirs = []

    for entry in schema_entries:
        sid = entry["id"]
        spath = spec / entry["path"]
        schema_dict = id2schema[sid]
        validator = Draft202012Validator(schema_dict, registry=registry)

        # Convention: examples live under ../examples/
        examples_dir = spath.parent.parent / "examples"
        if not examples_dir.exists():
            skipped_dirs.append(str(examples_dir.relative_to(spec)))
            continue

        for ex in sorted(examples_dir.rglob("*.json")):
            total += 1
            data = load_json(ex)
            errors = sorted(validator.iter_errors(data), key=lambda e: tuple(e.path))
            if errors:
                failed += 1
                print(f"❌ {ex.relative_to(spec)} (schema: {spath.relative_to(spec)})")
                for err in errors[:10]:
                    loc = "$" + "".join([f"[{p}]" if isinstance(p, int) else f".{p}" for p in err.path])
                    print(f"   - {loc}: {err.message}")
            else:
                print(f"✅ {ex.relative_to(spec)}")

        # Check invalid cases must fail (if present)
        invalid_dir = spath.parent.parent / "tests" / "invalid"
        if invalid_dir.exists():
            for ex in sorted(invalid_dir.rglob("*.json")):
                total += 1
                data = load_json(ex)
                errors = sorted(validator.iter_errors(data), key=lambda e: tuple(e.path))
                if errors:
                    print(f"✅ (expected fail) {ex.relative_to(spec)}")
                else:
                    failed += 1
                    print(f"❌ (should fail but passed) {ex.relative_to(spec)}")

    if skipped_dirs:
        print("\n(Info) No examples found under:", ", ".join(skipped_dirs))

    print(f"\nSummary: {total} example(s) validated, {failed} failed.")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
