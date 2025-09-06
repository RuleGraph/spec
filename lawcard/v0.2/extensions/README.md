# LawCard Extensions (v0.2.2)

Extensions let you attach **context, guidance, and governance** to a LawCard **without touching the executable core**. They validate independently, are **excluded from coreSha256**, and are **included in cardSha256**. Equation atom hashes (equations[*].astSha256) are **never affected by extensions**.

> Core schema: lawcard-v0.2.2.schema.json (see “properties” list for these references). 

# What’s in this folder?

These JSON Schemas define optional sections you can add under a LawCard’s top level. Each one is small, focused, and stable.

1) stability — **time-step heuristics**

**When**: Any dynamic rule used in time integration.
**Why**: Give simulators a safe Δt hint (CFL-style) and notes.

**Fields**

- cflHint (number): scale of recommended Δt relative to fastest mode.
- dtMaxRuleMachine (string): machine expression (not RG-AST) describing an upper bound, e.g. "dt < 0.5*sqrt(m/k)".
- dtMaxRuleTex (string): TeX mirror for docs.
- notes (string): caveats (e.g., “take min over participating masses”).

**Example**
```
"stability": {
  "cflHint": 0.5,
  "dtMaxRuleMachine": "dt < 0.5*sqrt(m/k)",
  "dtMaxRuleTex": "\\Delta t < 0.5\\sqrt{m/k}",
  "notes": "Heuristic for explicit integrators; choose min across bodies."
}
```

2) testVectors — **golden I/O checks**

**When**: Always if possible (it powers CI & regression).
**Why**: Converts your card into a self-testing spec.

**Fields (array of tests)**

- name (string)
- inputs (object): symbol→value (numbers, arrays)
- expected (object): one or more assertions like
    - { "<symbol>": { "value": <num|array>, "unit": "unit:..." } }
- tolerance (object): { "rel": <num> } and/or { "abs": <num> }

**Example**
```
"testVectors": [
  {
    "name": "Below threshold → linear",
    "inputs": { "alpha": 0.1, "beta": 0.5, "v_c": 2.0, "v_vec": [1,0,0] },
    "expected": { "F_mag": { "value": 0.1, "unit": "unit:N" } },
    "tolerance": { "rel": 1e-6 }
  }
]
```

3) validity — **regimes & assumptions**

**When**: You have applicability limits or assumptions to declare.
**Why**: Tools can warn or adapt when outside supported regimes.

**Fields**

- regimes (object of named regimes)
    - each: { "desc": string, "min": number?, "max": number? }
- assumptions (array of strings)

**Example**
```
"validity": {
  "regimes": {
    "lowMach": { "desc": "M ≲ 0.3 (incompressible)", "max": 0.3 }
  },
  "assumptions": [
    "Point masses", "Weak field", "No radiation reaction"
  ]
}
```

4) domains — **formal preconditions**

**When**: You need hard conditions like r > 0 or “clip on violation”.
**Why**: Lets engines check and optionally clip safely.

**Fields**

- symbols (object): per-symbol predicates as RG-AST nodes (v1.2).
- assume (array of RG-AST nodes): global predicates.
- onViolation ("warn" | "clip" | "error"): runtime policy.

**Example**
```
"domains": {
  "symbols": {
    "r": { "call": { "fn": "gt", "args": [ { "sym": "r" }, { "const": 0 } ] } }
  },
  "assume": [
    { "call": { "fn": "ge", "args": [ { "sym": "k" }, { "const": 0 } ] } }
  ],
  "onViolation": "warn"
}
```

5) numericProfile — **solver preferences**

**When**: You care about determinism/perf knobs.
**Why**: Hints for engines without changing physics.

**Fields**

- dtype: "float32" | "float64"
- fma: boolean
- order: "deterministic" | "fast"
- rngSeed: integer or null

**Example**
```
"numericProfile": { "dtype": "float64", "fma": true, "order": "deterministic" }
```

6) provenance — **who/when/source**

**When**: Always good hygiene.
**Why**: Traceability without touching the core.

**Fields (loose, PROV-flavored)**

- prov:wasAttributedTo (string): person/org
- prov:generatedAtTime (ISO 8601 string)
- sourceRepository (URL)
- optional: references pointer, commit id, etc.

**Example**
```
"provenance": {
  "prov:wasAttributedTo": "RuleGraph",
  "prov:generatedAtTime": "2025-09-04T00:00:00Z",
  "sourceRepository": "https://github.com/RuleGraph/lawcards"
}
```

7) references — **citations & mappings**

**When**: Cite literature/standards, or map paper variables → symbols.
**Why**: Academic rigor, reproducibility.

**Typical item**

- doi or url, title, citation
- equationRef (string like “Eq. (3.7)”)
- variableMap (object): { "paperVar": "cardSymbol" }

**Example**
```
"references": [
  {
    "doi": "10.1103/PhysRev.136.B1224",
    "title": "Einstein Equations...",
    "equationRef": "Eq. (12)",
    "variableMap": { "m_1": "m1", "m_2": "m2", "r": "r" }
  }
]
```

8) signatures — **multi-sig attestation**

**When**: Curated libraries, governance, or trust policies.
**Why**: Verify who signed this exact content.

**Fields**

- threshold (integer): minimum valid signatures.
- signers (array):
    - { "alg": "ed25519" | "secp256k1" | "...", "keyId": "did:...|https:...", "sig": "BASE64/HEX..." }

> Signing target: Usually cardSha256. Advanced flows MAY also sign coreSha256. Keep each signer’s policy clear in library docs.

**Example**
```
"signatures": {
  "threshold": 2,
  "signers": [
    { "alg": "ed25519", "keyId": "did:key:z6Mk...", "sig": "zJv8..." },
    { "alg": "ed25519", "keyId": "did:web:rulegraph.org#core", "sig": "zHkK..." }
  ]
}
```

9) schemaRefs — declared schema URIs

**When**: You want cards to be self-describing.
**Why**: Tools can re-fetch/validate with explicit versions.

**Fields**

- ast (string or array of strings): RG-AST schema URIs.
- lawcard (string or array): LawCard schema URIs.

**Example**
```
"schemaRefs": {
  "ast": "https://rulegraph.org/schema/rg-ast/v1.2/rg-ast-v1.2.schema.json",
  "lawcard": "https://rulegraph.org/schema/lawcard/v0.2.2/lawcard-v0.2.2.schema.json"
}
```

# Hashing & extensions (how it all fits)

**Atom hash**: equations[*].astSha256
Hash of the **canonicalized AST node only**. Never changes unless the math changes.

**Core hash**: coreSha256
Hash over **only the core** (id, version, type, title, license, kind, symbols, parameters, equations[id?,name?,astProfile,ast,astSha256], invariants).
Not affected by any extension content. Used by engines & lockfiles to prove “physics unchanged”.

**Card hash**: cardSha256
Hash over **the entire card** (core + extensions), excluding signatures. This is what libraries publish. Any extension edit (e.g., a new reference) will update cardSha256 but leave coreSha256 and all astSha256 unchanged. 

# Author checklist

- Put the physics in the core; put guidance & governance in extensions.
- Add at least one testVectors entry.
- Provide a stability hint for dynamic laws.
- Declare validity assumptions/regimes where relevant.
- Use domains for formal preconditions (e.g., r > 0).
- Record provenance and references for traceability.
- If curated, attach signatures; keep keys discoverable via keyId.
- Optionally add numericProfile to steer solvers.
- Include schemaRefs so tools know which spec version to use.
- Re-publish to refresh coreSha256/cardSha256 deterministically.
