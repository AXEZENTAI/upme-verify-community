import hashlib

def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def verify_vipr_bundle(bundle: dict) -> dict:
    need = ["type","format","solver","claimed_bound","artifacts","ledger"]
    if not all(k in bundle for k in need):
        return {"verified": False, "type":"vipr_bundle", "status":"MISSING_FIELDS", "details":{}}
    bad = []
    for name, obj in bundle.get("artifacts", {}).items():
        if _sha(obj.get("content","")) != obj.get("sha256",""):
            bad.append(name)
    ledger = bundle.get("ledger", [])
    ok = (len(bad)==0) and isinstance(ledger, list) and len(ledger)>0
    return {
        "verified": bool(ok),
        "type":"vipr_bundle",
        "status": "VERIFIED_BUNDLE" if ok else "BUNDLE_HASH_FAIL",
        "details": {"bad_artifacts": bad, "ledger_events": len(ledger)}
    }
