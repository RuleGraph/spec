RuleGraph AST — Normalization Profile v1

Goal: Any two tools that “normalize v1” produce identical bytes from equivalent math, enabling stable sha256, diffs, caching, and provenance.

This profile does not change the grammar. It specifies pure rewrites and ordering rules to put an AST in a deterministic normal form. Engines MUST accept already-normalized trees and SHOULD normalize inputs before hashing or publishing.

# 0) Notation & Safety

We show fragments like {"mul":[...]} ~> {"mul":[...]} to mean “rewrite to”.

These rewrites are algebraically safe and deliberately minimal:

No evaluation beyond identities (e.g., we don’t expand (𝑎 + 𝑏)2(a+b)2, we don’t simplify sin(0)).
No re-association of non-commutative ops.
No floating-point rounding changes.

# 1) Rewrite Pipeline (high level)

Apply these phases in order to the whole tree until no changes occur:

Primitive rewrites
1.1 Division to reciprocal power
1.2 Negative canonicalization
1.3 Power collapse

Tree shaping
2.1 Flatten commutative n-ary ops (add, mul)
2.2 Remove identity elements / short-circuit zeros

Deterministic ordering
3.1 Recursively normalize all children
3.2 Sort operands of add/mul by the total order defined here

Final cleanup (idempotence checks)

Normalization MUST be idempotent: a second pass makes no changes.

# 2) Primitive rewrites
2.1 Division → reciprocal power
   {"div":[A,B]} ~> {"mul":[A, {"pow":[B, {"const":-1}]}]}

  Rationale: reduces forms to {add, mul, pow}. Keeps exponent rules consistent.

2.2 Canonical negative

  If the grammar produced JSON {"const":-c} that’s fine; but unary minus on non-numbers MUST be represented as:

    -X → {"neg": X}

Double negation: {"neg":{"neg":X}} ~> X.

In products, pull all explicit negative constants to the front:

{"mul":[-2, X]} is allowed by JSON, but canonical form is either:

{"neg":{"mul":[2, X]}} (preferred when there exists at least one negative factor), or

keep the sign on a single const child if the product is a single factor.

Rationale: exactly one place carries the sign; makes diffs stable.

2.3 Power collapse

{"pow":[ {"pow":[X, A]}, B ]} ~> {"pow":[ X, {"mul":[A,B]} ]}

{"pow":[ X, {"const":1} ]} ~> X

Do not simplify {"pow":[X, {"const":0}]} except when X is trivially non-zero; to stay conservative, this profile does not rewrite pow(X,0).

# 3) Tree shaping
3.1 Flatten commutative n-ary ops

{"add":[X, {"add":[Y,Z]}]} ~> {"add":[X,Y,Z]}

{"mul":[X, {"mul":[Y,Z]}]} ~> {"mul":[X,Y,Z]}

Iterate until no nested add/mul remain.

3.2 Identities & short-circuits

Remove identity elements:

{"add":[..., {"const":0}]} → drop the zero

{"mul":[..., {"const":1}]} → drop the one

{"pow":[X, {"const":1}]} → X

Zero product short-circuit:

If any child of mul is exactly {"const":0}, the whole product normalizes to {"const":0}.

Do not introduce {"const":1} as a replacement for empty mul/add. Keep at least one operand.

# 4) Deterministic ordering (for add and mul)

Operands of commutative ops MUST be sorted stably by this total order:

4.1 Type precedence (ascending)

sym, const, neg, pow, call (then by fn name), vec, Any other node types (future-proof: compare by key name lexicographically)

4.2 Within the same type

sym: lexicographic by symbol string.

const:

Compare by numeric value (exactly, if both are JSON numbers).

If both are rationals {"rat":{"p":...,"q":...}}, compare by p/q with integer arithmetic; tie-break by (abs(p)+q) then by (p,q) lexicographic to get a stable order.

If one is rational and the other is a JSON number, do not coerce; sort by numeric value (use high-precision rational vs decimal comparison if needed).

neg: compare by the normalized inner node (recursively).

