from .certs.lp_cert import verify_lp_certificate
from .certs.vipr_bundle import verify_vipr_bundle
from .certs.pb_bundle import verify_pb_bundle

def verify_certificate(cert: dict, tol: float = 1e-8) -> dict:
    ctype = cert.get("type")
    if ctype == "lp_primal_dual":
        return verify_lp_certificate(cert, tol=tol)
    if ctype == "vipr_bundle":
        return verify_vipr_bundle(cert)
    if ctype == "pb_bundle":
        return verify_pb_bundle(cert)
    return {"verified": False, "type": ctype, "status":"UNKNOWN_CERT_TYPE", "details":{}}
