# System Architecture  -  Chakravyuh Active Voice-Clone Honeypot

## 1. High-Level System Architecture

```
+---------------------------------------------------------------------------------------------------+
|                           SPLIT-SCREEN COMMAND CENTER UI (Web Client)                             |
|  +---------------------------------------------+   +-------------------------------------------+  |
|  | LEFT PANE: VICTIM & HONEYPOT CALL CONSOLE   |   | RIGHT PANE: LIVE I4C THREAT DOSSIER       |  |
|  | - Incoming Scam Alert ("Digital Arrest")    |   | - Real-Time Extracted Mule UPIs & Banks   |  |
|  | - [Hand Over to Honeypot] 1-Click Trigger   |   | - [1, 768] bfloat16 Embedding Telemetry   |  |
|  | - 8kHz Scammer vs Cloned Decoy Waveform     |   | - Evon v3.3 Deception State Machine       |  |
|  | - Live Hinglish Transcript Stream           |   | - Auto-Populated I4C / 1930 FIR Dossier   |  |
|  +----------------------+----------------------+   +---------------------+---------------------+  |
+-------------------------|------------------------------------------------|------------------------+
                          | Full-Duplex WebSocket (/ws/call/{session_id})  | REST API (/api/v1/*)
                          v                                                v
+---------------------------------------------------------------------------------------------------+
|                             CHAKRAVYUH FASTAPI ORCHESTRATION GATEWAY                              |
|                                                                                                   |
|  +---------------------------+   +----------------------------+   +----------------------------+  |
|  |    PRISMA v2.5 ENGINE     |   |      EVON v3.3 ENGINE      |   |    VACHANA-VC-v1 ENGINE    |  |
|  |  (8kHz Telephonic ASR)    |   | (Tactical Deception Brain) |   | (Speaker-Embedding Clone)  |  |
|  | - 8000Hz PCM/u-law ingest |   | - Hinglish Persona Prompts |   | - 10s Ref Clip Ingestion   |  |
|  | - 300-3400Hz Bandpass DSP |==>| - Stall State Machine      |==>| - [1, 768] torch.bfloat16  |  |
|  | - VAD & Acoustic Scoring  |   |   (UPI Lag / Limit Error)  |   |   Speaker Embedding Tensor |  |
|  | - Scam Intent Classifier  |   | - Contextual Baiting       |   | - Anxious Prosody Modulator|  |
|  +-------------+-------------+   +-------------+--------------+   +-------------+--------------+  |
|                |                               |                                |                 |
|                +-------------------------------+--------------------------------+                 |
|                                                |                                                  |
|                                                v                                                  |
|  +---------------------------------------------------------------------------------------------+  |
|  |                  INTELLIGENCE EXTRACTION & I4C DOSSIER ENGINE                               |  |
|  | - Regex + Context IOC Parser (UPI Handles, Bank Accts, IFSC, Phones, Crypto/Phishing URLs)  |  |
|  | - Mule Account Confidence Scorer & Deduplicator                                             |  |
|  | - Real-Time I4C / Cybercrime.gov.in FIR Dossier Compiler & Phase-3 Threat Feed Emitter      |  |
|  +---------------------------------------------+-----------------------------------------------+  |
|                                                |                                                  |
|                                                v                                                  |
|  +---------------------------------------------------------------------------------------------+  |
|  |                         SQLITE3 PERSISTENCE LAYER (WAL Mode)                                |  |
|  |   Tables: call_sessions | transcript_turns | extracted_iocs | i4c_dossiers | threat_feed    |  |
|  +---------------------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
```

## 2. Component Boundaries & Responsibilities

### 2.1 `src/chakravyuh/voice/`  -  `vachana-vc-v1` Speaker-Embedding & Voice Decoy Engine
- **Reference Clip Ingestion**: Accepts a 10-second reference audio signal (default `16000 Hz` or `8000 Hz` PCM float32/int16).
- **Mel-Spectrogram & Acoustic Projection**: Extracts spectral frames (MFCC / log-mel filterbanks, fundamental frequency $F_0$ contour, spectral centroid, jitter/shimmer) and projects them via a deterministic orthogonal projection matrix into a **`[1, 768]` speaker-embedding tensor**.
- **`bfloat16` Precision Enforcement**:
  - If `torch` is installed, outputs a native `torch.Tensor` of shape `(1, 768)` and `dtype=torch.bfloat16`.
  - In lightweight/edge environments without `torch`, implements a strict `BFloat16Tensor` wrapper backed by IEEE-754 float32 truncated to the upper 16 bits (`(uint32 + 0x7FFF + ((uint32 >> 16) & 1)) >> 16` round-to-nearest-even `bfloat16` bit representation stored as `uint16` and unpacked to `float32` for arithmetic), exposing `.shape == (1, 768)`, `.dtype == "torch.bfloat16"`, `.to_bfloat16_bytes()`, and `.cosine_similarity()`.
