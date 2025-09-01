## What Changed: v0.1 → v0.2

# Summary

- Typed, explicit dynamics: selector (pairs/bodies/all), override (typed bag), phase, combines.
- Strict core + extensions: additionalProperties: false on core; ext and ^x- open extension joints.
- Cleaner frames/units: required {length,time,mass} on the first frame; consistent rg:InertialFrame and Euclidean metric.
- Profiles (optional): a hook to layer domain-specific constraints later.

# Detailed changes

1. dynamics[*] structure

v0.1: typically { "ref": "rg:law/..." }, sometimes implicit usage.

v0.2:

- ref: required LawCard IRI (pattern enforced).
- selector: required (one of pairs|bodies|"all").
- override: optional, with typed { value, unit? } entries or scalars.
- phase: integer, defaults to 0.
- combines: "additive" | "exclusive" | "nonlinear".

2. Extensibility model

- New ext object for namespaced blocks.
- ^x- fields allowed at any level for vendor/experimental fields.
- Core objects (Frame, Body, State, Dynamic) now set additionalProperties: false.

3. Units and frames

- First frame must provide {length,time,mass}; reduces ambiguity across engines.

4. Validation discipline

- v0.2 schema is more predictable for engines and tools; fewer edge cases, easier to lint.