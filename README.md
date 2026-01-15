# UPME-Verify (Community Edition)

**Independent verification** of optimization results and proof artifacts — with tamper-evident runpacks.

This repo is the **Community Edition** (demo-scale, fully checkable).  
For enterprise / government-scale verification, keep the *solver* you already use — UPME-Verify validates the outcome.

---

## What it does (Community Edition)
- ✅ **LP verification** via primal/dual certificates (semantic check)
- ✅ **Small MILP verification** (demo-size) with **checkable proof objects**
- ✅ **Proof bundle verification** (VIPR-like / PB-like *structural* checks)
- ✅ Outputs **VERIFIED / FAILED** + **hash-locked** artifacts

## What it does NOT do
- ❌ Does not replace Gurobi/CPLEX/SCIP
- ❌ No large-scale MILP verification in Community Edition
- ❌ No solver adapters in this public repo

---

## Quick start (local)
1) Download / clone this repo.
2) Run:

```bash
# Demo solve (creates a runpack in runs/)
python -m upme.cli solve examples/milp_knapsack_small.json --node_limit 50000

# Verify a proof bundle (demo)
python -m upme.cli verify examples/cert_bundles/vipr_bundle.json
python -m upme.cli verify examples/cert_bundles/pb_bundle.json
```

Runpacks appear in:
```
runs/run_YYYYMMDD_HHMMSS/
  problem.json
  result.json
  certificate.json
  manifest.sha256
  log.txt
```

---

## Why this is valuable
Verification reduces:
- audit friction
- rework cycles
- “are we sure?” meetings
- contractual / compliance exposure

---

## License
**Non-commercial / research only.** Commercial use requires permission.

## Enterprise / Government contact
If you need verification beyond demo-scale, contact:
**verification@your-domain.com**
