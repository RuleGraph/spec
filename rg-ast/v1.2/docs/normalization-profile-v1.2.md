# RuleGraph AST Normalization Profile — v1.2

**Status:** Stable  
**Schema:** `https://rulegraph.org/schema/rg-ast/v1.2/rg-ast-v1.2.schema.json`  
**Back-compat:** v1.2 is a strict superset of v1.1 (all v1.1 ASTs remain valid/unchanged).

This profile defines how ASTs are **canonicalized** so equivalent expressions serialize to the same JSON. It is **structure-preserving** (no algebraic expansion) and **idempotent** (normalizing twice yields byte-identical JSON).  
LawCards should tag equations with:
```
"astProfile": "rg-ast/v1.2"
```

# Global rules

1. Idempotence: canon(canon(x)) == canon(x).
2. No algebraic expansion: never distribute mul over add, etc.
3. Deterministic order: children of add/mul are sorted by the Ordering Key (below).
4. Identities removed: drop additive 0 and multiplicative 1 (with safeguards noted below).
5. Zero annihilation: any product containing 0 becomes {"const": 0}.
6. Explicit signs: negatives are hoisted to a top-level {"neg": …} for mixed products; within pure-constant products the sign stays in the merged constant.
7. Rationals normalized: {"const":{"rat":{"p":p,"q":q}}} with q>0 and gcd(|p|,q)=1. -0.0 serializes as 0.
8. Structural only: semantic validity (e.g., well-formed piecewise) is enforced by the schema.

# Node normalization
**let**
```
{"let": [{"sym":"<LHS>"}, <RHS>]}
```

- LHS coerced to a sym node.
- Canonicalize only the RHS.

**add**

- Flatten nested add.
- Drop 0 terms.
- If all terms were 0 → {"const": 0}.
- Sort by Ordering Key.
- No like-term combining.

**mul**

- Flatten nested mul.
- Partition constants; merge to a single constant:
    - float×float → numeric multiply;
    - rat×rat → rational multiply + GCD reduction;
    - float×rat → numeric multiply (float).
- If any factor is 0 → {"const": 0}.
- Drop *1 (ensure at least one factor remains; if all were 1 → {"const": 1}).
- Sign handling: for mixed products hoist a single outer {"neg": …}; for pure constants keep sign in the constant.
- Sort non-constant factors by Ordering Key.

**div**

- Rewrite to product of reciprocal powers:
    - {"div":[N,D]} → {"mul":[N, …]} where each factor of D becomes {"pow":[base, {"const": -1}]}.
    - If a factor is already {"pow":[b,e]} use {"pow":[b, -e]}.
- Then normalize as mul.

**pow**

- Collapse nested powers: pow(pow(b,a), c) → pow(b, a*c) (normalize a*c as constant product if possible).
- Normalize exponent:
    - {"neg":{"const":k}} → {"const": -k}
    - constant mul exponents are merged to one constant;
    - identity: pow(x,1) → x.
- No domain-dependent rewrites (e.g., don’t force pow(x,0)→1).

If the merged exponent is an exact integer (e.g., -3.0 or -3/1), serialize it as {"const": -3} (an int), not a float or rational.

**neg**

- neg(neg(x)) → x.
- neg(const) becomes a single negated constant.

**vec**

- Canonicalize elements; do not reorder.

**call**
```
{"call":{"fn":"<name>","args":[...]}}
```

- Canonicalize args; preserve order.
- Math (v1.2): abs, sign, min, max, clamp, saturate, step, mix, exp, log, sqrt, sin, cos, tan, sinh, cosh, tanh.
- Relational (scalar 0/1 in arithmetic): lt, le, gt, ge, eq, ne.
- Logical: and, or, not.

**piecewise** (new in v1.2)
```
{
  "piecewise": {
    "cases": [
      {"if": <Node>, "then": <Node>},
      ...
    ],
    "otherwise": <Node>   // optional
  }
}
```

- Canonicalize each if, then, and otherwise.
- Do not reorder cases (first-true-wins semantics).
- Do not synthesize/remove otherwise.

# Ordering Key (total order for add/mul)

Type-then-value tuple:

1. sym → (0, sym_name)
2. const→ (1, value) where rationals use (p,q) and floats use numeric value
3. neg → (2, key(child))
4. pow → (3, key(base), key(exp))
5. call → (4, fn_name, [key(arg_i)…])
6. vec → (5, [key(elem_i)…])
7. other/object fallback → (9, sorted_keys)

Ties fall through by structure, ensuring a deterministic total order.

# Allowed constants

- {"const": <int|float>} (no NaN/Inf).
- {"const":{"rat":{"p":<int>,"q":<int≥1>}}} reduced; q>0.

# Examples

**Division → negative power**
```
IN : {"div":[{"sym":"a"},{"pow":[{"sym":"r"},{"const":3}]}]}
OUT: {"mul":[{"sym":"a"},{"pow":[{"sym":"r"},{"const":-3}]}]}
```

**Nested power collapse**
```
IN : {"pow":[{"pow":[{"sym":"r"},{"const":3}]},{"const":-1}]}
OUT: {"pow":[{"sym":"r"},{"const":-3}]}
```

**Sign handling in product**
```
IN : {"mul":[{"neg":{"sym":"x"}},{"const":-2},{"sym":"a"}]}
OUT: {"mul":[{"sym":"a"},{"sym":"x"},{"const":2}]}
```

**Piecewise (branches normalized, order preserved)**
```
IN : {"piecewise":{"cases":[
       {"if":{"call":{"fn":"le","args":[{"sym":"x"},{"const":1}]}},
        "then":{"div":[{"sym":"y"},{"sym":"r"}]}},
       {"if":{"call":{"fn":"gt","args":[{"sym":"x"},{"const":1}]}},
        "then":{"pow":[{"pow":[{"sym":"r"},{"const":3}]},{"const":-1}]}}
     ],
     "otherwise":{"sym":"z"}}}
OUT: {"piecewise":{"cases":[
       {"if":{"call":{"fn":"le","args":[{"sym":"x"},{"const":1}]}},
        "then":{"mul":[{"sym":"y"},{"pow":[{"sym":"r"},{"const":-1}]}]}},
       {"if":{"call":{"fn":"gt","args":[{"sym":"x"},{"const":1}]}},
        "then":{"pow":[{"sym":"r"},{"const":-3}]}}
     ],
     "otherwise":{"sym":"z"}}}
```
# Hashing guidance

When computing a LawCard’s sha256:

- Normalize ASTs per v1.2 first.
- Serialize with sorted keys and compact separators.
- Exclude sha256 and any signatures block from the digest.

# Compatibility

- v1.2 accepts all v1.1 nodes unchanged.
- New in v1.2: piecewise; extended call set (relations, logicals, elementary math).
- Canonicalizers must recurse into piecewise and call but must not reorder piecewise.cases or call.args.