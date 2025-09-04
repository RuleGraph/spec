# RuleGraph Vocabulary

**Purpose.** This repo hosts RuleGraph’s public JSON-LD vocabulary: common prefixes (e.g., `rg`, `unit`, `prov`), controlled terms (law kinds, roles, invariants, capabilities), and governance metadata used across LawCards, worlds, and tools.

**Primary context:** `https://rulegraph.org/vocab/vocab.jsonld`  
**Terms registry:** `https://rulegraph.org/vocab/terms.jsonld`

---

## Layout

spec/vocab/vocab.jsonld # Base JSON-LD context (prefixes + stable core terms)
spec/vocab/terms.jsonld # Controlled terms (SKOS graph with labels/notes/status)
versions/


- Serve with `Content-Type: application/ld+json`.
- Versioned snapshots are immutable; `terms.jsonld` is the moving head.

## Use in LawCards

In your card JSON:

```
"@context": "https://rulegraph.org/vocab/vocab.jsonld"
```

Optionally pin a snapshot for fully reproducible builds:
```
"@context": [
  "https://rulegraph.org/vocab/vocab.jsonld",
  "https://rulegraph.org/vocab/versions/2025-09-03.jsonld"
]
```

Then use compact IRIs:
```
"kind": ["rg:PairwiseLaw"],
"invariants": { "conserves": ["rg:Energy", "rg:AngularMomentum"] }
```

# Adding / Changing Terms

Propose changes in spec/vocab/terms.jsonld (add concepts under rg: with skos:prefLabel, rg:status, optional skos:note).

Keep backward compatibility; deprecate via rg:status: "deprecated" rather than delete.

When a set of changes stabilizes, cut a snapshot into spec/vocab/versions/<YYYY-MM-DD>.jsonld.

# Conventions

Prefixes:

- rg → https://rulegraph.org/vocab#
- unit → https://qudt.org/vocab/unit/
- prov → http://www.w3.org/ns/prov#

Terms are lowercase kebab where practical (e.g., rg:singleBodyLaw, rg:pairwiseLaw, rg:output).

Keep human-readable skos:prefLabel and a brief skos:definition or skos:note.

# License

Content here is CC-BY-4.0 unless noted otherwise. Contributions imply you have rights to license under CC-BY-4.0.

**Questions?** Open an issue in this repo with a minimal example of the term(s) you need and how they’ll be used in LawCards or worlds.
