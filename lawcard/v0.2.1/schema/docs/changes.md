# What changed (v0.2 → v0.2.1)

1. Safer extensibility. Top-level vendor fields now use
patternProperties: { "^x-": {} } and additionalProperties: false (no more accidental property-name validation).

2. Equation “atoms/molecules” hooks (optional).

- equations[*].id — stable IRI for an individual equation (e.g., rg:eq/physics.gravity.newton.force.v1).
- equations[*].astSha256 — sha256 of the canonical AST node only (atom-level hash).

Card-level sha256 remains the molecule hash.

3. Symbol QoL. Optional symbols[*].domain string (e.g., "r > 0") for mild constraints/notes you already use.

4. Clarity/consistency.

- equations[*].astProfile fixed to const: "rg-ast/v1.2".
- stability and testVectors remain external extensions (no breaking change).
- provenance, numericProfile, usageHints unchanged, still optional/open.