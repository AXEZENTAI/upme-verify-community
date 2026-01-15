import os, time, hashlib

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def new_run_dir(base_dir: str = "runs") -> str:
    ts = time.strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(base_dir, f"run_{ts}")
    ensure_dir(run_dir)
    return run_dir

def write_text(path: str, content: str):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def write_manifest(dir_path: str):
    manifest = {}
    for root, _, files in os.walk(dir_path):
        for fn in files:
            if fn == "manifest.sha256":
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, dir_path)
            manifest[rel] = file_sha256(full)
    lines = [f"{h} {rel}" for rel, h in sorted(manifest.items())]
    write_text(os.path.join(dir_path, "manifest.sha256"), "\n".join(lines) + "\n")
    return manifest
