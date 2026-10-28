"""Security audit, input validation, and SQL injection resilience tests."""

import os
import tempfile
import unittest
from fastapi.testclient import TestClient

from chakravyuh.main import create_app
from chakravyuh.storage.database import ChakravyuhDatabase
from chakravyuh.voice.vachana_vc import BFloat16Tensor


class TestSecurityAndEdgeCases(unittest.TestCase):
    """Verify input validation, SQLi prevention, and tensor boundary invariants."""

    def setUp(self) -> None:
        self.tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp_db.close()
        self.app = create_app(db_path=self.tmp_db.name)
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        if os.path.exists(self.tmp_db.name):
            os.unlink(self.tmp_db.name)

    def test_sql_injection_resilience_in_session_and_turn_inputs(self) -> None:
        """Verify parameterized SQLite queries safely handle SQL injection payloads."""
        sqli_caller = "+91-9820471829'; DROP TABLE call_sessions; --"
        res = self.client.post(
            "/api/v1/sessions",
            json={
                "caller_number": sqli_caller,
                "victim_alias": "Test'); DELETE FROM extracted_iocs; --",
            },
        )
        self.assertEqual(res.status_code, 200)
        session_id = res.json()["session_id"]

        turn_res = self.client.post(
            f"/api/v1/sessions/{session_id}/turn",
            json={
                "scammer_text": "Send money to hacker@ybl'; DROP TABLE i4c_dossiers; --",
            },
        )
        self.assertEqual(turn_res.status_code, 200)

        # Verify tables remain intact and session is retrievable
        check_res = self.client.get(f"/api/v1/sessions/{session_id}")
        self.assertEqual(check_res.status_code, 200)
        self.assertEqual(check_res.json()["caller_number"], sqli_caller)

    def test_reject_empty_or_oversized_turn_payloads(self) -> None:
        """Empty whitespace or >4096 char scammer_text must be rejected with HTTP 422."""
        res = self.client.post("/api/v1/sessions", json={})
        session_id = res.json()["session_id"]

        empty_res = self.client.post(
            f"/api/v1/sessions/{session_id}/turn",
            json={"scammer_text": "   "},
        )
        self.assertEqual(empty_res.status_code, 422)

        huge_res = self.client.post(
            f"/api/v1/sessions/{session_id}/turn",
            json={"scammer_text": "A" * 5000},
        )
        self.assertEqual(huge_res.status_code, 422)

    def test_invalid_tensor_shape_raises_value_error(self) -> None:
        """BFloat16Tensor must reject any shape other than (1, 768)."""
        with self.assertRaises(ValueError):
            BFloat16Tensor([1.0, 2.0, 3.0])

    def test_cors_origin_restriction_and_allowlist(self) -> None:
        """Configured origins must be allowed; wildcard must not be emitted when origin filtering is active."""
        app = create_app(
            db_path=self.tmp_db.name,
            allowed_origins=["http://trusted-command-center.gov.in"],
        )
        client = TestClient(app)

        # Trusted origin gets matching allow-origin
        res_trusted = client.get(
            "/api/v1/health",
            headers={"Origin": "http://trusted-command-center.gov.in"},
        )
        self.assertEqual(res_trusted.status_code, 200)
        self.assertEqual(
            res_trusted.headers.get("access-control-allow-origin"),
            "http://trusted-command-center.gov.in",
        )

        # Untrusted origin does not get allow-origin
        res_untrusted = client.get(
            "/api/v1/health",
            headers={"Origin": "http://malicious-attacker.com"},
        )
        self.assertNotEqual(
            res_untrusted.headers.get("access-control-allow-origin"),
            "http://malicious-attacker.com",
        )
        self.assertNotEqual(
            res_untrusted.headers.get("access-control-allow-origin"),
            "*",
        )

    def test_api_key_authentication_enforcement(self) -> None:
        """Protected routes must reject requests missing or using invalid X-API-Key when auth is configured."""
        app = create_app(db_path=self.tmp_db.name, api_key="secret-tactical-token-7788")
        client = TestClient(app)

        # Public health route remains accessible
        res_health = client.get("/api/v1/health")
        self.assertEqual(res_health.status_code, 200)

        # Protected route without key returns 401
        res_unauth = client.post(
            "/api/v1/sessions",
            json={"caller_number": "+91-9820471829"},
        )
        self.assertEqual(res_unauth.status_code, 401)

        # Protected route with wrong key returns 401
        res_wrong = client.post(
            "/api/v1/sessions",
            json={"caller_number": "+91-9820471829"},
            headers={"X-API-Key": "wrong-token"},
        )
        self.assertEqual(res_wrong.status_code, 401)

        # Protected route with valid key succeeds
        res_auth = client.post(
            "/api/v1/sessions",
            json={"caller_number": "+91-9820471829"},
            headers={"X-API-Key": "secret-tactical-token-7788"},
        )
        self.assertEqual(res_auth.status_code, 200)

    def test_request_id_middleware_traceability(self) -> None:
        """Every response must return an X-Request-ID header."""
        res = self.client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.headers.get("X-Request-ID", "").startswith("req-"))

        # Preserves client-supplied X-Request-ID
        res_custom = self.client.get(
            "/api/v1/health",
            headers={"X-Request-ID": "trace-custom-9911"},
        )
        self.assertEqual(res_custom.headers.get("X-Request-ID"), "trace-custom-9911")

    def test_database_persistence_directory_creation_and_backup(self) -> None:
        """Database must auto-create parent directories, check integrity, and create online backups."""
        sub_dir = tempfile.mkdtemp()
        nested_db = os.path.join(sub_dir, "nested_folder", "durable.db")
        db = ChakravyuhDatabase(nested_db)
        self.assertTrue(os.path.exists(os.path.dirname(nested_db)))
        self.assertTrue(db.check_integrity())

        # Test online backup
        backup_path = os.path.join(sub_dir, "backup_folder", "backup_snapshot.db")
        result_path = db.backup_database(backup_path)
        self.assertEqual(result_path, backup_path)
        self.assertTrue(os.path.exists(backup_path))
        backup_db = ChakravyuhDatabase(backup_path)
        self.assertTrue(backup_db.check_integrity())


if __name__ == "__main__":
    unittest.main()
