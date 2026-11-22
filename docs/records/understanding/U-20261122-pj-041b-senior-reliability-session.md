---
id: U-20261122-pj-041b
person: pj
date: 2026-11-22T11:34:33Z
task: T-20261122-pj-b94d
---
# Senior reliability session — pj

## Concepts

| Concept | Role | Status | Source | Evidence | Next check |
|---------|------|--------|--------|----------|------------|
| region selection geometry | core | demonstrated | `docs/teaching/region-selection-geometry.pdf`, `cap_index.py` | Explained xy pre-filter vs lat/lon filter without repeating the brief; chose A-oracle strategy | — |
| cap grid membership | core | demonstrated | `D-20261122-pj-3e10`, pj chat | Preferred over-inclusion via footprint intersects rect; falsified mainly by bad induction or user confusion, not cost | engine ledger milestone |
| boundary cell disclosure | core | demonstrated | `D-20261122-pj-ae04`, pj chat | Always warn; no mandatory finer-mask refine v1; induced neighbors | build audit point 1 UI flags |

## Notes

- pj links falsification of membership policy to induction quality and UX comprehension, not compute cost.