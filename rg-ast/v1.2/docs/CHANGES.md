# What changed vs v1.1 (at a glance)

New node: **piecewise**

- Structure: { "piecewise": { "cases": [ { "if": <Node>, "then": <Node> }, ... ], "otherwise": <Node>? } }
- Evaluated in order; first true if wins; optional otherwise as fallback.

**Relational + logical ops** (via call)

- Added lt, le, gt, ge, eq, ne and and, or, not.
- Semantics guidance (for docs/tooling): relations yield scalar indicators (0/1) when used in arithmetic; logicals compose those conditions.

**Elementary math bump** (via call)

- Added exp, log, sqrt, sin, cos, tan, sinh, cosh, tanh.
- Complements v1.1’s numeric utilities (abs, sign, min, max, clamp, saturate, step, mix).

**Compatibility**

v1.2 is a strict superset of v1.1: all valid v1.1 ASTs validate under v1.2 unchanged.

Canonicalizers should recurse into piecewise but must not reorder cases.