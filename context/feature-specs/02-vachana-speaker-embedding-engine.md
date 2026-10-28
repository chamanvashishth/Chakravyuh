# Feature Spec 02  -  Vachana-VC-v1 Speaker Embedding & Voice Decoy Engine

## 1. Objective
Implement Gnani's `vachana-vc-v1` speaker-embedding extraction pipeline producing an exact `[1, 768]` tensor in `torch.bfloat16` precision from a 10-second user reference audio clip, coupled with an anxious/compliant Hinglish prosody synthesizer for WebSocket voice decoy streaming.

## 2. Context & Dependencies
- Depends on: `numpy`, `scipy.signal`, `hashlib`, `base64`, `io`, `wave`, `src/chakravyuh/models/schemas.py`.
- Key Unique Differentiator: Uses a `[1, 768]` speaker-embedding tensor in `bfloat16` for active cybersecurity deception rather than static content narration.

## 3. Exact Implementation Scope
- `src/chakravyuh/voice/__init__.py`
- `src/chakravyuh/voice/vachana_vc.py`

## 4. Required Behavior
1. **`BFloat16Tensor` Representation**:
   - Stores a 2D array of shape `(1, 768)`.
   - Converts `float32` values into true IEEE-754 16-bit Brain Floating Point (`bfloat16`: 1 sign bit, 8 exponent bits, 7 mantissa bits) via round-to-nearest-even bit manipulation (`uint32` view -> `uint16` bfloat16 raw words -> `float32` reconstructed values with zeroed lower 16 mantissa bits).
   - If `torch` is available at runtime, also provides `.to_torch()` returning `torch.Tensor` with `dtype=torch.bfloat16`.
   - Exposes `.shape == (1, 768)`, `.dtype == "torch.bfloat16"`, `.raw_bfloat16_uint16` (`1536` bytes), `.to_hex_preview()`, and `.cosine_similarity(other)`.
2. **10-Second Reference Clip Processing (`extract_speaker_embedding`)**:
   - Accepts raw PCM float32/int16 audio (or generates a calibrated 10.0s reference waveform for a given speaker profile seed when raw mic audio is omitted in headless/automated mode).
   - Enforces/normalizes to a 10.0-second window, extracts multi-band log-energy, spectral centroid, pitch contour ($F_0$), harmonic-to-noise ratio, and formant statistics, projects them into 768 dimensions, L2-normalizes the vector, and quantizes to `[1, 768]` `bfloat16`.
3. **Anxious Decoy Voice Synthesis (`synthesize_decoy_reply`)**:
   - Conditioned on the `[1, 768]` `bfloat16` embedding and the target Hinglish text + `DeceptionStage`.
   - Applies anxious prosody modulation (micro-jitter $1.8\%$, pitch elevation $+14\text{ Hz}$, hesitant syllable pauses) to produce an 8 kHz (`8000 Hz`) mono WAV/PCM audio payload, a 64-point waveform envelope for real-time UI rendering, and a cryptographic watermark SHA-256 hash.

## 5. Edge Cases & Security Considerations
- Handle short reference clips (`< 10s`) by symmetric reflection padding to 10.0s; handle long clips (`> 10s`) by selecting the highest-energy 10.0s voiced segment.
- Handle zero-energy (silent) reference clips gracefully without `NaN` division during L2 normalization.

## 6. Acceptance Criteria & Definition of Done
- `embedding.shape == (1, 768)` and `embedding.dtype == "torch.bfloat16"`.
- Every float value in the embedding has its lower 16 IEEE-754 bits strictly zeroed (`(uint32_bits & 0xFFFF) == 0`), proving true `bfloat16` quantization.
- Same speaker audio produces cosine similarity `> 0.98`; distinct speaker profiles produce lower similarity.
- Synthesized decoy audio returns valid 8000 Hz mono WAV bytes and 64-bin amplitude envelope.