pow: compare base first (recursively), then exponent.

call: compare by fn string (cross > dot > norm alphabetically) and then lexicographically by arguments.

vec: compare lexicographically by elements (recursively).

Implementation tip: define a (tag, key1, key2, …) tuple for each node and use Python’s tuple ordering; ensure recursion uses already-normalized children.

# 5) Constants

The schema allows numbers or rationals:

{"const": 3.5} or {"const": {"rat":{"p":7,"q":2}}}

This profile does not auto-convert floats to rationals or vice-versa.

Keep the literal as authored; only move signs per §2.2 when inside products.

# 6) let form

{"let":[ {"sym":"LHS"}, RHS ]} is the canonical equation node.

Normalize RHS per this profile.

Do not reorder let entries and do not inline them automatically in this profile.

If a card has multiple equations, the container (LawCard JSON) decides ordering; this profile is expression-local.

# 7) Calls & vectors

Allowed calls in v1: {"call":{"fn":"norm","args":[...]}}, "dot", "cross".

Normalize all args recursively; no additional call-specific rewrites.

vec is an ordered tuple; do not sort vector elements.

# 8) Canonical JSON for hashing

When computing the card’s sha256, first ensure AST normalization, then:

Remove the sha256 field from the card object.

Serialize JSON with:

UTF-8

sorted object keys (sort_keys=true)

no extra whitespace (separators=(",",":"))

Hash the resulting bytes via SHA-256 (hex-lowercase output recommended).

This yields stable bytes across platforms.

# 9) Provenance markers 

Publishers SHOULD set:
```bash
"provenance": {
  "rg:astProfile": "rg-ast/normalize-v1",
  "rg:canonicalizer": "rg-canon/1.0.0",
  "prov:wasAttributedTo": "RuleGraph",
  "prov:generatedAtTime": "2025-08-24T12:05:00Z"
}
```

Engines MAY record which profile they accepted when caching.

# 10) Examples
10.1 Division + sign + exponent

Input
```bash
{"let":[{"sym":"F_vec"},
  {"mul":[
     {"const":-1},
     {"sym":"G"},
     {"sym":"m1"},
     {"sym":"m2"},
     {"div":[{"sym":"r_vec"},{"pow":[{"sym":"r"},{"const":3}]}]}
  ]}
]}
```

Normalized
```bash
{"let":[{"sym":"F_vec"},
  {"neg":{
    "mul":[
      {"sym":"G"},
      {"sym":"m1"},
      {"sym":"m2"},
      {"sym":"r_vec"},
      {"pow":[{"sym":"r"},{"const":-3}]}
    ]
  }}
]}
```

Rules used: §2.1, §2.2, §3.1, §3.2, §4.

10.2 Flatten & sort

Input
```bash
{"add":[
  {"mul":[{"sym":"b"},{"sym":"a"}]},
  {"mul":[{"sym":"a"},{"sym":"b"},{"const":1}]},
  {"mul":[{"sym":"a"},{"sym":"c"}]
}]}
```

Normalized
```bash
{"add":[
  {"mul":[{"sym":"a"},{"sym":"b"}]},
  {"mul":[{"sym":"a"},{"sym":"b"}]},
  {"mul":[{"sym":"a"},{"sym":"c"}]}
]}
```

(Flattened, removed *1, and sorted factors within each mul so a<b<c by symbol name.)

# 11) Conformance

A canonicalizer conforms to Profile v1 if:

Idempotence: For every valid rg-ast v1 node N, normalize(normalize(N)) == normalize(N).

Determinism: On identical inputs, byte-identical outputs are produced across platforms.

Safety: Only the rewrites in this document are applied.

Ordering: add/mul children are sorted by the total order in §4.

Test recommendation:

Provide 10–20 fixtures: pairs of {input.json, normalized.json}.

CI must fail if the tool’s output differs from the normalized fixtures.

# 12) Versioning & Evolution

This document is Normalization Profile v1 for rg-ast v1.

Grammar extensions (e.g., piecewise, min/max, field operators) will be a new rg-ast v2 with its own profile.
