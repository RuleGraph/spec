## RuleGraph World Schema

This doc explains the RuleGraph World schema—the JSON contract that describes a simulation world (frames, entities, and which LawCards apply to whom).

# Overview

A World is a portable JSON file that:

- Declares frames (units/metric),
- Lists entities (e.g., bodies with mass and state),
- Assembles dynamics (references to LawCards) with selectors (who is affected), overrides (parameter tweaks), and combination semantics (how multiple laws interact).

Goal: a strict, composable, and verifiable description that any engine can run deterministically, with space for custom extensions.

# Core Contract (v0.2)

- type: must be "rg:World"
- frames[0].units: must define { length, time, mass }
- entities[*]: bodies with mass and initial state
- dynamics[*]: each entry links to a LawCard (ref) and defines where/how it applies.

**Top-level fields**
```
{
  "id": "rg:world/yourworld.v1",
  "type": "rg:World",
  "version": "0.2.0",
  "profile": "rg:profile/planetary.v1",     // optional
  "frames": [ ... ],
  "entities": [ ... ],
  "dynamics": [ ... ],
  "config": { "dtSeconds": 60, "steps": 10000 },  // optional
  "provenance": { ... },                           // optional
  "ext": { ... },                                  // optional, namespaced
  "x-yourlab-note": "optional vendor field"
}
```

**Frames**
```
{
  "id": "rg:frame/inertial",
  "type": "rg:InertialFrame",
  "metric": "Euclidean",
  "units": {
    "length": "unit:M",
    "time":   "unit:S",
    "mass":   "unit:KG"
  }
}
```

**Entities (bodies)**
```
{
  "id": "rg:body/earth",
  "type": "rg:Body",
  "mass": { "value": 5.972e24, "unit": "unit:KG" },
  "state": {
    "frame": "rg:frame/inertial",
    "t": "2025-01-01T00:00:00Z",
    "position": { "value": [1.4959787e11, 0, 0], "unit": "unit:M" },
    "velocity": { "value": [0, 29780, 0],        "unit": "unit:M-PER-SEC" }
  }
}
```

**Dynamics (laws + scope + composition)**

Each dynamic references a LawCard (rules as data) and tells the engine where it applies and how to combine it with others.
```
{
  "ref": "rg:law/physics.gravity.newton.v1",
  "selector": { "pairs": [["rg:body/sun", "rg:body/earth"]] },
  "override": {
    "G": { "value": 6.6743e-11, "unit": "unit:M3-PER-KG-SEC2" }
  },
  "phase": 0,
  "combines": "additive"
}
```

**Selector options**:

{"pairs": [[id1, id2], ...]} — pairwise scope (e.g., gravity)
{"bodies": [id, ...]} — single-body scope (e.g., drag or thrust)
"all" — every applicable target

**Combines**:

- "additive" — forces sum, torques sum, etc.
- "exclusive" — only this law applies in its scope (others ignored in same phase)
- "nonlinear" — the engine must call a composition kernel (e.g., coupled constraints)

phase: integer ordering hint (lower phase runs earlier). Use to control sequencing between laws.

# Minimal Example (v0.2)
```
{
  "id": "rg:world/two-body.demo",
  "type": "rg:World",
  "version": "0.2.0",
  "frames": [
    {
      "id": "rg:frame/inertial",
      "type": "rg:InertialFrame",
      "metric": "Euclidean",
      "units": { "length": "unit:M", "time": "unit:S", "mass": "unit:KG" }
    }
  ],
  "entities": [
    {
      "id": "rg:body/sun",
      "type": "rg:Body",
      "mass": { "value": 1.9885e30, "unit": "unit:KG" },
      "state": {
        "frame": "rg:frame/inertial",
        "t": "2025-01-01T00:00:00Z",
        "position": { "value": [0, 0, 0], "unit": "unit:M" },
        "velocity": { "value": [0, 0, 0], "unit": "unit:M-PER-SEC" }
      }
    },
    {
      "id": "rg:body/earth",
      "type": "rg:Body",
      "mass": { "value": 5.972e24, "unit": "unit:KG" },
      "state": {
        "frame": "rg:frame/inertial",
        "t": "2025-01-01T00:00:00Z",
        "position": { "value": [149597870000.0, 0, 0], "unit": "unit:M" },
        "velocity": { "value": [0, 29780, 0], "unit": "unit:M-PER-SEC" }
      }
    }
  ],
  "dynamics": [
    {
      "ref": "rg:law/physics.gravity.newton.v1",
      "selector": { "pairs": [["rg:body/sun", "rg:body/earth"]] },
      "phase": 0,
      "combines": "additive"
    }
  ],
  "config": { "dtSeconds": 120, "steps": 21600 }
}
```

**Adding a linear drag law on one body**
```
{
  "ref": "rg:law/physics.fluids.drag.linear.v1",
  "selector": { "bodies": ["rg:body/earth"] },
  "override": { "gamma": { "value": 2.0e-2, "unit": "unit:KG-PER-SEC" } },
  "phase": 0,
  "combines": "additive"
}
```

# Extensibility

- ext: a reserved top-level object for namespaced, domain-specific blocks (e.g., ext: { "rg:aerodynamics": { ... } }).
- x- fields: vendor/experimental keys allowed anywhere by ^x- pattern (kept out of the strict core).
- Profiles: optional profile string to trigger extra constraints in future linters (e.g., “planetary motion profile”).

# Design Rationale

- Strict where it matters, flexible where it helps: We lock down core shapes (so engines can be confident) while allowing growth via ext and x-.
- Deterministic composition: phase provides an ordering hint; combines tells engines how to fold multiple dynamics (additive/exclusive/nonlinear).
- Explicit scope: selector makes law application unambiguous (pairs vs single-body vs all).
- Unit safety: first frame must define {length,time,mass}; quantities carry units.

# FAQ

**Q: Do I need profile?**
A: No. It’s for future domain presets (e.g., “planetary orbits” vs “crowd dynamics”) that external tools could enforce.

**Q: Can I mix fields from other domains?**
A: Yes—put domain-specific content in ext or vendor keys x-* without polluting the core.

**Q: How do I model multi-law interaction?**
A: Use multiple dynamics entries scoped by selector. Choose phase ordering and combines strategy to match your engine’s semantics.