- **Anxious Prosody Synthesis**: Modulates pitch ($+12\%$ micro-tremor jitter), speaking rate ($0.94\times$ hesitant pacing), and breathiness to synthesize compliant, slightly anxious 8 kHz PCM audio packets for WebSocket transmission.

### 2.2 `src/chakravyuh/asr/`  -  `Prisma v2.5` 8 kHz Telephonic ASR & Scam Classifier
- **Telephonic DSP Pipeline**: Validates incoming audio sample rate; resamples arbitrary input rates to `8000 Hz` mono using `scipy.signal.resample_poly`, applies a 4th-order Butterworth band-pass filter (`300 Hz` to `3400 Hz` PSTN passband), and computes RMS energy (dBFS) and zero-crossing rate for Voice Activity Detection (VAD).
- **Scam Taxonomy Classifier**: Classifies incoming scammer utterances into:
  - `DIGITAL_ARREST` (CBI, Narcotics Control Bureau, Mumbai Police, Supreme Court warrant, Aadhaar money laundering)
  - `FEDEX_PARCEL` (FedEx/DHL customs seizure, MDMA/contraband, Taiwan/Thailand parcel)
  - `KYC_BANK_FRAUD` (PAN/SBI/HDFC KYC expiry, electricity bill disconnection, APK screen-share install)
  - `LOTTERY_EXTORTION` / `UNKNOWN`
- **Coercion & Threat Level Scoring**: Computes a real-time threat score (`0.0` to `100.0`) based on urgency markers ("arrest immediately", "CBI officer", "do not disconnect", "transfer to RBI verification account").

### 2.3 `src/chakravyuh/deception/`  -  `Evon v3.3` Tactical Deception State Machine
Operates a 6-stage state machine engineered to maximize scammer time wasted and force disclosure of secondary mule accounts:
1. `STAGE_1_INITIAL_PANIC`: Sounds frightened and compliant ("Sir please don't arrest me, main honest citizen hoon, main poora cooperate karunga...").
2. `STAGE_2_COMPLIANCE_HOOK`: Agrees to transfer funds for "RBI/CBI verification" or "Customs clearance" and asks where to send the money.
3. `STAGE_3_PRIMARY_UPI_STALL`: Once the scammer provides a primary UPI ID or QR/account, pretends the UPI app (GPay/PhonePe) is stuck on `"Processing... Bank Server Busy (Error U16)"` and asks for an **alternate/secondary UPI ID**.
4. `STAGE_4_SECONDARY_MULE_BAIT`: After extracting the secondary UPI ID, claims a `"₹1,00,000 daily UPI limit exceeded"` error on the secondary handle and requests a **direct IMPS/NEFT Bank Account Number + IFSC Code**.
5. `STAGE_5_PHISHING_AND_SUPERVISOR_BAIT`: Pretends the OTP screen is lagging and asks for the scammer's "Senior Officer WhatsApp number" or "Official Verification Portal Link" to extract phishing domains and supervisor phone numbers.
6. `STAGE_6_INFINITE_HOLD_LOOP`: Keeps the scammer on hold with simulated bank IVR/OTP delays while the I4C dossier is finalized and broadcast to threat feeds.

### 2.4 `src/chakravyuh/intelligence/`  -  Multi-Modal IOC Extractor
Deterministic + contextual extraction engine capturing:
- **UPI IDs (VPAs)**: `[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}` validated against known Indian PSP handles (`@ybl`, `@okaxis`, `@oksbi`, `@okhdfcbank`, `@okicici`, `@paytm`, `@ibl`, `@axl`, `@apl`, `@upi`, `@kotak`, `@barodampay`, `@fbl`, `@indus`) plus generic VPA validation, excluding standard email domains (`@gmail.com`, `@yahoo.com`, `@outlook.com`).
- **Bank Account Numbers**: 9 to 18 digit account strings contextualized by banking keywords (`account`, `a/c`, `ac no`, `khata`, `imps`, `neft`, `rtgs`, `beneficiary`) while filtering out 10-digit mobile numbers and 12-digit Aadhaar numbers where appropriate.
- **IFSC Codes**: Strict RBI format `^[A-Z]{4}0[A-Z0-9]{6}$` with automatic bank-name resolution (e.g., `SBIN` -> State Bank of India, `HDFC` -> HDFC Bank, `ICIC` -> ICICI Bank, `UTIB` -> Axis Bank, `PUNB` -> Punjab National Bank, `KKBK` -> Kotak Mahindra Bank, `BARB` -> Bank of Baroda, `CNRB` -> Canara Bank, `YESB` -> Yes Bank, `IDFB` -> IDFC First Bank).
- **Phone / WhatsApp Numbers**: Indian mobile numbers (`+91` / `0` / `[6-9]\d{9}`).
- **Phishing URLs & APK Links**: HTTP/HTTPS URLs, shortlinks (`bit.ly`, `tinyurl.com`), ngrok tunnels, and `.apk` download links.
- **Fake Identities & Badges**: Extracted officer names, fake CBI/Customs badge numbers, and spoofed case IDs.

