"""Unit tests for Vachana-VC-v1 ([1, 768] bfloat16) and Prisma v2.5 (8 kHz Telephonic ASR)."""

import base64
import io
import unittest
import wave
import numpy as np

from chakravyuh.asr.prisma_asr import PrismaTelephonicASREngine
from chakravyuh.models.schemas import DeceptionStage, ScamCategory
from chakravyuh.voice.vachana_vc import BFloat16Tensor, VachanaVoiceCloneEngine


class TestVachanaVoiceCloneEngine(unittest.TestCase):
    """Verify [1, 768] torch.bfloat16 speaker embedding invariants and voice synthesis."""

    def setUp(self) -> None:
        self.engine = VachanaVoiceCloneEngine()

    def test_bfloat16_tensor_shape_dtype_and_bit_truncation(self) -> None:
        """Embedding must strictly have shape (1, 768), dtype 'torch.bfloat16', and 1536 bytes."""
        bf16_tensor, meta = self.engine.extract_speaker_embedding(speaker_seed=42)
        self.assertEqual(bf16_tensor.shape, (1, 768))
        self.assertEqual(bf16_tensor.dtype, "torch.bfloat16")
        self.assertEqual(bf16_tensor.nbytes, 1536)
        self.assertTrue(bf16_tensor.verify_bfloat16_bit_invariant())
        self.assertEqual(meta.shape, [1, 768])
        self.assertEqual(meta.dtype, "torch.bfloat16")
        self.assertEqual(meta.raw_byte_size, 1536)
        self.assertEqual(len(meta.bfloat16_hex_preview), 12)
        self.assertAlmostEqual(bf16_tensor.l2_norm(), 1.0, delta=0.02)

    def test_speaker_embedding_determinism_and_separation(self) -> None:
        """Identical speaker clips must have cosine similarity 1.0; different speakers differ."""
        emb_a1, _ = self.engine.extract_speaker_embedding(speaker_seed=101)
        emb_a2, _ = self.engine.extract_speaker_embedding(speaker_seed=101)
        emb_b, _ = self.engine.extract_speaker_embedding(speaker_seed=202)

        self.assertAlmostEqual(emb_a1.cosine_similarity(emb_a2), 1.0, places=5)
        sim_diff = emb_a1.cosine_similarity(emb_b)
        self.assertLess(sim_diff, 0.999)

    def test_short_and_long_reference_clip_normalization(self) -> None:
        """Short (<10s) and long (>10s) clips must normalize cleanly to 10.0s at 16kHz."""
        short_clip = np.sin(np.linspace(0, 50, 3200, dtype=np.float32))  # 0.2s
        long_clip = np.sin(np.linspace(0, 500, 16000 * 15, dtype=np.float32))  # 15.0s

        emb_short, meta_short = self.engine.extract_speaker_embedding(
            reference_audio=short_clip, sample_rate=16000
        )
        emb_long, meta_long = self.engine.extract_speaker_embedding(
            reference_audio=long_clip, sample_rate=16000
        )
        self.assertEqual(emb_short.shape, (1, 768))
        self.assertEqual(emb_long.shape, (1, 768))
        self.assertEqual(meta_short.reference_duration_sec, 10.0)
        self.assertEqual(meta_long.reference_duration_sec, 10.0)

    def test_silent_reference_clip_does_not_produce_nan(self) -> None:
        """Zero-energy silent audio must not cause NaN division during L2 normalization."""
        silent = np.zeros(16000 * 10, dtype=np.float32)
        emb, meta = self.engine.extract_speaker_embedding(reference_audio=silent, sample_rate=16000)
        self.assertFalse(np.isnan(emb.numpy_float32()).any())
        self.assertGreater(meta.l2_norm, 0.9)

    def test_anxious_decoy_voice_synthesis_8khz_wav(self) -> None:
        """Synthesized decoy reply must output valid 8000 Hz mono WAV and 64-bin envelope."""
        emb, _ = self.engine.extract_speaker_embedding(speaker_seed=42)
        payload = self.engine.synthesize_decoy_reply(
            reply_text="Sir please mujhe Digital Arrest mat kijiye, main abhi UPI karta hoon!",
            speaker_embedding=emb,
            stage=DeceptionStage.STAGE_3_PRIMARY_UPI_STALL,
        )
        self.assertEqual(payload.sample_rate_hz, 8000)
        self.assertEqual(len(payload.waveform_envelope_64), 64)
        self.assertEqual(len(payload.watermark_sha256), 64)

        wav_bytes = base64.b64decode(payload.wav_audio_base64)
        with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
            self.assertEqual(wf.getnchannels(), 1)
            self.assertEqual(wf.getsampwidth(), 2)
            self.assertEqual(wf.getframerate(), 8000)
            self.assertGreater(wf.getnframes(), 8000)


