from client import AutonomousChargebackEvidenceDossierBuilderClient
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

def main():
    builder = AutonomousChargebackEvidenceDossierBuilderClient()
    print("=== AUTONOMOUS CHARGEBACK EVIDENCE DOSSIER BUILDER ===")
    
    txn = {"order_id": "ORD-884920", "amount": 799.00, "currency": "USD", "avs_result": "Y", "cvv_result": "M", "three_d_secure_authenticated": True}
    delivery = {"carrier": "FedEx Priority", "tracking_number": "FX-772918392", "signed_signature": True, "delivered_gps_match": True}
    history = {"completed_orders_count": 5, "prior_dispute_count": 0}
    
    dossier = builder.build_dispute_evidence_dossier("DISP-99214", "10.4", txn, delivery, history)
    print(f"Dispute ID: {dossier['dispute_id']} | Reason: {dossier['reason_code']} ({dossier['reason_name']})")
    print(f"Strength Score: {dossier['defense_strength_score']}/100 | Win Probability: {dossier['predicted_win_probability']*100:.1f}%")
    print(f"Action: {dossier['recommended_action']}")
    print("Evidence Factors:")
    for f in dossier['compelling_evidence_factors']:
        print(f"  - [{f['factor']}] +{f['weight']} pts: {f['detail']}")
    print()
    print("Cover Statement:")
    print(dossier['official_cover_statement'])

if __name__ == "__main__":
    main()
