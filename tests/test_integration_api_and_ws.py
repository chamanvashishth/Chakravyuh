"""Integration tests for FastAPI REST endpoints, WebSocket streaming, and SQLite persistence."""

import os
import tempfile
import unittest
from fastapi.testclient import TestClient

from chakravyuh.main import create_app


class TestFastAPIAndWebSocketIntegration(unittest.TestCase):
    """End-to-end verification of REST and WebSocket call handover workflows."""

    def setUp(self) -> None:
        self.tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_db.close()
        self.app = create_app(db_path=self.tmp_db.name)
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        if os.path.exists(self.tmp_db.name):
            os.unlink(self.tmp_db.name)

    def test_health_and_scenarios_endpoints(self) -> None:
        """Verify /api/v1/health reports [1, 768] torch.bfloat16 and 8000 Hz specs."""
        res = self.client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "OPERATIONAL")
        self.assertEqual(data["models"]["voice_clone"]["tensor_shape"], [1, 768])
        self.assertEqual(data["models"]["voice_clone"]["dtype"], "torch.bfloat16")
        self.assertEqual(data["models"]["telephonic_asr"]["sample_rate_hz"], 8000)

        scen_res = self.client.get("/api/v1/scenarios")
        self.assertEqual(scen_res.status_code, 200)
        self.assertIn("DIGITAL_ARREST", scen_res.json()["scenarios"])

    def test_full_call_handover_simulation_and_i4c_dossier_generation(self) -> None:
        """Verify session creation, scenario execution, dossier compilation, and threat feed."""
        create_res = self.client.post(
            "/api/v1/sessions",
            json={
                "caller_number": "+91-9820471829",
                "victim_alias": "Rohan Verma (Voice Decoy)",
                "initial_scam_hint": "DIGITAL_ARREST",
                "speaker_profile_seed": 77,
            },
        )
        self.assertEqual(create_res.status_code, 200)
        session = create_res.json()
        session_id = session["session_id"]
        self.assertEqual(session["speaker_embedding"]["shape"], [1, 768])
        self.assertEqual(session["speaker_embedding"]["dtype"], "torch.bfloat16")

        # Simulate full Digital Arrest scenario
        sim_res = self.client.post(
            f"/api/v1/sessions/{session_id}/simulate?scenario=DIGITAL_ARREST"
        )
        self.assertEqual(sim_res.status_code, 200)
        turns_out = sim_res.json()
        self.assertEqual(len(turns_out), 4)

        # Fetch compiled I4C Dossier
        dos_res = self.client.get(f"/api/v1/sessions/{session_id}/dossier")
        self.assertEqual(dos_res.status_code, 200)
        dossier = dos_res.json()
        self.assertEqual(len(dossier["mule_upi_ids"]), 2)
        self.assertEqual(len(dossier["mule_bank_accounts"]), 1)
        self.assertEqual(len(dossier["ifsc_codes"]), 1)
        self.assertIn("I4C-FIR-2026-", dossier["dossier_id"])
        self.assertIn("rbi.verification.cell@okaxis", dossier["formatted_fir_report_text"])
        self.assertIn("mumbaicrime.deposit99@ybl", dossier["formatted_fir_report_text"])

        # Verify Phase-3 Live Threat Feed populated
        feed_res = self.client.get("/api/v1/threat-feed")
        self.assertEqual(feed_res.status_code, 200)
        feed_items = feed_res.json()
        self.assertGreaterEqual(len(feed_items), 4)

    def test_websocket_duplex_streaming(self) -> None:
        """Verify real-time full-duplex WebSocket stream (/ws/call/{session_id})."""
        create_res = self.client.post(
            "/api/v1/sessions",
            json={
                "caller_number": "+91-9167283910",
                "victim_alias": "Priya Nair (Decoy)",
                "initial_scam_hint": "FEDEX_PARCEL",
            },
        )
        session_id = create_res.json()["session_id"]

        with self.client.websocket_connect(f"/ws/call/{session_id}") as ws:
            handshake = ws.receive_json()
            self.assertEqual(handshake["event"], "handover_established")
            self.assertEqual(handshake["speaker_embedding"]["shape"], [1, 768])

            ws.send_json(
                {
                    "type": "scammer_turn",
                    "scammer_text": (
                        "FedEx parcel seized! Pay ₹88,500 to fedex.customs.bond@oksbi "
                        "or Account 389201746512 IFSC SBIN0004821 immediately!"
                    ),
                    "input_sample_rate_hz": 8000,
                }
            )
            turn_msg = ws.receive_json()
            self.assertEqual(turn_msg["event"], "honeypot_turn_result")
            data = turn_msg["data"]
            self.assertGreaterEqual(len(data["newly_extracted_iocs"]), 3)
            self.assertEqual(
                data["honeypot_turn"]["voice_synthesis"]["sample_rate_hz"], 8000
            )


if __name__ == "__main__":
    unittest.main()
