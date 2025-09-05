# LawCard Extensions

A catalog of optional extension schemas for LawCards. These let you attach **domain-specific hints** (geometry, frames), **operational guidance** (stability, numeric), and **meta** (references, signatures).

All extensions are optional. Cards remain valid if they omit them.

In a card, include the matching property if you need it

# Extension catalog (what / when to use)

1) stability

What: Timestep heuristics and notes for explicit/implicit integrators.
When: Any dynamic law that benefits from a CFL-like bound or rule-of-thumb time step.
How: Provide dtMaxRuleMachine (machine string), optional TeX, and doc notes.

2) testVectors

What: Minimal input→expected output pairs (goldens) for sanity checks.
When: Every card if possible — it drives CI and regression testing.
How: Provide inputs, expected values/units, and a tolerance.

3) references

What: Bibliographic links (DOI/URL/textbook) to the source of the law.
When: Whenever you cite literature or a standard.
How: Prefer DOI if available; add equationRef/variableMap when helpful.

4) frames

What: Which reference frames each symbol lives in; optional transforms.
When: Multi-frame contexts (body vs. lab; rotating frames; robotics).
How: Map symbols→frame, declare default, optionally list transforms.

5) domains

What: Formal domain constraints as rg-ast predicates (e.g., r ≥ 0).
When: You have hard preconditions or safety clips.
How: Put symbol conditions under symbols and global assumptions under assume. Choose onViolation: warn|clip|error.

6) geometry

What: Pairing mode, neighbor cutoffs, PBC, softening.
When: N-body or particle systems (e.g., LJ, gravity, dipoles).
How: Set pairing, cutoff, periodicBox, optionally softening.

7) stochastic

What: Noise sources affecting targets (e.g., force jitter).
When: Langevin dynamics, uncertainty injection, randomized actuation.
How: List terms with distribution, parameters, and the target symbol.

8) calibration

What: Bounds/priors for parameters and target observables for fitting.
When: You intend to tune parameters to data.
How: parameters.<name>.bounds/prior, plus targets with weights.

9) composition

What: How to combine this rule with others (category, accumulation, splitting).
When: Complex worlds where multiple laws interact.
How: Set category (e.g., force), accumulation (sum/max), and an operator-splitting hint (e.g., Lie, Strang).

10) constraints

What: Holonomic/non-holonomic constraints with enforcement hints.
When: Bonds, joints, or general residuals g(q,t)=0.
How: Provide residualMachine, enforcement mode (penalty|lagrange|projection), and optional Jacobian hints.

11) boundaryConditions

What: Walls, inflow/outflow, periodic or custom boundaries.
When: Fluids, contacts, or domain-bounded motion.
How: Array of regions with type and parameters (e.g., restitution).

12) vizHints

What: Simple plotting suggestions for quick looks.
When: You want a default visualization (e.g., norm(F_vec) over time).
How: Provide plots with x, y, title, and kind.

13) numericHints

What: Solver-facing hints (sparsity, favorite integrator, vector width).
When: Performance matters or a particular solver is recommended.
How: Set sparsity, suggestedIntegrator, and optional vectorWidth.

14) digitalSignatures

What: Multi-signature attestation of the card’s content.
When: Governance, provenance, or curated libraries.
How: Provide threshold and a list of {alg, keyId, sig} signers.

15) nonDimensionalization

What: Canonical scales and derived dimensionless numbers.
When: Analysis/comparison across systems; nondimensional code paths.
How: Map physical scales (scales) and formulas for dimensionless groups.

16) contactModel

What: Parameters for impacts and friction.
When: Rigid/soft contacts, granular media, robotics.
How: Set restitution; define a friction model and parameters.

17) couplingFields

What: External fields/grids to sample (e.g., EM/B fields, CFD grids).
When: Multi-physics coupling or data-driven forces.
How: List named fields with a source URI and interpolant.