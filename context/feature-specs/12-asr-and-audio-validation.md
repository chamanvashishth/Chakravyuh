# Feature Spec 12  -  ASR Telephonic DSP & Acoustic Validation

## 1. Objective
Strengthen input validation, numerical stability, and boundary edge case handling for the `Prisma v2.5` 8 kHz telephonic DSP pipeline and `vachana-vc-v1` speaker-embedding engine.

## 2. Existing Architecture Context
`Prisma v2.5` (`src/chakravyuh/asr/prisma_asr.py`) processes 8 kHz telephonic audio with 4th-order Butterworth bandpass filtering (`300-3400 Hz`), VAD telemetry, and scam classification. `vachana-vc-v1` (`src/chakravyuh/voice/vachana_vc.py`) extracts a `[1, 768]` `torch.bfloat16` tensor from 10-second reference audio and synthesizes anxious prosody responses.

## 3. Dependencies
- Standard library: `math`, `typing`, `wave`, `io`
- External libraries: `numpy`, `scipy.signal`
- Internal modules: `chakravyuh.asr.prisma_asr`, `chakravyuh.voice.vachana_vc`

## 4. Exact Files in Scope
- `src/chakravyuh/asr/prisma_asr.py`
- `src/chakravyuh/voice/vachana_vc.py`
- `tests/test_unit_voice_and_asr.py`

## 5. Required Behavior
1. **Audio Validation & Extreme Boundary Handling**:
   - Ingesting clipped audio (`values > 1.0` or `< -1.0`), DC bias, or extreme audio bursts must clip gracefully without arithmetic overflow or filter explosion.
   - Malformed base64 strings in `audio_pcm_base64` must fall back cleanly to synthesized telephonic framing without raising unhandled exceptions.
2. **Frequency Verification**:
   - Verify that energy outside the 300-3400 Hz bandpass (e.g., 60 Hz mains hum, 3800 Hz high frequencies) is attenuated by ≥ 18 dB.
3. **Synthesis Consistency**:
   - Ensure `vachana-vc-v1` decoy synthesis deterministically generates valid 8000 Hz 16-bit mono PCM WAV bytes across all six `DeceptionStage` values.

## 6. Security Constraints
- Audio buffer sizes must be bounded (`max_audio_bytes = 2 * 8000 * 30` = 480 KB for 30s) to prevent memory allocation denial-of-service.

## 7. Edge Cases
- All-zero (silent) audio inputs.
- High-amplitude DC offset.
- Non-standard sample rates (e.g. 11025 Hz, 22050 Hz, 32000 Hz).

## 8. Tests
- Attenuation verification test for out-of-band signals (100 Hz and 3800 Hz).
- Extreme amplitude clipping test.
- Malformed base64 audio fallback test.

## 9. Acceptance Criteria
- Full 19 baseline tests pass.
- New edge cases verified with runnable unit tests.

## 10. Explicit Exclusions
- Deploying heavy neural weights (e.g. Whisper / XTTS) without explicit model weights provided.

## 11. Definition of Done
- Validation enhancements and tests implemented and passing.

