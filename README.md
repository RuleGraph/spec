# RuleGraph Spec Bundle

This folder contains **versioned, frozen specifications** for RuleGraph. Schemas are meant
to be resolved **offline** by tools; the `$id` URLs are identifiers, not network fetches (soon).

## What lives here

- `rg-ast-v1/` — canonical expression grammar (AST) for equations.
- `lawcard-v0.1/` — LawCard schema (references AST v1).
- `registry.json` — maps schema `$id` → local path (for offline validation).

Each versioned directory (`*-vX[.Y]/`) contains:
- `schema/*.json` — the JSON Schema (Draft 2020-12).
- `examples/*.json` — small, valid examples.
- `tests/invalid/*.json` — examples that **must fail** validation.
- `docs/*.md` — short normative guidance (authoring notes, canonicalization rules).

## Versioning & Freezing

- We use **SemVer** for schemas:
  - **MAJOR** — breaking validator/semantics
  - **MINOR** — backward-compatible additions
  - **PATCH** — non-functional clarifications
- Versioned directories are **immutable** after release. Any change → a **new dir** (e.g., `lawcard-v0.2/`).
- The whole bundle is versioned by `spec/VERSION` and tagged as `spec-vX.Y.Z`.

## Canonicalization & Hashing

LawCards include a `sha256` computed over **canonical JSON** with the `sha256` field removed.
Canonicalization rules live in authoring tools (see the `lawcards` repo).  
AST canonicalization: rewrite `div(a,b) → mul(a, pow(b,-1))`, prefer a single outer `neg`, flatten
associative ops, and constant-fold simple literals.

## Offline Validation

Use the bundle validator (no network):

```bash
python spec/tools/spec_validate_all.py

- Francis Bousquet