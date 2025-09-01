# What’s new in LawCard v0.2 — Additions, Tightening & Migration

Summary: v0.2 makes cards more machine-robust and interoperable:

- AST becomes first-class (profile required),
- Symbols (names, units, dimensions, roles) standardize the interface,
- Dissipative laws are first-class,
- Extensions replace ad-hoc fields,
- Vendor keys gated behind x- prefixes.

# 1) Equations: explicit AST profile + canonical AST

Each equations[*] must declare:
```
"astProfile": "rg-ast/v1",
"ast": { ...canonical form... }
```

- Publisher tool enforces canonicalization (division→negative powers, flattened/sorted sums/products, neg(const k)→const(-k), zero short-circuit, etc.).
- Result: consistent hashing, easy equivalence checks, safer downstream evaluation.

Migration:
If a v0.1 card has machine only, run the publisher to generate ast and add "astProfile":"rg-ast/v1".

# 2) Symbols block

A structured declaration of model variables:
```
"symbols": {
  "F_vec": { "kind":"vector3", "unit":"unit:N", "dimension":{"L":1,"M":1,"T":-2}, "role":"output" },
  "r_vec": { "kind":"vector3", "unit":"unit:M", "dimension":{"L":1}, "role":"state-or-input" },
  "r":     { "kind":"scalar",  "unit":"unit:M", "dimension":{"L":1}, "role":"intermediate", "derivedFrom":["r_vec"] },
  "G":     { "kind":"scalar",  "unit":"unit:M3-PER-KG-SEC2", "dimension":{"L":3,"M":-1,"T":-2}, "role":"parameter" }
}
```

- kind: scalar | vector3 | … (future vectorN/tensor welcomed)
- unit: QUDT unit IRI
- dimension: SI base exponents (L,M,T,I,Θ,N,J)
- role: parameter | state | state-or-input | output | intermediate

Value: lets engines auto-check dimensional consistency and wire symbols to world state.

Migration: add a symbols map for the variables appearing in machine/ast.

# 3) Dissipative laws & invariants

- v0.2 adds invariants.dissipative: true|false.
- If true, empty conserves lists are valid (e.g., linear drag).
- Drift budgets remain allowed but are optional for dissipative laws.

Migration: for drag-like laws set:
```
"invariants": { "dissipative": true, "conserves": [] }
```

# 4) Extensions (replace ad-hoc core fields)

- v0.1’s stabilityModel → extension stability (own schema)
- v0.1’s testVectors → extension testVectors (own schema)
- Core schema now stays lean while allowing well-typed optional add-ons:

Stability: https://rulegraph.org/schema/lawcard/v0.2/extensions/stability.schema.json
Test vectors: https://rulegraph.org/schema/lawcard/v0.2/extensions/test-vectors.schema.json

Migration:

Rename stabilityModel → stability, conform to the extension schema.

Keep using your existing testVectors, now validated by the extension schema.

# 5) Vendor keys & hygiene

- Unknown fields must be prefixed: x-myorg-…
- Prevents silent drift and keeps the core interoperable.

Migration: rename custom fields (e.g., publisher, license, schema) to x-publisher, x-license, x-schema or adopt standardized locations (e.g., provenance for publisher/author; SPDX in x-license until a core slot is added).

# 6) Tightened validation & URLs

The schema $id and references now point to stable URLs under:

https://rulegraph.org/schema/lawcard/v0.2/...

https://rulegraph.org/schema/rg-ast/v1/...

Your validator picks v0.2 by default and enforces astProfile presence.

# Example (v0.2, conservative)
```
{
  "@context": { "id":"@id","type":"@type","rg":"https://rulegraph.org/vocab#","unit":"https://qudt.org/vocab/unit/","prov":"http://www.w3.org/ns/prov#"},
  "id":"rg:law/physics.gravity.newton.v1",
  "version":"1.0.0",
  "type":"rg:LawCard",
  "title":"Pairwise Newtonian Gravity",
  "kind":["rg:PairwiseLaw"],
  "symbols": { /* as shown above */ },
  "equations":[
    {
      "machine":"F_vec = -G*m1*m2/r**3 * r_vec",
      "tex":"\\vec F = -G\\,\\frac{m_1 m_2}{r^3}\\,\\vec r",
      "astProfile":"rg-ast/v1",
      "ast": { "let":[{"sym":"F_vec"}, {"neg":{"mul":[{"sym":"G"},{"sym":"m1"},{"sym":"m2"},{"pow":[{"sym":"r"},{"const":-3}]},{"sym":"r_vec"}]}}] }
    }
  ],
  "parameters": { "G":{"value":6.6743e-11,"unit":"unit:M3-PER-KG-SEC2","sigma":1.5e-15} },
  "validity": { "regimes": { "beta": { "desc":"v/c","max":0.1 } }, "assumptions":["Point masses","Weak field","No radiation reaction"] },
  "invariants": {
    "dissipative": false,
    "conserves":["Energy","LinearMomentum","AngularMomentum"],
    "driftBudget": { "Energy":{"rel":1e-5}, "LinearMomentum":{"rel":1e-6}, "AngularMomentum":{"rel":1e-6} }
  },
  "stability": { "cflHint":0.25, "dtMaxRuleMachine":"dt < 0.25*sqrt(r**3/(G*(m1+m2)))" },
  "testVectors": [ /* optional examples with tolerances */ ],
  "provenance": { "prov:wasAttributedTo":"RuleGraph" },
  "sha256":"…"
}
```

# Example (v0.2, dissipative)
```
{
  "...":"…",
  "id":"rg:law/physics.fluids.drag.linear.v1",
  "kind":["rg:SingleBodyLaw"],
  "symbols": { "v_vec": { "kind":"vector3","unit":"unit:M-PER-SEC","dimension":{"L":1,"T":-1},"role":"state-or-input" }, "gamma": { "kind":"scalar","unit":"unit:ONE-PER-SEC","dimension":{"T":-1},"role":"parameter" }, "F_vec": { "kind":"vector3","unit":"unit:N","dimension":{"L":1,"M":1,"T":-2},"role":"output" } },
  "equations":[
    { "machine":"F_vec = -gamma * v_vec", "astProfile":"rg-ast/v1", "ast":{"let":[{"sym":"F_vec"},{"neg":{"mul":[{"sym":"gamma"},{"sym":"v_vec"}]}}]} }
  ],
  "parameters": { "gamma": {"value": 0.02, "unit":"unit:PER-SEC"} },
  "invariants": { "dissipative": true, "conserves": [] },
  "provenance": { "prov:wasAttributedTo":"RuleGraph" },
  "sha256":"…"
}
```

# “Small fixes” v0.2 enforces

- Require astProfile + canonical ast (prevents parser drift).
- Normalize math structure (deterministic hashing, easier diff/merge).
- Stronger typing for symbols (units + dimensions + roles).
- Clean separation of core vs extensions.
- Vendor field hygiene (^x-), preventing accidental schema creep.

# Practical validation commands

Canonicalize AST & update sha256
```
python lawcards/tools/lawcard_publish.py path/to/card.json --schema https://rulegraph.org/schema/rg-ast/v1/rg-ast-v1.schema.json --in-place --update-sha256
```

Validate against LawCard v0.2 (core + extensions)
```
python lawcards/tools/validate_card.py path/to/card.json
```
