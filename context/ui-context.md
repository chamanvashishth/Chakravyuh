# UI Context  -  Chakravyuh Split-Screen Command Center

## 1. Visual Identity & Aesthetic Direction
- **Theme**: Tactical Cybersecurity Operations Center (SOC) ("Offensive Cyber Defense").
- **Color Palette**:
  - Background Primary: `#070B14` (Deep Tactical Obsidian)
  - Background Secondary / Cards: `#0F172A` (Slate 900 with `1px solid rgba(56, 189, 248, 0.18)` border)
  - Accent Primary (Active Honeypot / Vachana Voice Clone): `#10B981` (Emerald 500  -  Cyber Defense Active)
  - Accent Secondary (Prisma / Evon Telemetry): `#38BDF8` (Sky 400  -  Neural Pipeline Telemetry)
  - Alert / Scammer Threat Indicator: `#F43F5E` (Rose 500  -  High-Risk Scammer / Mule IOC Extracted)
  - Warning / Stall State: `#F59E0B` (Amber 500  -  UPI Lag / Bank Limit Baiting State)
  - Text Primary: `#F8FAFC` (Slate 50)
  - Text Secondary: `#94A3B8` (Slate 400)
- **Typography**:
  - Primary UI Font: `Inter`, system sans-serif
  - Telemetry / Tensor / IOC / FIR Dossier Font: `JetBrains Mono` / `Fira Code`, monospace

## 2. Split-Screen Layout Architecture
- **Top Tactical Header Bar**:
  - Brand Identity: **CHAKRAVYUH** (`v1.0` badge) + Subtitle: *Active Voice-Clone Honeypot (`vachana-vc-v1` + `Prisma v2.5` + `Evon v3.3`)*
  - Scenario Preset Selector:
    1. **Scenario 1: "Digital Arrest" CBI/Narcotics Scam** (Mumbai Police / RBI Verification Account)
    2. **Scenario 2: Fake FedEx Customs Contraband Parcel** (Taiwan Parcel / Narcotics Clearance)
    3. **Scenario 3: Urgent SBI/PAN KYC & Electricity Disconnection Scam** (APK / Secondary UPI Bait)
  - Live Pipeline Status Pill (`IDLE` -> `CALL INTERCEPTED` -> `VOICE DECOY ACTIVE` -> `DOSSIER READY`)
  - Audio Synthesizer Mute/Unmute Toggle (Web Audio API real-time dual-tone & speech prosody synthesizer)
- **Left Pane (50% Desktop Width): Victim Phone Handover & Live Duplex Audio Intercept**:
  - **Call Handover Card**: Displays incoming caller ID (e.g., `+91 98204-71829 [Spoofed: CBI HQ / FedEx India]`), scam confidence gauge (`98.4% Digital Arrest Pattern`), 10-second User Voice Reference status (`[1, 768] torch.bfloat16 Tensor Locked`), and the prominent **"HAND OVER TO HONEYPOT"** action button (plus automated scenario play & step-turn controls).
  - **Dual-Channel Oscilloscope Waveform Canvas**: Real-time 60fps HTML5 `<canvas>` rendering both the `8 kHz` incoming scammer audio waveform (Rose `#F43F5E`) and the `vachana-vc-v1` cloned decoy voice waveform (Emerald `#10B981`).
  - **Live Hinglish Conversation Stream**: Chat-style timestamped transcript showing Scammer threats vs. `Evon v3.3` + `vachana-vc-v1` anxious Hinglish responses, with inline badges showing which tactical stall (`UPI_SERVER_BUSY_U16`, `DAILY_LIMIT_EXCEEDED_RTGS_BAIT`, `OTP_LAG_SUPERVISOR_BAIT`) triggered each reply.
  - **Custom Scammer Input Box**: Allows operators to inject custom scammer turns (including test UPI IDs or bank accounts) and observe the engine's real-time extraction and defensive counter-turns.
- **Right Pane (50% Desktop Width): Real-Time Intelligence Extraction & I4C / FIR Dossier**:
  - **Model Telemetry Strip**:
    - `vachana-vc-v1`: Shape `[1, 768]` | Precision `torch.bfloat16` (`1536 bytes`) | Cosine Sim `0.994` | Latency `38 ms`
    - `Prisma v2.5`: `8000 Hz` PSTN Bandpass (`300-3400 Hz`) | VAD Active
    - `Evon v3.3`: Current Deception State badge & Scam Time Wasted timer
  - **Extracted Mule IOCs Grid**: Live cards for **Mule UPI IDs**, **Bank Account Numbers + IFSC**, **Scammer Phone/WhatsApp Numbers**, and **Phishing URLs / Fake Badges**, each with confidence score, bank name resolution, and NPCI freeze status.
  - **Tabbed Inspector**:
    - **Tab 1: Live I4C / 1930 Cybercrime FIR Dossier** (Structured official report with one-click Copy JSON, Download FIR Report `.json`/`.txt`, and Broadcast to Phase-3 Fintech Threat Feed).
    - **Tab 2: `vachana-vc-v1` `[1, 768]` `bfloat16` Tensor Inspector** (Interactive heatmap + hex/bfloat16 slice viewer of the user's 10-second reference voice embedding and 10s reference re-calibration button).
    - **Tab 3: Phase 2 (SIP/WebRTC Trunk) & Phase 3 (NPCI/Fintech Threat API) Live Console** (Shows live SIP `INVITE` / `REFER` SDP packet inspection and live webhook payloads dispatched to fintech fraud engines).
