"""Centralized configuration and architectural constants for Chakravyuh."""

import os
import tempfile
from dataclasses import dataclass


@dataclass(frozen=True)
class ChakravyuhConfig:
    """Immutable configuration governing models, audio DSP, and storage."""

    app_name: str = "Chakravyuh Active Voice-Clone Honeypot"
    version: str = "1.0.0"

    # Vachana-VC-v1 Speaker Embedding Specifications
    vachana_model_id: str = "vachana-vc-v1"
    embedding_batch_dim: int = 1
    embedding_feature_dim: int = 768
    embedding_dtype: str = "torch.bfloat16"
    reference_clip_duration_sec: float = 10.0

    # Prisma v2.5 Telephonic ASR Specifications
    prisma_model_id: str = "Prisma-v2.5-Telephonic-8kHz"
    telephonic_sample_rate_hz: int = 8000
    pstn_bandpass_low_hz: float = 300.0
    pstn_bandpass_high_hz: float = 3400.0
    vad_energy_threshold_db: float = -42.0

    # Evon v3.3 Tactical Deception Specifications
    evon_model_id: str = "Evon-v3.3-Hinglish-Deception"
    max_turn_text_length: int = 4096

    # Security & CORS Governance (Unit 10)
    allowed_origins: tuple = tuple(
        origin.strip()
        for origin in os.environ.get(
            "CHAKRAVYUH_ALLOWED_ORIGINS",
            "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000",
        ).split(",")
        if origin.strip()
    )
    allow_all_origins: bool = (
        os.environ.get("CHAKRAVYUH_ALLOW_ALL_ORIGINS", "false").lower() in ("true", "1")
    )
    api_key: str = os.environ.get("CHAKRAVYUH_API_KEY", "").strip()

    # Persistence (defaults to persistent data directory with env override)
    sqlite_db_path: str = os.environ.get(
        "CHAKRAVYUH_DB_PATH",
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "chakravyuh_honeypot.db",
        ),
    )


CONFIG = ChakravyuhConfig()
