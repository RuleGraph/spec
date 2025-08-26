# RuleGraph Spec

Authoritative context and JSON Schemas for RuleGraph’s data model.

- JSON-LD contexts (prefixes, types) under `contexts/`
- Validation schemas (Draft 2020-12) under `schema/`

**License:** Apache-2.0.

---

## Namespaces

- `rg:` → `https://rulegraph.org/schema#`
- `unit:` → `https://qudt.org/vocab/unit/`
- `prov:` → `http://www.w3.org/ns/prov#`

---

## Artifacts

- `contexts/rulegraph-v1.jsonld` — minimal context for World / Frame / Body / LawCard.
- `schema/world.schema.json` — minimal World/Frame/Body model for v0.
- `schema/lawcard.schema.json` — LawCard with equations/validity/invariants/stability/provenance/hash.

These are **minimum viable**; expansions happen via RFCs in issues.

---

