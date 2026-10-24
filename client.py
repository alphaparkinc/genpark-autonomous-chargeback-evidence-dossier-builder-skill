import sys
sys.stdout.reconfigure(encoding='utf-8')

class AutonomousChargebackEvidenceDossierBuilderClient:
    """
    FinTech dispute defense builder. Assesses evidentiary criteria (AVS, CVV, Proof of Delivery,
    IP geolocation, customer purchase history) to compute a win-probability score and format
    a comprehensive dispute response dossier for payment gateways.
    """
    def __init__(self):
        self.reason_codes = {
            "10.4": {"name": "Fraud - Card Absent Environment", "network": "Visa", "focus": ["avs", "cvv", "ip_match", "device_fingerprint"]},
            "13.1": {"name": "Merchandise / Services Not Received", "network": "Visa", "focus": ["pod", "tracking_number", "delivery_signature"]},
            "4837": {"name": "No Cardholder Authorization", "network": "Mastercard", "focus": ["avs", "cvv", "3ds_auth"]},
            "4853": {"name": "Defective / Not as Described", "network": "Mastercard", "focus": ["terms_of_service", "refund_policy", "comms_log"]}
        }

    def evaluate_evidence(self, reason_code, transaction_meta, delivery_meta, history_meta):
        score = 0
        factors = []

        # AVS Check (Address Verification Service)
        avs = transaction_meta.get("avs_result", "").upper()
        if avs in ("Y", "M", "D"):
            score += 25
            factors.append({"factor": "AVS_FULL_MATCH", "weight": 25, "detail": f"Exact street and postal code match ({avs})"})
        elif avs in ("A", "Z", "W"):
            score += 15
            factors.append({"factor": "AVS_PARTIAL_MATCH", "weight": 15, "detail": f"Partial address match ({avs})"})

        # CVV Check
        cvv = transaction_meta.get("cvv_result", "").upper()
        if cvv == "M":
            score += 20
            factors.append({"factor": "CVV2_MATCH", "weight": 20, "detail": "Card security code verified successfully"})

        # 3D Secure Authentication
        if transaction_meta.get("three_d_secure_authenticated", False):
            score += 25
            factors.append({"factor": "3D_SECURE_LIABILITY_SHIFT", "weight": 25, "detail": "Full 3DS v2.2 frictionless liability shift achieved"})

        # Proof of Delivery (POD)
        if delivery_meta.get("signed_signature", False):
            score += 30
            factors.append({"factor": "PROOF_OF_DELIVERY_SIGNED", "weight": 30, "detail": f"Carrier signature captured by {delivery_meta.get('carrier')}"})
        elif delivery_meta.get("delivered_gps_match", False):
            score += 20
            factors.append({"factor": "DELIVERY_GPS_CONFIRMED", "weight": 20, "detail": "Carrier GPS coordinates match customer shipping address"})

        # Customer Historical Goodwill
        prior_orders = history_meta.get("completed_orders_count", 0)
        prior_chargebacks = history_meta.get("prior_dispute_count", 0)
        if prior_orders >= 3 and prior_chargebacks == 0:
            score += 15
            factors.append({"factor": "LOYAL_CUSTOMER_RECORD", "weight": 15, "detail": f"Zero prior disputes across {prior_orders} historical orders"})

        # Cap score at 100
        final_score = min(100, score)

        # Win probability calculation
        if final_score >= 85:
            win_prob = 0.88
            rec_action = "SUBMIT_AGGRESSIVE_CONTEST"
        elif final_score >= 65:
            win_prob = 0.68
            rec_action = "SUBMIT_STANDARD_EVIDENCE"
        elif final_score >= 45:
            win_prob = 0.42
            rec_action = "MANUAL_REPRESENTMENT_REVIEW"
        else:
            win_prob = 0.18
            rec_action = "ACCEPT_DISPUTE_LOSS"

        return final_score, win_prob, rec_action, factors

    def build_dispute_evidence_dossier(self, dispute_id, reason_code, transaction_meta, delivery_meta, history_meta):
        score, win_prob, rec_action, factors = self.evaluate_evidence(reason_code, transaction_meta, delivery_meta, history_meta)
        reason_info = self.reason_codes.get(reason_code, {"name": "Unspecified Dispute", "network": "Unknown"})

        cover_statement = " | ".join([
            f"REPRESENTMENT BRIEF FOR DISPUTE {dispute_id}",
            f"Network: {reason_info['network']} - Reason Code: {reason_code} ({reason_info['name']})",
            f"Fulfillment confirmed for Order #{transaction_meta.get('order_id')}",
            f"Amount: ${transaction_meta.get('amount', 0.0):,.2f} {transaction_meta.get('currency', 'USD')}",
            f"Defense Score: {score}/100 (Est. Win Probability: {win_prob*100:.1f}%)"
        ])

        return {
            "status": "success",
            "dispute_id": dispute_id,
            "reason_code": reason_code,
            "reason_name": reason_info["name"],
            "card_network": reason_info["network"],
            "disputed_amount": transaction_meta.get("amount", 0.0),
            "defense_strength_score": score,
            "predicted_win_probability": win_prob,
            "recommended_action": rec_action,
            "compelling_evidence_factors": factors,
            "official_cover_statement": cover_statement
        }
