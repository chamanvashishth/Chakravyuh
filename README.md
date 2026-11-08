# Chakravyuh (चक्रव्यूह)

## Active Voice-Clone Honeypot and Counter-Deception System for Telephonic Fraud

[![Tests](https://img.shields.io/badge/Tests-26%2F26%20PASSING-10b981?style=flat-square&logo=pytest&logoColor=white)](tests/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-38bdf8?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.92%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![DSP](https://img.shields.io/badge/DSP-8_kHz_Butterworth-f59e0b?style=flat-square)](src/chakravyuh/asr/)
[![Tensor](https://img.shields.io/badge/Embedding-%5B1%2C_768%5D_bfloat16-8b5cf6?style=flat-square)](src/chakravyuh/voice/)
[![Live Demo](https://img.shields.io/badge/Live_Demo-GitHub_Pages-lime?style=flat-square)](https://chamanvashishth.github.io/Chakravyuh/)
[![License](https://img.shields.io/badge/License-Apache_2.0-64748b?style=flat-square)](LICENSE)

Live Web Interface: https://chamanvashishth.github.io/Chakravyuh/

---

## What Chakravyuh Is and What It Does

Chakravyuh is an active cybersecurity defense system that counters telephonic financial extortion, specifically Digital Arrest police impersonation, fake FedEx narcotics parcel seizures, and urgent bank KYC utility disconnection scams.

Passive call blockers like Truecaller only flag numbers after hundreds of victims have already been defrauded. Because criminal syndicates rotate VoIP and SIP caller IDs continuously, passive blocking offers zero deterrence, costs scammers nothing, and leaves law enforcement with zero actionable intelligence on receiving bank accounts.

Chakravyuh reverses this dynamic:

1. Intercepts the Call: When an extortion call arrives, the user taps "Take Over Call" to hand the audio stream to the autonomous honeypot.
2. Clones the Voice: The Vachana engine generates a deterministic [1, 768] bfloat16 speaker embedding from a reference sample and synthesizes an anxious, submissive victim voice.
3. Stalls the Scammer: The Evon deception state machine engages the scammer in a multi-turn dialogue, feigning payment failures (such as "UPI Server Busy U16" or "Daily Transfer Limit Exceeded") to force the scammer into revealing backup mule accounts.
4. Extracts Financial Evidence: Captures, validates, and tags all Indicators of Compromise in real time, including mule UPI handles, bank accounts, IFSC codes, phone numbers, fake police badge IDs, and phishing URLs.
5. Generates Official FIR Dossier: Compiles an Indian Cyber Crime Coordination Centre (I4C / 1930 NCRP) compliant incident report ready for immediate police action and pre-transaction banking account freezes.

---

## Operational Architecture

```text
[ INCOMING CALL ] -> +91 98204-71829 (Spoofed CBI / Customs Authority)
       │
       ▼
[ PRISMA v2.5 ]   -> 8000 Hz Telephonic DSP (300-3400 Hz Butterworth Bandpass)
       │             Scam Classification & Voice Activity Detection
       ▼
[ 1-CLICK TAKEOVER ] Autonomous Honeypot Activation
       │
       ├─────────────────────────────────────────┐
       ▼                                         ▼
[ VACHANA-VC-v1 ]                         [ EVON v3.3 DECEPTION ]
Deterministic [1, 768] torch.bfloat16     Stage 1: Frightened Compliance
Speaker Embedding from 10s voice sample   Stage 2: Verification Agreement
Synthesizes Anxious Decoy Audio           Stage 3: "UPI Server Busy" (Mule Bait #1)
                                          Stage 4: "Daily Limit Exceeded" (Mule Bait #2)
                                          Stage 5: "Need Web Portal" (Phishing Link Bait)
                                          Stage 6: Infinite Hold Loop (Bank Clerk Sync)
       │                                         │
       └────────────────────┬────────────────────┘
                            │
                            ▼
[ IOC FORENSIC ENGINE ]
  ├── Primary VPA    : rbi.verification.cell@okaxis (Axis Bank)
  ├── Secondary VPA  : mumbaicrime.deposit99@ybl    (YES Bank)
  ├── Mule Bank A/C  : 50100482917364              (HDFC Bank - IFSC HDFC0001842)
  ├── Phishing APK   : http://cbi-rbi-verify-court.in/clearance.apk
  └── Scammer Phone  : +91-9820471829
                            │
       ┌────────────────────┴────────────────────┐
       ▼                                         ▼
[ I4C FIR DOSSIER ]                       [ NPCI THREAT ENGINE ]
Auto-generated structured JSON            Pre-Transaction API: BLOCK_TRANSACTION
Form 1930 / NCRP Evidentiary Report       Signed STIX-3.0 Broadcast to Banks
```

---

## Core Subsystems

### 1. Vachana Voice Clone Engine (vachana-vc-v1)
- Representation: Strict [1, 768] tensor in torch.bfloat16 precision (1536 bytes memory footprint).
- Calibration: Normalizes a 10.0-second user reference clip at 16 kHz with reflection padding and energy gating.
- Synthesis: Generates 8000 Hz telephonic mono audio with subtle anxiety micro-tremors and IEEE-754 round-to-nearest-even conversion.
- Non-Repudiation: Computes a SHA-256 cryptographic watermark on every synthesized turn, binding the embedding vector, transcript, and audio header so decoy turns cannot be misattributed to human victims.

### 2. Prisma Telephonic Audio Pipeline (Prisma v2.5)
- Standard: 8000 Hz mono audio processing optimized for cellular and PSTN networks.
- Filtering: 4th-order Butterworth bandpass filter spanning 300 Hz to 3400 Hz, with out-of-band rejection (>15x attenuation outside voice band).
- Numerical Resilience: Zero-division protection, NaN/Inf sanitization, and extreme clipping immunity (>10.0 amplitude values clamped cleanly).
- Classifier: Classifies calls into Digital Arrest, Customs Narcotics Parcel, or Bank KYC extortion.

### 3. Evon Tactical Deception Engine (Evon v3.3)
A six-stage psychological state machine engineered to exploit the greed and urgency of extortionists:
1. Stage 1 (Initial Panic): Feigns deep submission and distress ("Sir please arrest mat kijiye, main kya karoon bataiye...").
2. Stage 2 (Compliance Hook): Agrees to transfer funds to verify innocence or clear warrants.
3. Stage 3 (Primary UPI Stall): Claims Google Pay returned error "Bank Server Busy U16". Extracts secondary backup UPI handle.
4. Stage 4 (Secondary Mule Bait): Claims secondary UPI failed with "Daily Limit Exceeded". Requests direct bank account and IFSC details for RTGS transfer.
5. Stage 5 (Phishing & Supervisor Bait): Requests official case verification links or senior officer direct numbers. Extracts malicious APK links and WhatsApp C2 numbers.
6. Stage 6 (Infinite Hold Loop): Keeps the scammer waiting indefinitely ("Sir bank server timeout bol raha hai, 2 minute line par rahiye...") while accounts are flagged.

### 4. Financial IOC Extractor & I4C Dossier Compiler
- Patterns: Captures Indian VPAs (@okaxis, @okhdfcbank, @paytm, @ybl, etc.), 9 to 18 digit bank account numbers, 11-character RBI IFSC codes, phone numbers, and phishing URLs.
- Deduplication: Deduplicates targets and calculates confidence scores (0.90 to 0.99).
- Dossier: Compiles formal incident records formatted for the Indian Cyber Crime Coordination Centre (I4C) and 1930 NCRP reporting portal.

### 5. Phase 2 SIP Bridge & Phase 3 NPCI Threat Engine
- SIP Bridge: Simulates RFC 3515 SIP REFER call handover using ITU-T G.711 mu-law (PCMU/8000) audio transcoding with >0.99 waveform correlation.
- NPCI Threat Engine: Screens payment handles pre-transaction and returns BLOCK_TRANSACTION decisions on flagged mule accounts, broadcasting HMAC-SHA256 authenticated STIX-3.0 feeds.

---

## Command Center Interface

The web interface is built using a dark glassmorphism aesthetic inspired by frosted translucent stadium pills and 3D glossy indicators:

- Frosted Glass Stadium Pills: High-clarity frosted surfaces with backdrop-filter blur, translucent borders, and specular top highlights.
- 3D Glossy Jelly Badges: Ruby Red "X" badge representing intercepted scam threats and Electric Lime Check badge representing active decoy countermeasures.
- Dual-Channel 60 FPS Oscilloscope: Real-time HTML5 canvas rendering scammer input frequency alongside synthesized decoy responses.
- Ghost Watermark Typography & Ambient Blooms: Layered depth with radiant lime and rose blooms that shine and refract through the glass panels.
- Live Telemetry: Tracks time wasted, active deception stage, speaker embedding activations, and financial indicators.

Live online demo: https://chamanvashishth.github.io/Chakravyuh/

---

## Quickstart

### Prerequisites
- Python 3.11, 3.12, or 3.14
- Operating System: Windows, macOS, or Linux

### 1. Installation
```bash
git clone https://github.com/chamanvashishth/Chakravyuh.git
cd Chakravyuh/chakravyuh

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Run Automated Test Suite (26/26 Passing)
```bash
python run_tests.py
# or using Makefile:
make test
```
All 26 unit, integration, security, and audio DSP tests pass with zero external network dependencies.

### 3. Launch Local Honeypot Server
```bash
python -m uvicorn chakravyuh.main:app --host 127.0.0.1 --port 8000 --reload
# or using Makefile:
make run
```
Open **`http://127.0.0.1:8000/`** in your browser. The Command Center connects automatically to the local backend.

---

## API Authentication & Configuration

### Authentication
Chakravyuh operates in open development mode by default. To enforce API authentication in production:

1. Set the environment variable:
   ```bash
   # On Windows PowerShell:
   $env:CHAKRAVYUH_API_KEY = "your-secret-token"

   # On Linux / macOS:
   export CHAKRAVYUH_API_KEY="your-secret-token"
   ```
2. Mutating endpoints (`/api/v1/sessions`, `/api/v1/sessions/{id}/turn`, `/api/v1/threat-feed/*`) will require the `X-API-Key` HTTP header.
3. In the web interface, click the settings gear in the bottom dock to save your token. It is stored in browser localStorage and passed automatically.

### Environment Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `CHAKRAVYUH_ALLOWED_ORIGINS` | `http://127.0.0.1:8000,http://localhost:8000` | Comma-separated CORS origin allowlist |
| `CHAKRAVYUH_ALLOW_ALL_ORIGINS` | `false` | Set true only for isolated local testing |
| `CHAKRAVYUH_API_KEY` | None (Optional) | Enforces X-API-Key authentication when set |
| `CHAKRAVYUH_DB_PATH` | `./data/chakravyuh_honeypot.db` | Persistent SQLite database location |
| `CHAKRAVYUH_HOST` | `127.0.0.1` | Server binding address |
| `CHAKRAVYUH_PORT` | `8000` | Server HTTP port |

---

## API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | System status, model registry, and roadmap modules |
| `GET` | `/api/v1/scenarios` | Pre-configured scam scenarios (Digital Arrest, FedEx, KYC) |
| `POST` | `/api/v1/sessions` | Create a new honeypot call engagement session |
| `POST` | `/api/v1/sessions/{id}/turn` | Ingest scammer dialogue and return synthesized decoy reply |
| `GET` | `/api/v1/sessions/{id}/dossier` | Retrieve structured I4C / 1930 NCRP incident complaint |
| `POST` | `/api/v1/sessions/{id}/sip-merge` | Simulate RFC 3515 SIP REFER telecom call handover |
| `POST` | `/api/v1/threat-feed/check-transaction` | Pre-transaction screening against flagged mule accounts |
| `POST` | `/api/v1/threat-feed/broadcast/{id}` | Broadcast STIX-3.0 threat intelligence bundle |
| `WS` | `/ws/call/{id}` | Full-duplex real-time telephonic audio streaming |

---

## Sample I4C Incident Dossier

Every call engagement compiles a formal complaint for law enforcement and banking networks:

```json
{
  "dossier_id": "DOS-I4C-CHK-88F4A2",
  "incident_metadata": {
    "jurisdiction": "NCRP-1930 / I4C National Cybercrime Portal",
    "scam_category": "DIGITAL ARREST (98.4%)",
    "suspect_caller_id": "+91-9820471829",
    "claimed_authority": "CBI Cyber Crime Cell Mumbai / RBI Anti-Money Laundering Unit",
    "time_wasted_sec": 240,
    "handover_mode": "AUTOMATED_HONEYPOT_TAKEOVER"
  },
  "extracted_iocs": [
    {
      "type": "UPI_VPA",
      "value": "cbi.escrow.mumbai@okaxis",
      "role": "Mule Payment Handle",
      "provider": "OKAXIS (Axis Bank)",
      "confidence": 0.96
    },
    {
      "type": "BANK_ACCOUNT",
      "value": "987201928374",
      "role": "Mule Settlement Acct",
      "provider": "Canara Bank",
      "confidence": 0.92
    },
    {
      "type": "IFSC_CODE",
      "value": "CNRB0001092",
      "role": "Settlement Branch",
      "provider": "Canara Bank",
      "confidence": 0.98
    },
    {
      "type": "PHISHING_URL",
      "value": "http://cbi-cyber-cell-mumbai.verify-bail.in/auth",
      "role": "Phishing Gateway",
      "provider": "Credential Harvester",
      "confidence": 0.99
    }
  ],
  "voice_clone_audit": {
    "model_id": "vachana-vc-v1",
    "tensor_shape": [1, 768],
    "tensor_dtype": "torch.bfloat16",
    "watermark_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "codec": "ITU-T G.711 PCMU (8000 Hz)"
  },
  "recommended_actions": [
    "FREEZE_MULE_ACCOUNTS",
    "BLOCK_UPI_HANDLES_ACROSS_PSPS",
    "INITIATE_1930_NCRP_FREEZE"
  ]
}
```

---

## Security and Privacy Guardrails

- Ephemeral Voice Data: The 10-second reference clip is transformed into a non-reversible [1, 768] bfloat16 tensor. Raw audio is not persisted.
- Cryptographic Watermarking: Every synthesized voice frame embeds a SHA-256 watermark binding the embedding tensor and transcript to prevent misattribution.
- Defanged Malicious Links: URLs extracted from scammers are defanged (such as `hxxp://...`) in reports and interfaces to prevent accidental clicks.
- SQL Injection Protection: All database queries use parameterized SQL bindings exclusively.
- HMAC Verification: Threat intelligence broadcasts use RFC 2104 HMAC-SHA256 signatures validated in constant time.

---

## Project Structure

```text
chakravyuh/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Automated 26-test CI & GitHub Pages deploy
├── docs/
│   ├── index.html                 # Live Command Center WebApp
│   ├── architecture.md            # Detailed technical specification
│   ├── qa-report.md               # 26/26 automated test audit report
│   └── security-audit.md          # Threat model & security controls
├── src/
│   └── chakravyuh/
│       ├── main.py                # FastAPI entrypoint
│       ├── config.py              # Configuration & settings
│       ├── api/                   # REST routes & WebSocket gateway
│       ├── asr/                   # Prisma 8kHz Butterworth ASR
│       ├── deception/             # Evon 6-stage Hinglish deception engine
│       ├── dossier/               # I4C / 1930 NCRP FIR report generator
│       ├── intelligence/          # Financial IOC extractor
│       ├── models/                # Schemas & data contracts
│       ├── static/                # Modern glassmorphism UI
│       ├── storage/               # SQLite WAL persistence
│       ├── telecom/               # G.711 mu-law & SIP bridge
│       ├── threat_intel/          # NPCI STIX 3.0 fraud engine
│       └── voice/                 # Vachana [1, 768] bfloat16 clone engine
├── tests/                         # 26 automated unit and integration tests
├── .gitignore
├── Makefile
├── pyproject.toml
├── README.md
├── requirements.txt
└── run_tests.py
```

---

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
