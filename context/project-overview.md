# Project Overview  -  Chakravyuh: Active Voice-Clone Honeypot for Scam Calls

## 1. Executive Summary
**Chakravyuh** is an offensive cybersecurity defense system designed to counter Indian telephonic financial fraud ("Digital Arrest" CBI/Customs impersonation, fake FedEx/DHL narcotics parcel scams, and urgent KYC/electricity disconnection scams). Unlike passive caller-ID warning banners that merely alert a user and leave the scammer free to dial the next victim, Chakravyuh actively takes over the suspicious call using real-time voice cloning (`vachana-vc-v1`), wastes the scammer's operational bandwidth, and socially engineers the scammer into revealing multiple mule bank accounts, UPI IDs, and phishing infrastructure while automatically compiling a structured **I4C (Indian Cyber Crime Coordination Centre) / Cybercrime FIR Dossier**.

## 2. Problem Statement
1. **Passive Defenses Fail at Deterrence**: Existing caller-ID apps only flag known numbers. Scammers rotate VoIP/SIP numbers every few hours, rendering static blocklists ineffective.
2. **High-Pressure Psychological Coercion**: In "Digital Arrest" and "FedEx Parcel" scams, perpetrators keep victims on video/voice calls for hours under threat of immediate arrest, coercing RTGS/NEFT/UPI transfers to multi-layered mule accounts.
3. **Lack of Actionable Financial Intelligence**: Even when a user hangs up on a scammer, law enforcement (1930 Helpline / `cybercrime.gov.in`) receives zero actionable intelligence about the scammer's active receiving mule UPI IDs or bank accounts unless money was already lost.

## 3. Target Operational Users
- **Telecom & Anti-Fraud Operations**: Telecom carriers and anti-fraud engineering teams deploying automated call interception and scam mitigation pipelines.
- **Law Enforcement Agencies**: Indian Cyber Crime Coordination Centre (I4C), State Cyber Crime Cells, and 1930 Helpline analysts requiring structured FIR dossiers with forensic evidence.
- **Financial Institutions**: Fintechs, payment gateways, and banking security engines consuming real-time Indicator of Compromise (IOC) feeds to freeze mule accounts pre-transaction.

## 4. Goals & Measurable Success Criteria
| Metric | Target | Verification Method |
| :--- | :--- | :--- |
| **Speaker Embedding Tensor Specification** | Exact `[1, 768]` tensor in `bfloat16` precision from a 10-second reference clip | Unit test assertion on shape `(1, 768)`, dtype/bit-pattern (`bfloat16`), and L2-normalized cosine similarity |
| **Telephonic Audio Ingestion** | 8 kHz (`8000 Hz`) mono PCM / mu-law audio stream processing | Unit & integration test verifying 8 kHz frame ingestion and resampling |
| **IOC Extraction Recall & Precision** | ≥ 95% extraction accuracy across UPI IDs (`@ybl`, `@okaxis`, etc.), 9-18 digit Bank Accounts, IFSC codes (`^[A-Z]{4}0[A-Z0-9]{6}$`), phone numbers, and phishing URLs | Automated test suite against realistic Hinglish scam transcripts |
| **Deception Stall Escalation** | Multi-turn state transitions that force scammers to reveal secondary/backup mule accounts after simulated primary UPI failure | State machine integration tests across Digital Arrest, FedEx, and KYC scenarios |
| **Dossier Completeness** | Auto-populated I4C / FIR JSON + printable report within < 100ms of call termination or live turn | API contract & schema validation tests |

## 5. Core Honeypot Capabilities
1. **1-Click Call Handover**: Seamless transition from "Incoming Suspected Scam Call" to active AI Honeypot takeover (`HANDOVER_INITIATED` -> `ACTIVE_ENGAGEMENT`).
2. **Voice Decoy (`vachana-vc-v1`)**: Extracts a `[1, 768]` `bfloat16` speaker embedding from the user's 10-second reference audio clip and synthesizes anxious, compliant Hinglish voice responses streamed over WebSockets.
3. **8 kHz Telephonic Transcription (`Prisma v2.5`)**: Ingests 8 kHz scammer audio frames, performs voice activity detection (VAD) and telephonic acoustic normalization, and outputs timestamped Hinglish transcripts with scam-category classification.
4. **Tactical Deception Engine (`Evon v3.3`)**: Implements a finite state machine (`COMPLIANT_ANXIOUS` -> `PAYMENT_ATTEMPT_STALL` -> `PRIMARY_UPI_SERVER_ERROR` -> `SECONDARY_MULE_BAIT` -> `BANK_LIMIT_EXCEEDED_RTGS_BAIT`) designed specifically to make scammers divulge backup UPI IDs and full bank account + IFSC details.
5. **Real-Time IOC & I4C Dossier Generator**: Extracts, deduplicates, and risk-scores UPI handles, bank account numbers, IFSC codes, aliases, and phishing links in real time, formatting an official I4C-compatible Cybercrime FIR JSON/Report.
6. **Split-Screen Command Center UI**: Interactive web application showing the Victim Call Handover & Hinglish Audio Waveform on the left, and the Live Threat Intelligence / I4C Dossier & Model Telemetry (`[1, 768] bfloat16` embedding inspector, WebSocket stream, IOC cards) on the right.

## 6. Scope & Exclusions
- **In Scope (Core Subsystems)**: Complete Python backend (`FastAPI` + WebSockets + SQLite), `vachana-vc-v1` `[1, 768]` `bfloat16` embedding & synthesis pipeline, `Prisma v2.5` 8 kHz telephonic processor, `Evon v3.3` Hinglish deception engine, regex + contextual IOC extractor, I4C FIR dossier generator, Phase 3 Threat Feed REST API preview, and a self-contained Split-Screen Interactive Command Center WebApp with synthesized Hinglish audio playback.
- **Out of Scope (Future Roadmap)**:
  - *Phase 2*: Live carrier-grade SIP/WebRTC SS7 trunk bridging with telecom operators (Jio/Airtel)  -  architectural hooks and SIP SDP payload generators are included, but live PSTN carrier trunking is excluded due to telecom regulatory licensing.
  - *Phase 3*: Direct production write-access to NPCI's internal production switches  -  represented via a documented, authenticated Threat Intelligence Webhook/REST feed.

## 7. Technology Stack Decisions
- **Backend Framework**: Python 3.11 + `FastAPI` + `Starlette` WebSockets (`uvicorn` ASGI server). Chosen for native asynchronous full-duplex WebSocket streaming and strict `Pydantic` schema contracts.
- **Numerical & Signal Processing**: `NumPy` + `SciPy` (`scipy.signal` for 8 kHz butterworth band-pass filtering `[300Hz - 3400Hz]`, spectral feature extraction, and exact IEEE-754 `bfloat16` `[1, 768]` tensor projection).
- **Persistence**: `SQLite3` with WAL (Write-Ahead Logging) mode for zero-configuration, ACID-compliant persistence of call sessions, transcript turns, extracted IOCs, and I4C dossiers.
- **Frontend Demo UI**: Single-file responsive HTML5 / Tailwind CSS / Web Audio API + Canvas 2D waveform visualizer (`chakravyuh_command_center.html`) capable of running standalone in Canvas or connected to the FastAPI WebSocket backend.
