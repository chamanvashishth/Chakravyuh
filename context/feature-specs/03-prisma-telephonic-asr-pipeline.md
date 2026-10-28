# Feature Spec 03  -  Prisma v2.5 8 kHz Telephonic ASR & Scam Classifier

## 1. Objective
Implement the `Prisma v2.5` telephonic audio ingestion, 8 kHz PSTN signal processing (`300 Hz - 3400 Hz` bandpass), Voice Activity Detection (VAD), and Hinglish Scam Intent & Coercion Classifier.

## 2. Context & Dependencies
- Depends on: `numpy`, `scipy.signal`, `src/chakravyuh/models/schemas.py`.

## 3. Exact Implementation Scope
- `src/chakravyuh/asr/__init__.py`
- `src/chakravyuh/asr/prisma_asr.py`

## 4. Required Behavior
1. **8 kHz Telephonic Acoustic Pipeline (`process_telephonic_audio`)**:
   - Accepts raw PCM samples at any sample rate (`8000`, `16000`, `44100`, `48000 Hz`) and resamples deterministically to `8000 Hz` via `scipy.signal.resample_poly`.
   - Applies a 4th-order Butterworth band-pass filter (`300 Hz` to `3400 Hz` at `fs=8000 Hz`) to isolate telephonic voice frequencies.
   - Computes acoustic telemetry: `sample_rate_hz=8000`, `rms_db`, `vad_active`, `zero_crossing_rate`, `spectral_centroid_hz`, and `duration_ms`.
2. **Scam Taxonomy & Coercion Classifier (`classify_scammer_utterance`)**:
   - Analyzes Hinglish/English transcripts to classify scam category (`DIGITAL_ARREST`, `FEDEX_PARCEL`, `KYC_BANK_FRAUD`, `UTILITY_DISCONNECT`) with confidence score (`0.0 - 1.0`).
   - Computes a cumulative `threat_score` (`0.0 - 100.0`) and extracts `coercion_tactics` (e.g., `LAW_ENFORCEMENT_IMPERSONATION`, `IMMEDIATE_ARREST_THREAT`, `ISOLATION_COMMAND`, `FINANCIAL_VERIFICATION_DEMAND`, `URGENT_COUNTDOWN`).
   - Identifies the `claimed_authority` (e.g., `"CBI Cyber Crime Unit / Mumbai Police"`, `"FedEx International Customs & NCB"`, `"SBI KYC Verification Cell"`).

## 5. Acceptance Criteria & Definition of Done
- Audio at `16000 Hz` or `44100 Hz` is accurately downsampled to `8000 Hz` (`len(out) == int(len(in) * 8000 / sr)`).
- Digital Arrest, FedEx Parcel, and KYC scam utterances are classified with `>= 0.85` confidence and accurate coercion tags.
