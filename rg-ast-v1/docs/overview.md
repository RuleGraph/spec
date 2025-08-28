# RG-AST v1 — Overview
Nodes: sym, const, neg, add, sub, mul, div, pow, vec, call(norm|dot|cross), let.
Canonicalization (enforced by tools): no div (rewrite), outer neg, flatten assoc ops, const-fold.
