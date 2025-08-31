# RG-AST v1 — Overview
 
The AST is intentionally small, strict, and canonical so that rules from different cards can be combined, verified, and reproduced across engines without ambiguity.
 
Here’s the design logic, piece by piece:

Tiny core = predictable composition
The node types are just: sym, const (incl. exact rationals), neg, add, sub, mul, div, pow, vec, call(norm|dot|cross), and let. That’s enough to express most analytic laws (forces, energies) while keeping the space of expressions easy to normalize, hash, and compare for equality. Fewer forms → fewer surprises when you inline one card into another. 

Canonical structure for hashing & diffing
Arrays are used for n-ary ops like add/mul (so we can flatten/sort operands), and 2-ary ops like div/pow use prefixItems with fixed arity. This makes canonicalization straightforward (e.g., replace a/b with mul(a, pow(b, -1)), sort commutative terms) which in turn stabilizes the SHA-256 over the canonical JSON. That’s why you can verify a card byte-for-byte across machines. 

Pure expressions (no side-effects)
Cards describe what a quantity is, not how to compute it procedurally. The only “binding” form is let([{"sym": "LHS"}, RHS]), which just says “this equation defines LHS”. That keeps rules declarative, so multiple cards can be composed by symbolic substitution/aggregation (e.g., total force = sum of forces from gravity + drag). 

Vectors are first-class, but limited ops are whitelisted
Many physical laws are vector-valued, so there’s vec and a minimal call set: norm, dot, cross. Limiting the function space prevents engine-specific semantics from leaking in, keeps evaluation portable, and allows safe unit/dimension checks.

Exactness where it matters
const can be a number or a rational { "rat": { "p": ..., "q": ... } } so canonicalization and equivalence work without floating-point drift (e.g., π approximations aside, many coefficients are exact). 

“additionalProperties”: false → no hidden semantics
Every node type is closed: no extra keys. That makes validation crisp and guarantees two equivalent formulas won’t hide different metadata or engine hints. Great for security, caching, and provenance audits. 

Why not a richer language now?
The goal of v1 is interoperability: enough math to cover classical mechanics, EM basics, and common constitutive laws, but not so much that two engines disagree. More advanced constructs (piecewise conditions, min/max/clamp, distributions, fields like ∇·F, ∇×F) are on a path for a future v2—added as explicit nodes once we lock their cross-engine semantics.

How this helps rules interact:

Aggregation: multiple cards can each produce a contribution (e.g., F_drag, F_grav) and a world/engine sums them because the trees are pure and typed.

Substitution: symbols line up (F_vec, r_vec, etc.), so one card’s RHS can feed another’s LHS without control-flow.

Auditing: a uniform AST lets you walk all trees to check dimensions, invariants, and stability hints consistently.

Portability: the same AST evaluates in Python, C++, JS, or on a GPU kernel, because it’s just structured data with a tiny op set.


- Francis Bousquet
