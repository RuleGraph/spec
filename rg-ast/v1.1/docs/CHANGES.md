# What goes into ATS v1.1

Extend call.fn with a small set of side-effect-free math ops:

- abs(x) — absolute value
- sign(x) — returns −1, 0, +1
- min(a,b,...), max(a,b,...) — commutative, variadic
- clamp(x, lo, hi) — equivalent to min(max(x, lo), hi)
- step(edge, x) — 0 if x < edge else 1
- mix(a, b, t) — linear interpolation: a*(1−t)+b*t (aka lerp)
- saturate(x) — shorthand for clamp(x,0,1)

These cover most “piecewise-lite” needs: stick–slip caps, penetration penalties only when >0, bounded gains, deadzones, and stable denominators (e.g., max(r, eps)).

Examples that can now be encoded :

- Friction cap: F_t = -clamp(k*v_t, -F_max, F_max)
- Contact penalty: F_n = k * max(0, -penetration)
- Safe denominator: F = … / max(r, eps)
- Lerp: mix(a, b, t) for parameter schedules