### 2.5 `src/chakravyuh/dossier/` & `src/chakravyuh/storage/`  -  I4C Dossier & SQLite Persistence
- Compiles a legally structured **I4C (Indian Cyber Crime Coordination Centre) / National Cyber Crime Reporting Portal (1930) FIR Dossier** containing incident metadata, scam classification, chronological transcript log, acoustic & voice-clone verification audit trail, extracted mule financial instruments, and recommended NPCI freeze actions.
- Persists all state in SQLite (`chakravyuh.db`) with thread-safe connection pooling.

## 3. Data & Control Flow (WebSocket Duplex Handshake)
1. **Session Initialization (`POST /api/v1/sessions`)**: Client registers a call handover with caller number, scam suspicion hint, and optional 10-second reference audio clip.
2. **Voice Embedding Generation**: `vachana-vc-v1` processes the 10-second reference clip and caches the `[1, 768]` `bfloat16` speaker embedding on the session.
3. **WebSocket Connection (`WS /ws/call/{session_id}`)**:
   - Client sends `scammer_audio_or_text` payload (8 kHz PCM base64 frame or simulated transcript turn).
   - Server runs `Prisma v2.5` -> extracts transcript + 8 kHz acoustic telemetry + scam intent.
   - Server runs `IOCExtractor` -> extracts any new UPI IDs, bank accounts, IFSCs, URLs, or phone numbers.
   - Server runs `Evon v3.3` -> transitions deception state based on newly extracted IOCs and generates the next Hinglish bait response.
   - Server runs `vachana-vc-v1` conditioned on the `[1, 768]` `bfloat16` speaker embedding -> synthesizes anxious 8 kHz voice decoy audio + waveform envelope.
   - Server updates the I4C Dossier in SQLite and pushes a comprehensive `honeypot_turn_result` event over the WebSocket in `< 50ms`.

## 4. Security & Privacy Invariants
- **Victim Voice Consent & Ephemeral Embedding**: Reference audio clips are converted immediately into non-reversible `[1, 768]` `bfloat16` speaker embeddings; raw victim audio is never persisted to disk by default.
- **Synthetic Watermarking**: Every synthesized voice packet generated by `vachana-vc-v1` embeds a cryptographic SHA-256 frame signature in its metadata header so law enforcement can distinguish honeypot decoy turns from the actual human victim in court filings.
- **Strict Input Sanitization**: All extracted IOCs and scammer strings are sanitized before rendering or database insertion (parameterized SQL queries exclusively; zero string interpolation).

## 5. External Integration Boundaries & Technical Transparency
To maintain engineering truthfulness (Part III Invariants):
- **Phase 2 SIP / WebRTC Bridge**: Implements RFC 3261/3515 signaling formatting and ITU-T G.711 $\mu$-law logarithmic audio companding. Live PSTN interception and carrier IMS conference merges require telecom operator interconnect agreements, SBC infrastructure, and regulatory licensing.
- **Phase 3 Fintech Threat Feed**: Implements high-fidelity local risk screening and HMAC-SHA256 signed STIX-3.0 bundle formatting. Actual automated debit-freeze enforcement on external banking accounts requires authorized NPCI CFCFRMS / PSP API credentials.
- **Vachana-VC-v1 Acoustic Pipeline**: Implements spectral feature extraction with deterministic orthogonal projection into exact `[1, 768]` `torch.bfloat16` representations and FM prosody synthesis. Full zero-shot neural voice cloning requires trained neural model weights.
- **Prisma v2.5 Telephonic ASR**: Implements 8 kHz Butterworth bandpass filtering, RMS/ZCR voice activity detection, and keyword scam taxonomy classification. Continuous neural speech-to-text transcription requires separate acoustic model integration.
