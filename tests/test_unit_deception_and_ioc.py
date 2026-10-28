"""Unit tests for IOCExtractor and Evon v3.3 Tactical Deception State Machine."""

import unittest

from chakravyuh.deception.evon_agent import EvonDeceptionEngine, SCAM_SCENARIOS
from chakravyuh.intelligence.ioc_extractor import IOCExtractor
from chakravyuh.models.schemas import DeceptionStage, IOCType, ScamCategory


class TestIOCExtractorAndEvonDeception(unittest.TestCase):
    """Verify multi-modal IOC extraction and Evon v3.3 tactical stall escalation."""

    def setUp(self) -> None:
        self.extractor = IOCExtractor()
        self.evon = EvonDeceptionEngine()

    def test_extract_upi_handles_and_ignore_standard_emails(self) -> None:
        """UPI handles must be captured and resolved while ignoring standard email domains."""
        text = (
            "Email us at complaint@gmail.com or officer@gov.in, lekin paisa abhi "
            "rbi.verification.cell@okaxis aur backup handle mumbaicrime.deposit99@ybl pe bhejo!"
        )
        iocs = self.extractor.extract_from_text(text, turn_id=1)
        upi_values = [i.value for i in iocs if i.ioc_type == IOCType.UPI_ID]
        self.assertEqual(
            upi_values,
            ["rbi.verification.cell@okaxis", "mumbaicrime.deposit99@ybl"],
        )
        roles = [i.role_classification for i in iocs if i.ioc_type == IOCType.UPI_ID]
        self.assertIn("PRIMARY_MULE_UPI_HANDLE", roles)
        self.assertIn("SECONDARY_BACKUP_MULE_UPI_HANDLE", roles)

    def test_extract_bank_account_ifsc_phone_url_and_badge(self) -> None:
        """Verify extraction of bank accounts, IFSC codes, phones, URLs, and warrant badges."""
        text = (
            "Warrant CBI-8841 ke liye IMPS karo Account Number 50100482917364 aur "
            "IFSC Code HDFC0001842 pe. Receipt WhatsApp +91-9820471829 ya "
            "https://cbi-rbi-verify-court.in/clearance.apk pe bhejo!"
        )
        iocs = self.extractor.extract_from_text(text, turn_id=3)
        by_type = {i.ioc_type: i.value for i in iocs}

        self.assertEqual(by_type.get(IOCType.BANK_ACCOUNT), "50100482917364")
        self.assertEqual(by_type.get(IOCType.IFSC_CODE), "HDFC0001842")
        self.assertEqual(by_type.get(IOCType.PHONE_NUMBER), "+91-9820471829")
        self.assertEqual(
            by_type.get(IOCType.PHISHING_URL),
            "https://cbi-rbi-verify-court.in/clearance.apk",
        )
        self.assertEqual(by_type.get(IOCType.FAKE_OFFICER_ID), "CBI-8841")

    def test_evon_state_machine_progression_across_scenario(self) -> None:
        """Verify Evon v3.3 escalates from Initial Panic -> Primary UPI Stall -> Secondary Mule Bait -> Hold Loop."""
        all_iocs = []
        stage = DeceptionStage.STAGE_1_INITIAL_PANIC
        steps = SCAM_SCENARIOS[ScamCategory.DIGITAL_ARREST]

        visited_stages = []
        for idx, step in enumerate(steps, start=1):
            new_iocs = self.extractor.extract_from_text(
                step["scammer_text"], turn_id=idx, existing_iocs=all_iocs
            )
            all_iocs.extend(new_iocs)
            stage, stall_reason, reply = self.evon.generate_deception_turn(
                scammer_text=step["scammer_text"],
                scam_category=ScamCategory.DIGITAL_ARREST,
                current_stage=stage,
                all_session_iocs=all_iocs,
                new_turn_iocs=new_iocs,
            )
            visited_stages.append(stage)
            self.assertTrue(len(reply) > 30)
            self.assertTrue(len(stall_reason) > 5)

        self.assertEqual(
            visited_stages,
            [
                DeceptionStage.STAGE_2_COMPLIANCE_HOOK,
                DeceptionStage.STAGE_3_PRIMARY_UPI_STALL,
                DeceptionStage.STAGE_4_SECONDARY_MULE_BAIT,
                DeceptionStage.STAGE_6_INFINITE_HOLD_LOOP,
            ],
        )


if __name__ == "__main__":
    unittest.main()
