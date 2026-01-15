import json, hashlib, os

def stable_json(obj):
    return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False)

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)
