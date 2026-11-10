# Chakravyuh

Active Voice Clone Defense and Telephonic Honeypot

[![Tests](https://img.shields.io/badge/Tests-26%2F26%20PASSING-10b981?style=flat-square&logo=pytest&logoColor=white)](tests/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-38bdf8?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.92%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![DSP](https://img.shields.io/badge/DSP-8_kHz_Butterworth-f59e0b?style=flat-square)](src/chakravyuh/asr/)
[![Tensor](https://img.shields.io/badge/Embedding-%5B1%2C_768%5D_bfloat16-8b5cf6?style=flat-square)](src/chakravyuh/voice/)
[![Live Console](https://img.shields.io/badge/Live_Console-GitHub_Pages-lime?style=flat-square)](https://chamanvashishth.github.io/Chakravyuh/)
[![License](https://img.shields.io/badge/License-Apache_2.0-64748b?style=flat-square)](LICENSE)

---

## What Chakravyuh Is

Chakravyuh is an automated voice honeypot built to defend against telephone extortion.

Most defenses rely on caller ID blocklists. Blocklists fail because scammers change phone numbers continuously. Chakravyuh takes the opposite approach. When an extortion call arrives you hand the call over to the system. An acoustic model clones your voice from a short reference clip. An automated agent answers the caller with an anxious persona. The agent pretends payment attempts failed and asks for alternative accounts. As the scammer speaks the extractor captures payment handles bank accounts and routing codes. Once the call ends the system writes a complete incident report for police and banking networks.

---

## How It Works

1. Call Handover
You transfer an incoming extortion call to the honeypot gateway.

2. Voice Cloning
The Vachana engine turns a ten second reference clip into a 768 dimension bfloat16 tensor and generates realistic telephone audio.

3. Tactical Stall
The Evon deception engine cycles through panic compliance payment errors and hold loops. The scammer stays on the line waiting for funds.

4. Evidence Extraction
The intelligence engine captures payment handles bank account numbers IFSC codes and malicious links from the dialogue.

5. Incident Report
The dossier generator creates structured complaints aligned with the Indian Cyber Crime Coordination Centre and the 1930 helpline.

---

## System Architecture

```text
[ Incoming Call ] -> +91 98204 71829
       |
       v
[ Prisma Audio Filter ] -> 8000 Hz Bandpass Filter (300 to 3400 Hz)
       |                   Scam Classification and Voice Activity Detection
       v
[ Honeypot Handover ] -> Autonomous Agent Takes Over
       |
       +-----------------------------------------+
       |                                         |
       v                                         v
[ Vachana Voice Engine ]                  [ Evon Deception Engine ]
Converts 10s voice clip                   Stage 1: Frightened Compliance
Generates 768 dim bfloat16 tensor         Stage 2: Payment Agreement
Synthesizes Anxious Decoy Audio           Stage 3: UPI Server Busy Error
                                          Stage 4: Daily Limit Exceeded Error
                                          Stage 5: Need Web Portal Link
                                          Stage 6: Infinite Hold Loop
       |                                         |
       +--------------------+--------------------+
                            |
                            v
[ Financial Intelligence Extractor ]
  Primary VPA    : rbi.verification.cell@okaxis
  Secondary VPA  : mumbaicrime.deposit99@ybl
  Bank Account   : 50100482917364 (HDFC Bank IFSC HDFC0001842)
  Phishing APK   : http://cbi-rbi-verify-court.in/clearance.apk
  Phone Number   : +91 98204 71829
                            |
       +--------------------+--------------------+
       |                                         |
       v                                         v
[ Incident Dossier Compiler ]             [ Banking Threat Engine ]
Auto generated incident JSON              Transaction Screening: BLOCK TRANSACTION
Official 1930 Helpline Report             STIX 3.0 Broadcast Feed to Banks
```

---

## Core Components

### 1. Vachana Voice Clone Engine
- Generates a 768 dimension bfloat16 tensor requiring 1536 bytes of memory.
- Uses a ten second reference clip at 16 kHz with reflection padding.
- Synthesizes 8000 Hz telephonic mono audio with subtle anxiety tremors.
- Stamps every synthesized voice packet with a SHA256 watermark to distinguish honeypot audio from human statements.

### 2. Prisma Telephonic Audio Pipeline
- Processes 8000 Hz mono audio standard on mobile and landline networks.
- Uses a fourth order Butterworth bandpass filter from 300 Hz to 3400 Hz.
- Clamps extreme amplitudes and shields the pipeline from NaN values.
- Flags Digital Arrest extortion fake parcel seizures and urgent bank account threats.

### 3. Evon Tactical Deception Engine
A six stage state machine that exploits the urgency of extortionists:
1. Stage 1 Panic: Feigns submission and asks what to do.
2. Stage 2 Agreement: Agrees to transfer money to clear charges.
3. Stage 3 Primary UPI Stall: Reports a server busy error to extract a backup handle.
4. Stage 4 Secondary Mule Bait: Reports a daily limit error to extract a bank account and IFSC code.
5. Stage 5 Phishing Bait: Asks for a verification portal to extract malicious links.
6. Stage 6 Infinite Hold Loop: Keeps the scammer waiting on the line while accounts are flagged.

### 4. Financial Intelligence Extractor
- Extracts Indian VPAs bank account numbers IFSC codes phone numbers and web links.
- Deduplicates indicators and assigns confidence scores from 0.90 to 0.99.
- Outputs incident records formatted for the Indian Cyber Crime Coordination Centre.

### 5. Telecom Bridge and Banking Feed
- Simulates telephone call handover using RFC 3515 SIP REFER with G.711 mu law audio.
- Screens payment handles in real time and returns block decisions for flagged accounts.

---

## Web Console

The browser console provides an interactive control center:
- Rotating Chakravyuh defense radar showing active call stages
- Dual trace 60 FPS oscilloscope displaying scammer and decoy audio
- High contrast stadium cards with status badges
- Live financial evidence ledger with one click copy
- Instant incident report preview and text file export
- Discreet configuration modal for custom backend tokens

---

## Quickstart

### Prerequisites
- Python 3.11 or newer
- Windows macOS or Linux

### 1. Installation
```bash
git clone https://github.com/chamanvashishth/Chakravyuh.git
cd Chakravyuh

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Run Test Suite
```bash
python run_tests.py
```
All 26 unit integration security and audio DSP tests pass locally with zero network calls.

### 3. Launch Local Server
```bash
python -m uvicorn chakravyuh.main:app --host 127.0.0.1 --port 8000 --reload
```
Open http://127.0.0.1:8000 in your browser. The console connects directly to the local backend.

---

## Configuration

Chakravyuh runs in development mode without authentication. To enable authentication in production set an environment variable:

```bash
# Windows PowerShell
$env:CHAKRAVYUH_API_KEY = "your-token"

# Linux and macOS
export CHAKRAVYUH_API_KEY="your-token"
```

When set endpoints require the X-API-Key header. You can also save this key inside the web console settings modal.

### Environment Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `CHAKRAVYUH_ALLOWED_ORIGINS` | `http://127.0.0.1:8000,http://localhost:8000` | Allowed web origins |
| `CHAKRAVYUH_ALLOW_ALL_ORIGINS` | `false` | Disable origin restrictions |
| `CHAKRAVYUH_API_KEY` | None | API authentication token |
| `CHAKRAVYUH_DB_PATH` | `./data/chakravyuh_honeypot.db` | SQLite database file path |
| `CHAKRAVYUH_HOST` | `127.0.0.1` | Network binding address |
| `CHAKRAVYUH_PORT` | `8000` | Server port |

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | System status and model registry |
| `GET` | `/api/v1/scenarios` | Preconfigured scam scenarios |
| `POST` | `/api/v1/sessions` | Create a new call session |
| `POST` | `/api/v1/sessions/{id}/turn` | Process dialogue and return decoy reply |
| `GET` | `/api/v1/sessions/{id}/dossier` | Return formal incident complaint |
| `POST` | `/api/v1/sessions/{id}/sip-merge` | Simulate SIP REFER telephone handover |
| `POST` | `/api/v1/threat-feed/check-transaction` | Screen account against flagged mules |
| `POST` | `/api/v1/threat-feed/broadcast/{id}` | Broadcast threat intelligence feed |
| `WS` | `/ws/call/{id}` | Real time telephone audio stream |

---

## Sample Incident Dossier

Every call engagement compiles an incident complaint for law enforcement and banks:

```json
{
  "dossier_id": "DOS-I4C-CHK-88F4A2",
  "incident_metadata": {
    "jurisdiction": "NCRP 1930 National Cybercrime Portal",
    "scam_category": "DIGITAL ARREST 98.4%",
    "suspect_caller_id": "+91 98204 71829",
    "claimed_authority": "CBI Cyber Crime Cell Mumbai and RBI Anti Money Laundering Unit",
    "time_wasted_sec": 240,
    "handover_mode": "AUTOMATED HONEYPOT TAKEOVER"
  },
  "extracted_iocs": [
    {
      "type": "UPI_VPA",
      "value": "cbi.escrow.mumbai@okaxis",
      "role": "Mule Payment Handle",
      "provider": "Axis Bank",
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
    "codec": "ITU-T G.711 PCMU 8000 Hz"
  },
  "recommended_actions": [
    "FREEZE MULE ACCOUNTS",
    "BLOCK UPI HANDLES ACROSS PSPS",
    "INITIATE 1930 NCRP FREEZE"
  ]
}
```

---

## Security Guardrails

- Ephemeral voice data: The reference clip is converted into a 768 dimension bfloat16 tensor. Raw audio is never saved.
- Cryptographic watermarking: Every synthesized turn contains a SHA256 signature to prevent misattribution.
- Defanged links: Malicious URLs are rendered safely without clickable triggers.
- Parameterized SQL: Database queries use parameterized bindings to prevent injection.
- HMAC verification: Threat intelligence feeds require HMAC-SHA256 signatures validated in constant time.

---

## Repository Layout

```text
chakravyuh/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Automated 26 test CI and GitHub Pages deploy
├── docs/
│   ├── index.html                 # Live Command Center console
│   ├── architecture.md            # Detailed technical specification
│   ├── qa-report.md               # 26 test verification report
│   ├── security-audit.md          # Threat model and security controls
│   └── .nojekyll                  # GitHub Pages Jekyll bypass
├── src/
│   └── chakravyuh/
│       ├── main.py                # FastAPI entrypoint
│       ├── config.py              # Configuration and settings
│       ├── api/                   # REST routes and WebSocket gateway
│       ├── asr/                   # Prisma 8kHz Butterworth ASR
│       ├── deception/             # Evon 6 stage deception engine
│       ├── dossier/               # Incident report compiler
│       ├── intelligence/          # Financial IOC extractor
│       ├── models/                # Schemas and data contracts
│       ├── static/                # Modern glassmorphism UI
│       ├── storage/               # SQLite WAL persistence
│       ├── telecom/               # G.711 mu law and SIP bridge
│       ├── threat_intel/          # NPCI STIX 3.0 fraud engine
│       └── voice/                 # Vachana 768 dim clone engine
├── tests/                         # 26 automated unit and integration tests
├── .gitignore
├── .nojekyll                      # Root GitHub Pages Jekyll bypass
├── index.html                     # Root entrypoint for branch hosting
├── Makefile
├── pyproject.toml
├── README.md
├── requirements.txt
└── run_tests.py
```

---

## License

Licensed under the Apache License Version 2.0. See [LICENSE](LICENSE) for details.
