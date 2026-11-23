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
| footprint prefilter completeness | core | demonstrated | D-6bf5 | drop lon (omissions), keep lat (0 omit in suite); falsifier=notably slower — rejected via precision-first + measured delta | broader lat bench |
| smooth fill inventing mid-scores between sparse points | core | introduced | D-3f81 | keep quadrants for simplicity; metric order feasible→RMSE→max\|e\|; hard to falsify (personal vision) | — |
| evidence-gated validation | core | demonstrated | D-a64b | chose local=compare / CI without data=honest fail / claims match; falsification=distrust of PC or PC cannot run — neither worrying | — |

## Notes

- Session continues T-b94d after independent auditor verify (2026-11-22): three open themes — Windows `resource`, lon prefilter miss, validation_full false green.
- Warm-up skipped: open debts (climatology, hazard proxy, nodata) do not touch these three fix themes.
- Approach (pj): Windows ≈ little to decide; map unclear; validation — data not in repo, so “missing → red” seems the fix.
- Teaching gap for Decide: distinguish script-red vs pytest-green; and “has data but did not compare”.
