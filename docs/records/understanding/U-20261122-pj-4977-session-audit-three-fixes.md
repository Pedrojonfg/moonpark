---
id: U-20261122-pj-4977
person: pj
date: 2026-11-22T18:42:00Z
task: T-20261122-pj-b94d
---
# Auditor three remaining fixes — pj

## Concepts

| Concept | Role | Status | Source | Evidence | Next check |
|---------|------|--------|--------|----------|------------|
| platform-portable session memory | core | introduced | D-f3a8; `moonpark/session_memory.py` | correctly framed as mostly technical under existing Windows claim | — |
| footprint prefilter completeness | core | introduced | D-c1ed | chose measure-like-AABB then decide; falsification deferred to post-data keep/drop | after criba bench numbers |
| evidence-gated validation | core | demonstrated | D-a64b | chose local=compare / CI without data=honest fail / claims match; falsification=distrust of PC or PC cannot run — neither worrying | — |

## Notes

- Session continues T-b94d after independent auditor verify (2026-11-22): three open themes — Windows `resource`, lon prefilter miss, validation_full false green.
- Warm-up skipped: open debts (climatology, hazard proxy, nodata) do not touch these three fix themes.
- Approach (pj): Windows ≈ little to decide; map unclear; validation — data not in repo, so “missing → red” seems the fix.
- Teaching gap for Decide: distinguish script-red vs pytest-green; and “has data but did not compare”.
