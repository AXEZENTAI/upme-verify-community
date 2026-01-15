import argparse, os, json
from .utils import stable_json
from .runpack import new_run_dir, write_text, write_manifest
from .milp import milp_from_json, solve_milp_exact
from .cert_hub import verify_certificate
from .certs.lp_cert import verify_lp_certificate

def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def cmd_solve(args):
    spec = _load_json(args.problem_json)
    run_dir = new_run_dir()
    os.makedirs(run_dir, exist_ok=True)

    if spec.get("type") == "milp":
        milp = milp_from_json(spec)
        cert = solve_milp_exact(milp, node_limit=args.node_limit)
        result = {"mode": "CERTIFIED" if cert["provable_optimality"] else "HEURISTIC", "best_x": cert["best_x"], "best_objective": cert["best_objective"], "milp_certificate": cert}
        write_text(os.path.join(run_dir, "problem.json"), stable_json(spec))
        write_text(os.path.join(run_dir, "result.json"), stable_json(result))
        write_text(os.path.join(run_dir, "certificate.json"), stable_json({"method":"milp_demo_enumeration","bounds":{"provable_optimality": cert["provable_optimality"], "scope": cert["scope_note"]}}))
        write_manifest(run_dir)
        write_text(os.path.join(run_dir, "log.txt"), "UPME-Verify CE runpack\n")
        print(f"[UPME-Verify CE] Runpack: {run_dir}")
        return

    if spec.get("type") == "lp":
        lp = spec.get("lp", {})
        n = len(lp.get("c", []))
        m = len(lp.get("b", []))
        cert = {"type":"lp_primal_dual", "lp": lp, "primal_x":[0.0]*n, "dual_y":[0.0]*m}
        v = verify_lp_certificate(cert, tol=args.tol)
        result = {"mode": "CERTIFIED" if v["verified"] else "FAILED", "lp_verification": v, "best_x": cert["primal_x"], "best_objective": v["details"].get("primal_obj")}
        write_text(os.path.join(run_dir, "problem.json"), stable_json(spec))
        write_text(os.path.join(run_dir, "result.json"), stable_json(result))
        write_text(os.path.join(run_dir, "certificate.json"), stable_json(v))
        write_manifest(run_dir)
        write_text(os.path.join(run_dir, "log.txt"), "UPME-Verify CE runpack\n")
        print(f"[UPME-Verify CE] Runpack: {run_dir}")
        return

    raise SystemExit("Unknown problem type (use type=milp or type=lp).")

def cmd_verify(args):
    cert = _load_json(args.certificate_file)
    run_dir = new_run_dir()
    v = verify_certificate(cert, tol=args.tol)
    write_text(os.path.join(run_dir, "problem.json"), stable_json({"certificate_file": os.path.basename(args.certificate_file)}))
    write_text(os.path.join(run_dir, "result.json"), stable_json({"mode": "VERIFIED" if v["verified"] else "FAILED", "verification": v}))
    write_text(os.path.join(run_dir, "certificate.json"), stable_json(v))
    write_manifest(run_dir)
    write_text(os.path.join(run_dir, "log.txt"), "UPME-Verify CE verification runpack\n")
    print(f"[UPME-Verify CE] Verification runpack: {run_dir}")

def build_parser():
    p = argparse.ArgumentParser(prog="upme", description="UPME-Verify Community Edition")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("solve", help="solve demo-sized LP/MILP problems")
    s.add_argument("problem_json", type=str)
    s.add_argument("--node_limit", type=int, default=50000)
    s.add_argument("--tol", type=float, default=1e-8)
    s.set_defaults(func=cmd_solve)

    v = sub.add_parser("verify", help="verify certificate bundles")
    v.add_argument("certificate_file", type=str)
    v.add_argument("--tol", type=float, default=1e-8)
    v.set_defaults(func=cmd_verify)
    return p

def main():
    p = build_parser()
    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
