import sys, json
from client import AutonomousChargebackEvidenceDossierBuilderClient
sys.stdout.reconfigure(encoding='utf-8')

def handle_mcp():
    builder = AutonomousChargebackEvidenceDossierBuilderClient()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps({"status": "ready", "skill": "genpark-autonomous-chargeback-evidence-dossier-builder-skill"}))
        return
    req = json.loads(sys.stdin.read() or "{}")
    did = req.get("dispute_id", "DISP_001")
    rc = req.get("reason_code", "10.4")
    txn = req.get("transaction", {})
    delv = req.get("delivery", {})
    hist = req.get("history", {})
    res = builder.build_dispute_evidence_dossier(did, rc, txn, delv, hist)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    handle_mcp()
