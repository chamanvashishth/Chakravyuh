"""
I4C (Indian Cyber Crime Coordination Centre) / NCRP 1930 Cybercrime FIR Dossier Compiler.

Automatically compiles extracted mule UPI handles, bank account numbers, IFSC codes,
phishing links, chronological Hinglish transcripts, and vachana-vc-v1 speaker-embedding
cryptographic audit logs into an actionable Law Enforcement & Fintech Threat Dossier.
"""

import hashlib
from typing import Any, Dict, List

from chakravyuh.models.schemas import (
    CallSession,
    ExtractedIOC,
    I4CDossier,
    IOCType,
)


class I4CDossierCompiler:
    """Compiles real-time I4C / Cybercrime FIR Dossiers from active CallSessions."""

    def compile_dossier(self, session: CallSession) -> I4CDossier:
        """Build a complete I4CDossier for the given CallSession."""
        dossier_hash = hashlib.sha256(session.session_id.encode("utf-8")).hexdigest()[:8].upper()
        dossier_id = f"I4C-FIR-2026-{dossier_hash}"

        mule_upis = [i for i in session.extracted_iocs if i.ioc_type == IOCType.UPI_ID]
        mule_banks = [i for i in session.extracted_iocs if i.ioc_type == IOCType.BANK_ACCOUNT]
        ifscs = [i for i in session.extracted_iocs if i.ioc_type == IOCType.IFSC_CODE]
        phones = [i for i in session.extracted_iocs if i.ioc_type == IOCType.PHONE_NUMBER]
        urls = [i for i in session.extracted_iocs if i.ioc_type == IOCType.PHISHING_URL]
        badges = [i for i in session.extracted_iocs if i.ioc_type == IOCType.FAKE_OFFICER_ID]

        # Build prioritized NPCI / I4C enforcement actions
        actions: List[str] = []
        for upi in mule_upis:
            actions.append(
                f"[NPCI / PSP PRIORITY FREEZE] Issue immediate debit freeze & VPA block on "
                f"{upi.role_classification}: '{upi.value}' ({upi.bank_or_provider})"
            )
        for idx, bank in enumerate(mule_banks):
            paired_ifsc = ifscs[idx].value if idx < len(ifscs) else (ifscs[0].value if ifscs else "PENDING_IFSC")
            actions.append(
                f"[CFA / BANK NODAL LIEN] Place Layer-1 Lien & Debit Freeze under Section 106 BNSS "
                f"on Account No. '{bank.value}' (IFSC: {paired_ifsc} | {bank.bank_or_provider})"
            )
        for url in urls:
            actions.append(
                f"[CERT-In / DoT TAKEDOWN] Sinkhole malicious domain/APK payload: '{url.value}'"
            )
        for ph in phones:
            actions.append(
                f"[DoT SANCHAAR SAATHI / CHAKSHU] Block IMEI & MSISDN '{ph.value}' for telecom impersonation"
            )
        if not actions:
            actions.append(
                "[ACTIVE HONEYPOT ENGAGEMENT] Continue Evon v3.3 stall loop until primary and secondary mule instruments are disclosed."
            )

        # Phase 2 SIP / WebRTC Call Merge Signaling Payload
        sip_payload: Dict[str, Any] = {
            "phase": "Phase 2 : SIP/WebRTC Call Forwarding & Merge Bridge",
            "sip_method": "REFER / INVITE (3GPP TS 24.229 IMS Conference Merge)",
            "call_id": f"chakravyuh-sip-{session.session_id}@honeypot.gnani.ai",
            "caller_msisdn": session.caller_number,
            "victim_mute_state": "MUTED_AT_IMS_BRIDGE",
            "rtp_codec": "PCMU/8000/1 (ITU-T G.711 mu-law 8kHz)",
            "voice_decoy_stream": "ws://127.0.0.1:8000/ws/call/" + session.session_id,
            "vachana_embedding_lock": session.speaker_embedding.embedding_sha256[:16],
        }

        # Phase 3 Automated Fintech Threat Intelligence API Payload
        threat_payload: Dict[str, Any] = {
            "schema_version": "I4C-NPCI-STIX-3.0",
            "dossier_id": dossier_id,
            "scam_category": session.scam_category.value,
            "threat_score": session.threat_score,
            "flagged_vpas": [u.value for u in mule_upis],
            "flagged_bank_accounts": [
                {
                    "account_number": b.value,
                    "ifsc": ifscs[idx].value if idx < len(ifscs) else (ifscs[0].value if ifscs else None),
                    "bank": b.bank_or_provider,
                }
                for idx, b in enumerate(mule_banks)
            ],
            "flagged_urls": [u.value for u in urls],
            "flagged_phones": [p.value for p in phones],
            "recommended_engine_rule": "BLOCK_OUTBOUND_P2P_P2M_AND_ALERT_1930",
        }

        report_text = self._format_official_fir_text(
            dossier_id=dossier_id,
            session=session,
            mule_upis=mule_upis,
            mule_banks=mule_banks,
            ifscs=ifscs,
            phones=phones,
            urls=urls,
            badges=badges,
            actions=actions,
        )

        return I4CDossier(
            dossier_id=dossier_id,
            session_id=session.session_id,
            caller_number=session.caller_number,
            scam_category=session.scam_category,
            claimed_authority=session.claimed_authority,
            threat_score=session.threat_score,
            scammer_time_wasted_sec=session.time_wasted_sec,
            current_deception_stage=session.current_stage,
            voice_clone_audit=session.speaker_embedding,
            mule_upi_ids=mule_upis,
            mule_bank_accounts=mule_banks,
            ifsc_codes=ifscs,
            scammer_phones=phones,
            phishing_urls=urls,
            fake_officer_ids=badges,
            chronological_transcript=session.turns,
            recommended_enforcement_actions=actions,
            sip_trunk_forwarding_sdp=sip_payload,
            npci_threat_feed_payload=threat_payload,
            formatted_fir_report_text=report_text,
        )

    def _format_official_fir_text(
        self,
        dossier_id: str,
        session: CallSession,
        mule_upis: List[ExtractedIOC],
        mule_banks: List[ExtractedIOC],
        ifscs: List[ExtractedIOC],
        phones: List[ExtractedIOC],
        urls: List[ExtractedIOC],
        badges: List[ExtractedIOC],
        actions: List[str],
    ) -> str:
        """Render a clean, printable Cybercrime FIR / I4C Evidence Dossier."""
        lines = [
            "================================================================================",
            "      INDIAN CYBER CRIME COORDINATION CENTRE (I4C) / NCRP 1930 FIR DOSSIER      ",
            "           GENERATED BY CHAKRAVYUH ACTIVE VOICE-CLONE HONEYPOT SYSTEM           ",
            "================================================================================",
            f"DOSSIER ID          : {dossier_id}",
            f"SESSION ID          : {session.session_id}",
            f"INCIDENT TIMESTAMP  : {session.updated_at}",
            f"SUSPECT CALLER ID   : {session.caller_number}",
            f"SCAM CLASSIFICATION : {session.scam_category.value} (Threat Score: {session.threat_score}/100)",
            f"CLAIMED AUTHORITY   : {session.claimed_authority}",
            f"DECEPTION STAGE     : {session.current_stage.value}",
            f"SCAMMER TIME WASTED : {session.time_wasted_sec} seconds (Active Honeypot Containment)",
            "--------------------------------------------------------------------------------",
            "1. CRYPTOGRAPHIC VOICE-CLONE DECOY AUDIT (EVIDENTIARY INTEGRITY)",
            f"   - Synthesis Model     : {session.speaker_embedding.model_name}",
            f"   - Embedding Tensor    : Shape {session.speaker_embedding.shape} | Dtype {session.speaker_embedding.dtype}",
            f"   - Reference Window    : {session.speaker_embedding.reference_duration_sec}s User Consent Clip ({session.speaker_embedding.raw_byte_size} bytes)",
            f"   - Tensor SHA-256      : {session.speaker_embedding.embedding_sha256}",
            f"   - bfloat16 Hex Slice  : {', '.join(session.speaker_embedding.bfloat16_hex_preview[:6])}",
            "--------------------------------------------------------------------------------",
            "2. EXTRACTED MULE FINANCIAL INSTRUMENTS & INFRASTRUCTURE (IOCs)",
        ]

        if mule_upis:
            lines.append("   [A] EXTRACTED MULE UPI HANDLES (VPAs):")
            for u in mule_upis:
                lines.append(
                    f"       * {u.value} | {u.role_classification} | {u.bank_or_provider} (Conf: {int(u.confidence*100)}%)"
                )
        else:
            lines.append("   [A] EXTRACTED MULE UPI HANDLES (VPAs): None captured yet")

        if mule_banks or ifscs:
            lines.append("   [B] EXTRACTED MULE BANK ACCOUNTS & IFSC CODES:")
            for b in mule_banks:
                lines.append(
                    f"       * Account No: {b.value} | {b.role_classification} | {b.bank_or_provider}"
                )
            for f in ifscs:
                lines.append(f"       * IFSC Code : {f.value} | {f.bank_or_provider}")
        else:
            lines.append("   [B] EXTRACTED MULE BANK ACCOUNTS & IFSC CODES: None captured yet")

        if phones or urls or badges:
            lines.append("   [C] COMMAND PHONES, PHISHING URLs & IMPERSONATION ARTIFACTS:")
            for p in phones:
                lines.append(f"       * C2 Phone/WhatsApp : {p.value}")
            for u in urls:
                lines.append(f"       * Phishing/APK Link : {u.value} ({u.bank_or_provider})")
            for bd in badges:
                lines.append(f"       * Fake Warrant/ID   : {bd.value}")

        lines.append("--------------------------------------------------------------------------------")
        lines.append("3. RECOMMENDED IMMEDIATE ENFORCEMENT & NPCI FREEZE ACTIONS")
        for idx, act in enumerate(actions, start=1):
            lines.append(f"   {idx}. {act}")

        lines.append("--------------------------------------------------------------------------------")
        lines.append("4. CHRONOLOGICAL DUPLEX INTERCEPT TRANSCRIPT (PRISMA v2.5 + EVON v3.3)")
        for t in session.turns:
            tag = "[SCAMMER 8kHz PSTN]" if t.speaker == "SCAMMER" else "[CHAKRAVYUH VOICE DECOY]"
            lines.append(f"   Turn #{t.turn_id:02d} {tag} ({t.deception_stage.value}):")
            lines.append(f"      \"{t.text}\"")
        lines.append("================================================================================")
        return "\n".join(lines)
