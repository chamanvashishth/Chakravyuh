"""
Prisma v2.5: 8 kHz Telephonic Scammer Audio Processor & Hinglish Fraud Classifier.

Responsibilities:
1. Ingests telephonic audio streams, resampling arbitrary sample rates to 8000 Hz mono.
2. Applies a 4th-order Butterworth PSTN band-pass filter (300 Hz - 3400 Hz).
3. Computes Voice Activity Detection (VAD), RMS energy (dBFS), ZCR, and spectral centroid.
4. Classifies Hinglish scammer utterances into Digital Arrest, FedEx Parcel, or KYC Fraud,
   extracting coercion tactics and claimed authority.
"""

import base64
import hashlib
import math
from typing import List, Optional, Tuple
import numpy as np
from scipy import signal

from chakravyuh.config import CONFIG
from chakravyuh.models.schemas import (
    AudioTelemetry,
    ScamAnalysisResult,
    ScamCategory,
)


class PrismaTelephonicASREngine:
    """Prisma v2.5 8 kHz Telephonic Audio DSP and Scam Intent Classifier."""

    def __init__(self) -> None:
        self.model_name = CONFIG.prisma_model_id
        self.target_sr = CONFIG.telephonic_sample_rate_hz  # 8000 Hz
        self._sos_bandpass = signal.butter(
            4,
            [CONFIG.pstn_bandpass_low_hz, CONFIG.pstn_bandpass_high_hz],
            btype="bandpass",
            fs=self.target_sr,
            output="sos",
        )

    def synthesize_scammer_8khz_frame(self, text: str, duration_sec: float = 1.6) -> np.ndarray:
        """
        Generate a deterministic 8 kHz telephonic audio frame matching the scammer utterance
        when raw PCM audio is not attached to a text simulation turn.
        """
        num_samples = int(duration_sec * self.target_sr)
        t = np.linspace(0.0, duration_sec, num_samples, endpoint=False, dtype=np.float32)
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        base_f0 = 110.0 + (digest[0] % 55)
        raw = (
            0.65 * np.sin(2.0 * np.pi * base_f0 * t)
            + 0.35 * np.sin(2.0 * np.pi * (base_f0 * 2.1) * t)
            + 0.20 * np.sin(2.0 * np.pi * (base_f0 * 3.4) * t)
        )
        cadence = 0.6 + 0.4 * np.sin(2.0 * np.pi * 4.8 * t + (digest[1] / 255.0))
        return (raw * cadence * 0.75).astype(np.float32)

    def resample_to_8khz(self, audio_samples: np.ndarray, input_sr: int) -> np.ndarray:
        """Resample arbitrary mono PCM audio to 8000 Hz telephonic sample rate."""
        samples = np.asarray(audio_samples, dtype=np.float32).flatten()
        if samples.size == 0:
            return np.zeros(800, dtype=np.float32)
        if input_sr <= 0:
            raise ValueError(f"input_sr must be positive, got {input_sr}")
        if input_sr == self.target_sr:
            return samples
        gcd = math.gcd(self.target_sr, input_sr)
        up = self.target_sr // gcd
        down = input_sr // gcd
        resampled = signal.resample_poly(samples, up, down)
        return np.asarray(resampled, dtype=np.float32)

    def process_telephonic_audio(
        self,
        audio_samples: Optional[np.ndarray] = None,
        input_sr: int = 8000,
        fallback_text: str = "Hello",
        audio_pcm_base64: Optional[str] = None,
    ) -> Tuple[np.ndarray, AudioTelemetry]:
        """
        Process raw scammer audio through the 8 kHz PSTN bandpass filter and compute VAD telemetry.
        """
        if audio_pcm_base64:
            try:
                raw_bytes = base64.b64decode(audio_pcm_base64)
                if len(raw_bytes) >= 4:
                    int16_arr = np.frombuffer(
                        raw_bytes[: len(raw_bytes) - (len(raw_bytes) % 2)], dtype=np.int16
                    )
                    audio_samples = int16_arr.astype(np.float32) / 32768.0
            except Exception:
                audio_samples = None

        if audio_samples is None or np.asarray(audio_samples).size == 0:
            audio_samples = self.synthesize_scammer_8khz_frame(fallback_text)
            input_sr = self.target_sr
        else:
            audio_samples = np.nan_to_num(
                np.asarray(audio_samples, dtype=np.float32),
                nan=0.0,
                posinf=1.0,
                neginf=-1.0,
            )
            audio_samples = np.clip(audio_samples, -1.0, 1.0)

        pcm_8khz = self.resample_to_8khz(audio_samples, input_sr=input_sr)
        filtered_8khz = signal.sosfilt(self._sos_bandpass, pcm_8khz).astype(np.float32)

        rms = float(np.sqrt(np.mean(filtered_8khz * filtered_8khz) + 1e-12))
        rms_db = float(20.0 * math.log10(max(rms, 1e-6)))
        vad_active = bool(rms_db > CONFIG.vad_energy_threshold_db)

        if filtered_8khz.size > 1:
            zcr = float(np.mean(np.abs(np.diff(np.signbit(filtered_8khz)))))
        else:
            zcr = 0.0

        # Spectral centroid in Hz (0 - 4000 Hz Nyquist at 8 kHz)
        spectrum = np.abs(np.fft.rfft(filtered_8khz))
        freqs = np.fft.rfftfreq(filtered_8khz.size, d=1.0 / self.target_sr)
        spec_sum = float(np.sum(spectrum))
        if spec_sum > 1e-9:
            centroid_hz = float(np.sum(freqs * spectrum) / spec_sum)
        else:
            centroid_hz = 1000.0

        duration_ms = round((filtered_8khz.size / float(self.target_sr)) * 1000.0, 2)

        telemetry = AudioTelemetry(
            model_name=self.model_name,
            input_sample_rate_hz=input_sr,
            processed_sample_rate_hz=self.target_sr,
            bandpass_filter_hz="300-3400Hz (4th-Order Butterworth)",
            duration_ms=duration_ms,
            rms_db=round(rms_db, 2),
            vad_active=vad_active,
            zero_crossing_rate=round(zcr, 4),
            spectral_centroid_hz=round(centroid_hz, 1),
        )
        return filtered_8khz, telemetry

    def classify_scammer_utterance(
        self, text: str, prior_category: ScamCategory = ScamCategory.UNKNOWN
    ) -> ScamAnalysisResult:
        """
        Classify Hinglish/English scammer utterance into scam taxonomy, extract coercion
        tactics, and compute a real-time threat score.
        """
        lower = text.lower()

        digital_arrest_kw = [
            "digital arrest",
            "cbi",
            "mumbai police",
            "crime branch",
            "supreme court",
            "warrant",
            "money laundering",
            "naresh goyal",
            "rbi verification",
            "aadhaar",
            "fir",
            "ncb",
            "cyber cell",
            "arrest",
            "custody",
            "video call",
        ]
        fedex_kw = [
            "fedex",
            "dhl",
            "parcel",
            "customs",
            "mdma",
            "drugs",
            "narcotics",
            "taiwan",
            "bangkok",
            "contraband",
            "passport",
            "seized",
            "shipment",
            "courier",
        ]
        kyc_kw = [
            "kyc",
            "pan card",
            "account block",
            "sbi",
            "hdfc",
            "electricity",
            "bijli",
            "power cut",
            "apk",
            "anydesk",
            "rustdesk",
            "otp",
            "suspended",
            "update kyc",
        ]

        da_hits = sum(1 for kw in digital_arrest_kw if kw in lower)
        fx_hits = sum(1 for kw in fedex_kw if kw in lower)
        kyc_hits = sum(1 for kw in kyc_kw if kw in lower)

        if fx_hits > da_hits and fx_hits >= kyc_hits and fx_hits > 0:
            category = ScamCategory.FEDEX_PARCEL
            confidence = min(0.99, 0.82 + 0.05 * fx_hits)
            authority = "Spoofed FedEx International Customs / NCB Narcotics Cell"
        elif da_hits >= fx_hits and da_hits >= kyc_hits and da_hits > 0:
            category = ScamCategory.DIGITAL_ARREST
            confidence = min(0.99, 0.84 + 0.04 * da_hits)
            authority = "Spoofed CBI / Mumbai Cyber Crime Branch / RBI Verification Cell"
        elif kyc_hits > 0:
            category = ScamCategory.KYC_BANK_FRAUD
            confidence = min(0.99, 0.83 + 0.05 * kyc_hits)
            authority = "Spoofed SBI/NPCI KYC & Utility Disconnection Desk"
        elif prior_category != ScamCategory.UNKNOWN:
            category = prior_category
            confidence = 0.88
            authority_map = {
                ScamCategory.DIGITAL_ARREST: "Spoofed CBI / Mumbai Cyber Crime Branch",
                ScamCategory.FEDEX_PARCEL: "Spoofed FedEx International Customs & NCB",
                ScamCategory.KYC_BANK_FRAUD: "Spoofed Banking KYC Verification Officer",
                ScamCategory.UTILITY_DISCONNECT: "Spoofed State Electricity Board",
            }
            authority = authority_map.get(prior_category, "Suspected Financial Fraud Caller")
        else:
            category = ScamCategory.DIGITAL_ARREST
            confidence = 0.75
            authority = "Suspected Telephonic Extortion / Mule Operator"

        # Detect specific psychological coercion tactics
        tactics: List[str] = []
        if any(w in lower for w in ["cbi", "police", "officer", "customs", "rbi", "court", "ncb"]):
            tactics.append("AUTHORITY_IMPERSONATION")
        if any(w in lower for w in ["arrest", "warrant", "jail", "fir", "non-bailable", "seized"]):
            tactics.append("IMMEDIATE_ARREST_COERCION")
        if any(
            w in lower
            for w in ["upi", "transfer", "rtgs", "imps", "neft", "account", "ifsc", "pay", "deposit"]
        ):
            tactics.append("MULE_PAYMENT_EXTRACTION_DEMAND")
        if any(
            w in lower
            for w in ["abhi", "immediately", "5 minute", "turant", "disconnect mat", "do not cut"]
        ):
            tactics.append("ARTIFICIAL_TIME_PRESSURE_AND_ISOLATION")
        if any(w in lower for w in ["http", ".apk", "link", "click", "portal", "whatsapp"]):
            tactics.append("PHISHING_OR_MALWARE_DELIVERY")

        if not tactics:
            tactics.append("SOCIAL_ENGINEERING_PROBING")

        base_threat = 68.0 + (da_hits + fx_hits + kyc_hits) * 6.5 + len(tactics) * 5.5
        threat_score = round(float(np.clip(base_threat, 55.0, 99.8)), 1)

        return ScamAnalysisResult(
            scam_category=category,
            confidence=round(confidence, 3),
            threat_score=threat_score,
            claimed_authority=authority,
            coercion_tactics=tactics,
        )
