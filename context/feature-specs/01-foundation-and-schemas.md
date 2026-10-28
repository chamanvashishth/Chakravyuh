# Feature Spec 01  -  Project Foundation, Config, and Core Schemas

## 1. Objective
Establish the foundational Python package structure (`src/chakravyuh/`), centralized configuration (`config.py`), and strict Pydantic data contracts (`models/schemas.py`) governing sessions, speaker embeddings, 8 kHz audio frames, deception states, extracted IOCs, and I4C FIR dossiers.

## 2. Context & Dependencies
- Depends on: `pydantic` (v1.10+), `enum`, `typing`, `datetime`.
- Consumed by: All downstream modules (`voice`, `asr`, `deception`, `intelligence`, `dossier`, `storage`, `api`).

## 3. Exact Implementation Scope
- `src/chakravyuh/__init__.py`
- `src/chakravyuh/config.py`
- `src/chakravyuh/models/__init__.py`
- `src/chakravyuh/models/schemas.py`

## 4. Required Behavior & Data Contracts
- **Enums**:
  - `ScamCategory`: `DIGITAL_ARREST`, `FEDEX_PARCEL`, `KYC_BANK_FRAUD`, `UTILITY_DISCONNECT`, `UNKNOWN`
  - `DeceptionStage`: `STAGE_1_INITIAL_PANIC`, `STAGE_2_COMPLIANCE_HOOK`, `STAGE_3_PRIMARY_UPI_STALL`, `STAGE_4_SECONDARY_MULE_BAIT`, `STAGE_5_PHISHING_AND_SUPERVISOR_BAIT`, `STAGE_6_INFINITE_HOLD_LOOP`
  - `IOCType`: `UPI_ID`, `BANK_ACCOUNT`, `IFSC_CODE`, `PHONE_NUMBER`, `PHISHING_URL`, `FAKE_OFFICER_ID`
  - `CallStatus`: `RINGING`, `HANDOVER_INITIATED`, `ACTIVE_ENGAGEMENT`, `DOSSIER_FINALIZED`, `TERMINATED`
- **Models**:
  - `SpeakerEmbeddingMetadata`: `model_name="vachana-vc-v1"`, `shape=[1, 768]`, `dtype="torch.bfloat16"`, `reference_duration_sec=10.0`, `l2_norm`, `bfloat16_hex_preview`, `embedding_sha256`.
  - `ExtractedIOC`: `ioc_id`, `ioc_type`, `value`, `confidence`, `bank_or_provider`, `context_snippet`, `first_seen_turn`, `flagged_for_npci_freeze`.
  - `TranscriptTurn`: `turn_id`, `session_id`, `speaker` (`SCAMMER` | `HONEYPOT_DECOY`), `text`, `timestamp`, `deception_stage`, `audio_metrics`, `extracted_iocs`.
  - `I4CDossier`: Official National Cyber Crime Reporting Portal (1930) / I4C schema including `dossier_id`, `session_id`, `incident_timestamp`, `scam_category`, `threat_score`, `caller_number`, `claimed_authority`, `voice_clone_audit`, `mule_upi_ids`, `mule_bank_accounts`, `ifsc_codes`, `phishing_urls`, `scammer_phones`, `chronological_transcript`, `recommended_enforcement_actions`.

## 5. Edge Cases & Security Considerations
- Reject empty or oversized scammer inputs (`> 4096` chars per single turn) to prevent memory exhaustion.
- Ensure timestamps are UTC ISO-8601 strings.

## 6. Acceptance Criteria & Definition of Done
- All schemas instantiate, validate, and serialize cleanly via `.dict()` and `.json()`.
- Unit tests verify invalid enum values and schema constraints raise `ValidationError`.
