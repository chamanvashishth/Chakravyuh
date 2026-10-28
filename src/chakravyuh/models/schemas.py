"""Pydantic data contracts for Chakravyuh subsystems."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


class ScamCategory(str, Enum):
    """Classification taxonomy for Indian telephonic fraud calls."""

    DIGITAL_ARREST = "DIGITAL_ARREST"
    FEDEX_PARCEL = "FEDEX_PARCEL"
    KYC_BANK_FRAUD = "KYC_BANK_FRAUD"
    UTILITY_DISCONNECT = "UTILITY_DISCONNECT"
    UNKNOWN = "UNKNOWN"


class DeceptionStage(str, Enum):
    """Tactical states for the Evon v3.3 Hinglish deception state machine."""

    STAGE_1_INITIAL_PANIC = "STAGE_1_INITIAL_PANIC"
    STAGE_2_COMPLIANCE_HOOK = "STAGE_2_COMPLIANCE_HOOK"
    STAGE_3_PRIMARY_UPI_STALL = "STAGE_3_PRIMARY_UPI_STALL"
    STAGE_4_SECONDARY_MULE_BAIT = "STAGE_4_SECONDARY_MULE_BAIT"
    STAGE_5_PHISHING_AND_SUPERVISOR_BAIT = "STAGE_5_PHISHING_AND_SUPERVISOR_BAIT"
    STAGE_6_INFINITE_HOLD_LOOP = "STAGE_6_INFINITE_HOLD_LOOP"


class IOCType(str, Enum):
    """Types of financial and infrastructure Indicators of Compromise."""

    UPI_ID = "UPI_ID"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    IFSC_CODE = "IFSC_CODE"
    PHONE_NUMBER = "PHONE_NUMBER"
    PHISHING_URL = "PHISHING_URL"
    FAKE_OFFICER_ID = "FAKE_OFFICER_ID"


class CallStatus(str, Enum):
    """Lifecycle states of an intercepted scam call."""

    RINGING = "RINGING"
    HANDOVER_INITIATED = "HANDOVER_INITIATED"
    ACTIVE_ENGAGEMENT = "ACTIVE_ENGAGEMENT"
    DOSSIER_FINALIZED = "DOSSIER_FINALIZED"
    TERMINATED = "TERMINATED"


class SpeakerEmbeddingMetadata(BaseModel):
    """Metadata describing the vachana-vc-v1 [1, 768] bfloat16 speaker tensor."""

    model_name: str = Field(default="vachana-vc-v1")
    shape: List[int] = Field(default_factory=lambda: [1, 768])
    dtype: str = Field(default="torch.bfloat16")
    reference_duration_sec: float = Field(default=10.0)
    raw_byte_size: int = Field(default=1536)
    l2_norm: float = Field(...)
    bfloat16_hex_preview: List[str] = Field(...)
    embedding_sha256: str = Field(...)
    sample_values_preview: List[float] = Field(...)

    @validator("shape")
    def validate_shape(cls, v: List[int]) -> List[int]:
        if v != [1, 768]:
            raise ValueError(f"vachana-vc-v1 speaker embedding shape must be [1, 768], got {v}")
        return v

    @validator("dtype")
    def validate_dtype(cls, v: str) -> str:
        if v != "torch.bfloat16":
            raise ValueError(f"vachana-vc-v1 dtype must be 'torch.bfloat16', got {v}")
        return v


class AudioTelemetry(BaseModel):
    """Acoustic telemetry from Prisma v2.5 8kHz telephonic pipeline."""

    model_name: str = Field(default="Prisma-v2.5-Telephonic-8kHz")
    input_sample_rate_hz: int = Field(default=8000)
    processed_sample_rate_hz: int = Field(default=8000)
    bandpass_filter_hz: str = Field(default="300-3400Hz (4th-Order Butterworth)")
    duration_ms: float = Field(...)
    rms_db: float = Field(...)
    vad_active: bool = Field(...)
    zero_crossing_rate: float = Field(...)
    spectral_centroid_hz: float = Field(...)


class ScamAnalysisResult(BaseModel):
    """Scam classification and threat telemetry from Prisma v2.5."""

    scam_category: ScamCategory = Field(...)
    confidence: float = Field(..., ge=0.0, le=1.0)
    threat_score: float = Field(..., ge=0.0, le=100.0)
    claimed_authority: str = Field(...)
    coercion_tactics: List[str] = Field(default_factory=list)


class ExtractedIOC(BaseModel):
    """Single extracted Indicator of Compromise (Mule UPI, Bank Account, IFSC, etc.)."""

    ioc_id: str = Field(...)
    ioc_type: IOCType = Field(...)
    value: str = Field(...)
    confidence: float = Field(..., ge=0.0, le=1.0)
    bank_or_provider: str = Field(...)
    role_classification: str = Field(default="PRIMARY_MULE_INSTRUMENT")
    context_snippet: str = Field(...)
    first_seen_turn: int = Field(..., ge=1)
    flagged_for_npci_freeze: bool = Field(default=True)
    extracted_at: str = Field(default_factory=utc_now_iso)


class VoiceSynthesisPayload(BaseModel):
    """Synthesized anxious voice decoy output from vachana-vc-v1."""

    model_name: str = Field(default="vachana-vc-v1")
    sample_rate_hz: int = Field(default=8000)
    duration_ms: float = Field(...)
    prosody_profile: str = Field(default="ANXIOUS_COMPLIANT_HINGLISH")
    pitch_shift_hz: float = Field(default=14.0)
    jitter_percent: float = Field(default=1.8)
    speaking_rate: float = Field(default=0.94)
    waveform_envelope_64: List[float] = Field(...)
    wav_audio_base64: str = Field(...)
    watermark_sha256: str = Field(...)
    embedding_cosine_similarity: float = Field(...)


class TranscriptTurn(BaseModel):
    """A single conversational turn in the honeypot session."""

    turn_id: int = Field(..., ge=1)
    session_id: str = Field(...)
    speaker: str = Field(...)  # "SCAMMER" or "HONEYPOT_DECOY"
    text: str = Field(...)
    timestamp: str = Field(default_factory=utc_now_iso)
    deception_stage: DeceptionStage = Field(...)
    tactical_stall_reason: Optional[str] = None
    audio_telemetry: Optional[AudioTelemetry] = None
    voice_synthesis: Optional[VoiceSynthesisPayload] = None
    extracted_iocs: List[ExtractedIOC] = Field(default_factory=list)


class I4CDossier(BaseModel):
    """Structured Cybercrime FIR / I4C (1930 Helpline) Threat Intelligence Dossier."""

    dossier_id: str = Field(...)
    session_id: str = Field(...)
    generated_at: str = Field(default_factory=utc_now_iso)
    portal_jurisdiction: str = Field(
        default="Indian Cyber Crime Coordination Centre (I4C) : NCRP 1930 / cybercrime.gov.in"
    )
    applicable_legal_sections: List[str] = Field(
        default_factory=lambda: [
            "Bharatiya Nyaya Sanhita (BNS) Section 318(4) : Cheating and dishonestly inducing delivery of property",
            "Bharatiya Nyaya Sanhita (BNS) Section 319(2) : Cheating by personation",
            "Information Technology Act, 2000 Section 66C : Identity Theft",
            "Information Technology Act, 2000 Section 66D : Cheating by personation by using computer resource",
        ]
    )
    caller_number: str = Field(...)
    scam_category: ScamCategory = Field(...)
    claimed_authority: str = Field(...)
    threat_score: float = Field(...)
    scammer_time_wasted_sec: int = Field(...)
    current_deception_stage: DeceptionStage = Field(...)
    voice_clone_audit: SpeakerEmbeddingMetadata = Field(...)
    mule_upi_ids: List[ExtractedIOC] = Field(default_factory=list)
    mule_bank_accounts: List[ExtractedIOC] = Field(default_factory=list)
    ifsc_codes: List[ExtractedIOC] = Field(default_factory=list)
    scammer_phones: List[ExtractedIOC] = Field(default_factory=list)
    phishing_urls: List[ExtractedIOC] = Field(default_factory=list)
    fake_officer_ids: List[ExtractedIOC] = Field(default_factory=list)
    chronological_transcript: List[TranscriptTurn] = Field(default_factory=list)
    recommended_enforcement_actions: List[str] = Field(default_factory=list)
    sip_trunk_forwarding_sdp: Dict[str, Any] = Field(default_factory=dict)
    npci_threat_feed_payload: Dict[str, Any] = Field(default_factory=dict)
    formatted_fir_report_text: str = Field(...)


class CallSession(BaseModel):
    """Complete representation of an active or completed honeypot call session."""

    session_id: str = Field(...)
    caller_number: str = Field(...)
    victim_alias: str = Field(default="Protected Citizen #IN-8842")
    status: CallStatus = Field(default=CallStatus.HANDOVER_INITIATED)
    scam_category: ScamCategory = Field(default=ScamCategory.UNKNOWN)
    claimed_authority: str = Field(default="Unverified Caller")
    threat_score: float = Field(default=50.0)
    current_stage: DeceptionStage = Field(default=DeceptionStage.STAGE_1_INITIAL_PANIC)
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)
    time_wasted_sec: int = Field(default=0)
    speaker_embedding: SpeakerEmbeddingMetadata = Field(...)
    turns: List[TranscriptTurn] = Field(default_factory=list)
    extracted_iocs: List[ExtractedIOC] = Field(default_factory=list)


class CreateSessionRequest(BaseModel):
    """Request payload to hand over a suspicious call to Chakravyuh."""

    caller_number: str = Field(default="+91-9820471829")
    victim_alias: str = Field(default="Aarav Sharma (Voice Cloned Decoy)")
    initial_scam_hint: ScamCategory = Field(default=ScamCategory.DIGITAL_ARREST)
    reference_audio_base64: Optional[str] = Field(
        default=None,
        description="Optional 10-second PCM/WAV reference audio clip encoded in base64",
    )
    speaker_profile_seed: int = Field(default=42, ge=1, le=999999)


class TurnInputRequest(BaseModel):
    """Request payload for submitting a scammer utterance or 8kHz audio frame."""

    scammer_text: str = Field(..., min_length=1, max_length=4096)
    audio_pcm_base64: Optional[str] = Field(default=None)
    input_sample_rate_hz: int = Field(default=8000)

    @validator("scammer_text")
    def validate_non_whitespace(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("scammer_text cannot be empty or whitespace only")
        return cleaned


class TurnProcessingResponse(BaseModel):
    """Comprehensive response after processing a single duplex turn."""

    session_id: str = Field(...)
    scammer_turn: TranscriptTurn = Field(...)
    honeypot_turn: TranscriptTurn = Field(...)
    newly_extracted_iocs: List[ExtractedIOC] = Field(default_factory=list)
    scam_analysis: ScamAnalysisResult = Field(...)
    previous_stage: DeceptionStage = Field(...)
    current_stage: DeceptionStage = Field(...)
    updated_dossier: I4CDossier = Field(...)


class ThreatFeedEntry(BaseModel):
    """Phase 3 Live Threat Intelligence entry for Fintech / NPCI fraud engines."""

    feed_id: str = Field(...)
    ioc_type: IOCType = Field(...)
    ioc_value: str = Field(...)
    bank_or_provider: str = Field(...)
    role_classification: str = Field(...)
    scam_category: ScamCategory = Field(...)
    confidence: float = Field(...)
    source_session_id: str = Field(...)
    recommended_action: str = Field(default="IMMEDIATE_DEBIT_FREEZE_AND_LIEN_MARK")
    reported_at: str = Field(default_factory=utc_now_iso)
