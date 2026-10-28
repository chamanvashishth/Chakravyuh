"""Tests for Phase 2 SIP/WebRTC G.711 mu-law Bridge and Phase 3 NPCI Fraud Engine API."""

import os
import tempfile
import unittest
import numpy as np
from fastapi.testclient import TestClient

from chakravyuh.main import create_app
from chakravyuh.telecom.sip_webrtc_bridge import SIPWebRTCBridgeService


class TestPhase2AndPhase3Services(unittest.TestCase):
    """Verify ITU-T G.711 mu-law codec, SIP REFER call merge, and NPCI pre-transaction screening."""

    def setUp(self) -> None:
        self.tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_db.close()
        self.app = create_app(db_path=self.tmp_db.name)
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        if os.path.exists(self.tmp_db.name):
            os.unlink(self.tmp_db.name)

    def test_g711_ulaw_codec_roundtrip_fidelity(self) -> None:
        """G.711 mu-law encode/decode on 8 kHz audio must preserve >0.99 waveform correlation."""
        t = np.linspace(0, 0.25, 2000, endpoint=False, dtype=np.float32)
        sine_pcm16 = (np.sin(2.0 * np.pi * 440.0 * t) * 24000.0).astype(np.int16)

        ulaw_encoded = SIPWebRTCBridgeService.encode_pcm16_to_ulaw(sine_pcm16)
        self.assertEqual(ulaw_encoded.dtype, np.uint8)
        self.assertEqual(ulaw_encoded.shape, sine_pcm16.shape)

        pcm16_decoded = SIPWebRTCBridgeService.decode_ulaw_to_pcm16(ulaw_encoded)
        self.assertEqual(pcm16_decoded.dtype, np.int16)

        corr = float(np.corrcoef(sine_pcm16.astype(np.float32), pcm16_decoded.astype(np.float32))[0, 1])
        self.assertGreater(corr, 0.995)

    def test_phase2_sip_merge_endpoint(self) -> None:
        """POST /api/v1/sessions/{id}/sip-merge must return RFC 3515 SIP REFER & SDP with G.711 PCMU/8000."""
        create_res = self.client.post(
            "/api/v1/sessions",
            json={"caller_number": "+91-9820471829", "initial_scam_hint": "DIGITAL_ARREST"},
        )
        session_id = create_res.json()["session_id"]

        sip_res = self.client.post(
            f"/api/v1/sessions/{session_id}/sip-merge",
            json={"victim_msisdn": "+91-9811223344"},
        )
        self.assertEqual(sip_res.status_code, 200)
        data = sip_res.json()
        self.assertEqual(data["status"], "SIP_IMS_CONFERENCE_MERGED")
        self.assertIn("PCMU/8000/1", data["sdp_offer"])
        self.assertIn("REFER sip:+91-9820471829", data["sip_refer_frame"])

    def test_phase3_npci_transaction_screening_and_stix_broadcast(self) -> None:
        """Extracted mule UPIs/Bank accounts must trigger BLOCK_TRANSACTION on pre-transaction checks."""
        create_res = self.client.post(
            "/api/v1/sessions",
            json={"caller_number": "+91-9820471829", "initial_scam_hint": "DIGITAL_ARREST"},
        )
        session_id = create_res.json()["session_id"]

        # Simulate Digital Arrest scenario to populate mule UPIs & Bank accounts
        self.client.post(f"/api/v1/sessions/{session_id}/simulate?scenario=DIGITAL_ARREST")

        # 1. Check flagged primary mule UPI
        blocked_upi = self.client.post(
            "/api/v1/threat-feed/check-transaction",
            json={"recipient_vpa": "rbi.verification.cell@okaxis", "amount_inr": 95000.0},
        )
        self.assertEqual(blocked_upi.status_code, 200)
        self.assertEqual(blocked_upi.json()["decision"], "BLOCK_TRANSACTION")
        self.assertGreater(blocked_upi.json()["risk_score"], 95.0)

        # 2. Check flagged backup mule UPI
        blocked_backup = self.client.post(
            "/api/v1/threat-feed/check-transaction",
            json={"recipient_vpa": "mumbaicrime.deposit99@ybl", "amount_inr": 95000.0},
        )
        self.assertEqual(blocked_backup.json()["decision"], "BLOCK_TRANSACTION")

        # 3. Check clean merchant UPI
        clean_res = self.client.post(
            "/api/v1/threat-feed/check-transaction",
            json={"recipient_vpa": "irctc.official@sbi", "amount_inr": 1250.0},
        )
        self.assertEqual(clean_res.status_code, 200)
        self.assertEqual(clean_res.json()["decision"], "ALLOW_TRANSACTION")

        # 4. Verify HMAC-SHA256 STIX-3.0 Webhook Broadcast and Signature Verification
        bcast_res = self.client.post(f"/api/v1/threat-feed/broadcast/{session_id}")
        self.assertEqual(bcast_res.status_code, 200)
        bcast_data = bcast_res.json()
        self.assertEqual(bcast_data["broadcast_status"], "DISPATCHED_TO_FINTECH_FRAUD_ENGINES")
        self.assertTrue(bcast_data["hmac_sha256_signature"].startswith("sha256="))
        self.assertGreaterEqual(bcast_data["indicator_count"], 4)

        fraud_engine = self.app.state.orchestrator.fraud_engine
        self.assertTrue(
            fraud_engine.verify_broadcast_signature(
                bcast_data["stix_bundle"],
                bcast_data["hmac_sha256_signature"],
            )
        )

        # Tampered bundle must fail signature check
        tampered_bundle = dict(bcast_data["stix_bundle"])
        tampered_bundle["threat_score"] = 0.0
        self.assertFalse(
            fraud_engine.verify_broadcast_signature(
                tampered_bundle,
                bcast_data["hmac_sha256_signature"],
            )
        )


if __name__ == "__main__":
    unittest.main()
