def _dot(a, b):
    return float(sum(float(x)*float(y) for x, y in zip(a, b)))

def _mat_vec(A, x):
    return [float(sum(float(Ai[j])*float(x[j]) for j in range(len(x)))) for Ai in A]

def _transpose_mat_vec(A, y):
    n = len(A[0]) if A else 0
    out = [0.0]*n
    for i, row in enumerate(A):
        yi = float(y[i])
        for j in range(n):
            out[j] += float(row[j])*yi
    return out

def verify_lp_certificate(cert: dict, tol: float = 1e-8) -> dict:
    lp = cert.get("lp", {})
    A = lp.get("A", [])
    b = lp.get("b", [])
    c = lp.get("c", [])
    x = cert.get("primal_x", [])
    y = cert.get("dual_y", [])

    m = len(A)
    n = len(A[0]) if m > 0 else 0
    if len(b)!=m or len(c)!=n or len(x)!=n or len(y)!=m:
        return {"verified": False, "type":"lp_primal_dual", "status":"DIMENSION_MISMATCH", "details":{}}

    x_min = min(float(v) for v in x) if x else 0.0
    Ax = _mat_vec(A, x)
    primal_viol = max(float(Ax[i]) - float(b[i]) for i in range(m)) if m else 0.0
    primal_feasible = (x_min >= -tol) and (primal_viol <= tol)

    y_min = min(float(v) for v in y) if y else 0.0
    ATy = _transpose_mat_vec(A, y)
    dual_viol = max(float(c[j]) - float(ATy[j]) for j in range(n)) if n else 0.0
    dual_feasible = (y_min >= -tol) and (dual_viol <= tol)

    p_obj = _dot(c, x)
    d_obj = _dot(b, y)
    gap = p_obj - d_obj
    ok_gap = (gap >= -1e-6) and (gap <= tol*10)

    verified = primal_feasible and dual_feasible and ok_gap
    return {
        "verified": bool(verified),
        "type":"lp_primal_dual",
        "status": "CERTIFIED_OPTIMAL" if verified else "NOT_CERTIFIED",
        "details": {
            "primal_feasible": primal_feasible,
            "dual_feasible": dual_feasible,
            "duality_gap": gap,
            "primal_obj": p_obj,
            "dual_obj": d_obj,
            "tolerance": tol
        }
    }
