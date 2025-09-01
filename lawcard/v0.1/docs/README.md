## LawCard v0.1 — Model & Validation Guide

# Purpose

A LawCard captures a single law/rule as data: its equation(s), parameters, units, applicability, and reproducibility metadata. Cards are portable across engines and can be verified by hash.

# Document identity & context

- @context — JSON-LD-style aliases (stable URIs):

    - rg: https://rulegraph.org/vocab# (concepts/kinds)
    - unit: https://qudt.org/vocab/unit/
    - prov: http://www.w3.org/ns/prov#

- id — IRI for the law, e.g. rg:law/physics.gravity.newton.v1
- version — SemVer for this card document (e.g. 1.0.0)
- type — must be "rg:LawCard"
- title — human label
- kind — array of law kind tags, e.g. ["rg:PairwiseLaw"], ["rg:SingleBodyLaw"]

Semantics: id major (…v1) only changes on breaking law meaning; version changes on doc edits.

# Equations

equations is a list; each item:

- machine: a compact machine string (SymPy-friendly), e.g.
F_vec = -G*m1*m2/r**3 * r_vec

- tex: optional TeX rendering

- ast (optional in v0.1): a canonical JSON AST of the right-hand side (or let(lhs, rhs) form)

In v0.1, ast may be omitted (engines can parse machine). If present, it should follow rg-ast/v1 conventions, but v0.1 doesn’t strictly require the astProfile string.

# Parameters

parameters is a map of named constants:
```
"G": { "value": 6.6743e-11, "unit": "unit:M3-PER-KG-SEC2", "sigma": 1.5e-15 }
```

- value: number
- unit: QUDT unit IRI
- sigma: optional uncertainty (same unit scale)

# Validity (applicability domain)

validity.regimes — named regime constraints (e.g., beta for v/c):
```
"regimes": { "beta": { "desc": "v/c", "max": 0.1 } }
```

validity.assumptions — array of textual assumptions.

# Invariants & drift budgets
```
"invariants": {
  "conserves": ["Energy","LinearMomentum","AngularMomentum"],
  "driftBudget": {
    "Energy": { "rel": 1e-5 },
    "LinearMomentum": { "rel": 1e-6 },
    "AngularMomentum": { "rel": 1e-6 }
  }
}
```

- conserves: non-empty list of quantities the ideal law conserves.
- driftBudget: optional tolerances engines can audit against (relative).

v0.1 assumes conservative laws by default. Dissipative modeling is not first-class yet.

# Stability hints (optional in v0.1)

stabilityModel — integrator hints:
```
"stabilityModel": {
  "cflHint": 0.25,
  "dtMaxRuleMachine": "dt < 0.25*sqrt(r**3/(G*(m1+m2)))",
  "dtMaxRuleTex": "\\Delta t < 0.25\\sqrt{\\frac{r^3}{G(m_1+m_2)}}"
}
```
# Test vectors (optional in v0.1)

- testVectors — simple IO checks with tolerances.

# Provenance & integrity

- provenance — e.g. {"prov:wasAttributedTo":"RuleGraph","prov:generatedAtTime":"…"}
- sha256 — canonical digest over the card excluding sha256 itself (and any signatures), with sorted keys + compact separators.

# Minimal example (v0.1)
```
{
  "@context": {
    "id":"@id","type":"@type",
    "rg":"https://rulegraph.org/vocab#",
    "unit":"https://qudt.org/vocab/unit/",
    "prov":"http://www.w3.org/ns/prov#"
  },
  "id":"rg:law/physics.gravity.newton.v1",
  "version":"1.0.0",
  "type":"rg:LawCard",
  "title":"Pairwise Newtonian Gravity",
  "kind":["rg:PairwiseLaw"],
  "equations":[
    {
      "machine":"F_vec = -G*m1*m2/r**3 * r_vec",
      "tex":"\\vec F = -G\\,\\frac{m_1 m_2}{r^3}\\,\\vec r"
      // "ast": { ... } // optional in v0.1
    }
  ],
  "parameters":{
    "G":{"value":6.6743e-11,"unit":"unit:M3-PER-KG-SEC2","sigma":1.5e-15}
  },
  "validity":{ "regimes": { "beta": { "desc":"v/c","max":0.1 } }, "assumptions":["Point masses","Weak field"] },
  "invariants":{ "conserves":["Energy","LinearMomentum","AngularMomentum"] }
}
```

# Validation quick commands

- AST (rg-ast/v1) shape:
use your lawcards/tools/lawcard_publish.py with --schema https://rulegraph.org/schema/rg-ast/v1/rg-ast-v1.schema.json

- Card against v0.1:
python lawcards/tools/validate_card.py path/to/card.json --schema spec/lawcard/v0.1/schema/lawcard-v0.1.schema.json


Par : Francis Bousquet