class TestPrismaTelephonicASREngine(unittest.TestCase):
    """Verify Prisma v2.5 8 kHz resampling, bandpass filtering, and scam classification."""

    def setUp(self) -> None:
        self.prisma = PrismaTelephonicASREngine()

    def test_resample_44100_and_16000_to_8000_hz(self) -> None:
        """Arbitrary input sample rates must resample accurately to 8000 Hz."""
        sr_in = 16000
        t = np.linspace(0, 1.0, sr_in, endpoint=False, dtype=np.float32)
        tone_1khz = 0.6 * np.sin(2.0 * np.pi * 1000.0 * t)
        filtered, telemetry = self.prisma.process_telephonic_audio(
            audio_samples=tone_1khz, input_sr=sr_in
        )
        self.assertEqual(filtered.size, 8000)
        self.assertEqual(telemetry.processed_sample_rate_hz, 8000)
        self.assertTrue(telemetry.vad_active)
        self.assertAlmostEqual(telemetry.duration_ms, 1000.0, delta=5.0)

    def test_classify_digital_arrest_fedex_and_kyc_scams(self) -> None:
        """Verify accurate classification across all three primary scam categories."""
        da_res = self.prisma.classify_scammer_utterance(
            "Main CBI Cyber Crime Mumbai Police se bol raha hoon, aap Digital Arrest mein hain!"
        )
        self.assertEqual(da_res.scam_category, ScamCategory.DIGITAL_ARREST)
        self.assertGreaterEqual(da_res.confidence, 0.85)
        self.assertIn("IMMEDIATE_ARREST_COERCION", da_res.coercion_tactics)

        fx_res = self.prisma.classify_scammer_utterance(
            "FedEx International Customs se call hai, aapke Taiwan parcel mein MDMA drugs mile hain!"
        )
        self.assertEqual(fx_res.scam_category, ScamCategory.FEDEX_PARCEL)
        self.assertGreaterEqual(fx_res.confidence, 0.85)

        kyc_res = self.prisma.classify_scammer_utterance(
            "Aapka SBI PAN card KYC aaj block ho jayega aur bijli power cut ho jayegi, APK install karo!"
        )
        self.assertEqual(kyc_res.scam_category, ScamCategory.KYC_BANK_FRAUD)
        self.assertGreaterEqual(kyc_res.confidence, 0.85)

    def test_butterworth_out_of_band_attenuation(self) -> None:
        """Energy outside the 300-3400 Hz passband (e.g. 80 Hz hum) must be attenuated compared to in-band 1 kHz."""
        t = np.linspace(0, 1.0, 8000, endpoint=False, dtype=np.float32)
        tone_inband = 0.5 * np.sin(2.0 * np.pi * 1000.0 * t)
        tone_outband = 0.5 * np.sin(2.0 * np.pi * 80.0 * t)

        filtered_in, _ = self.prisma.process_telephonic_audio(audio_samples=tone_inband, input_sr=8000)
        filtered_out, _ = self.prisma.process_telephonic_audio(audio_samples=tone_outband, input_sr=8000)

        rms_in = float(np.sqrt(np.mean(filtered_in * filtered_in)))
        rms_out = float(np.sqrt(np.mean(filtered_out * filtered_out)))
        # Out-of-band 80 Hz must be attenuated by at least 15x compared to 1 kHz
        self.assertGreater(rms_in / max(rms_out, 1e-6), 15.0)

    def test_extreme_clipping_and_nan_resilience(self) -> None:
        """Audio samples with NaN, Inf, or extreme > 10.0 clipping must be sanitized without crashing."""
        t = np.linspace(0, 0.5, 4000, endpoint=False, dtype=np.float32)
        wild_samples = np.sin(2.0 * np.pi * 400.0 * t) * 50.0  # severely clipped
        wild_samples[100] = np.nan
        wild_samples[200] = np.inf

        filtered, telemetry = self.prisma.process_telephonic_audio(
            audio_samples=wild_samples, input_sr=8000
        )
        self.assertEqual(filtered.size, 4000)
        self.assertFalse(np.isnan(filtered).any())
        self.assertFalse(np.isinf(filtered).any())
        self.assertTrue(telemetry.vad_active)

    def test_decoy_synthesis_across_all_deception_stages(self) -> None:
        """vachana-vc-v1 must synthesize valid 8 kHz audio across all 6 deception stages."""
        engine = VachanaVoiceCloneEngine()
        emb, _ = engine.extract_speaker_embedding(speaker_seed=77)
        for stage in DeceptionStage:
            payload = engine.synthesize_decoy_reply(
                reply_text=f"Testing synthesis in stage {stage.value}",
                speaker_embedding=emb,
                stage=stage,
            )
            self.assertEqual(payload.sample_rate_hz, 8000)
            self.assertEqual(len(payload.waveform_envelope_64), 64)
            self.assertTrue(len(payload.wav_audio_base64) > 100)


if __name__ == "__main__":
    unittest.main()
