# Feature Spec 07  -  Interactive Split-Screen Command Center Web App

## 1. Objective
Build a self-contained, single-file interactive Web Application (`chakravyuh_command_center.html`) that delivers the **60-Second Split-Screen Hackathon Demo** directly in Canvas (and via the FastAPI server), complete with synthesized Hinglish voice audio via Web Audio API, live dual-channel 8 kHz waveform oscilloscope, interactive `[1, 768] torch.bfloat16` speaker-embedding tensor inspector, custom scammer utterance injector, and live I4C / 1930 FIR Dossier builder.

## 2. Context & Dependencies
- Follows `system:web-app-generation` rules strictly: single self-contained `.html` file, Tailwind CSS CDN (`https://cdn.tailwindcss.com/3.4.17`), zero broken links, zero `alert()`/`confirm()`/`prompt()`, `try/catch` around `localStorage`, and verified with `scripts/check_web_app.py`.

## 3. Exact Implementation Scope
- `src/chakravyuh/static/index.html`

## 4. Required Interactive Capabilities
1. **3 Complete Hinglish Scam Scenarios**:
   - *Digital Arrest (CBI / Mumbai Police Narcotics Warrant)*
   - *Fake FedEx International Contraband Parcel*
   - *Urgent SBI KYC & Electricity Disconnection Scam*
2. **1-Click "Hand Over to Honeypot" + Auto-Play 60s Demo + Manual Step & Custom Scammer Input**:
   - Users can click **"Hand Over to Honeypot (Auto-Demo)"** to watch the split-screen takeover unfold automatically with real-time Web Audio API voice synthesis, or step turn-by-turn, or type any custom scammer message containing arbitrary UPI IDs (`scammer@ybl`), Bank Account Numbers, IFSCs (`HDFC0001234`), phone numbers, or URLs.
3. **Real-Time Dual Oscilloscope (`<canvas>`)**:
   - Renders incoming 8 kHz telephonic scammer audio (Rose) vs. `vachana-vc-v1` cloned anxious user voice decoy (Emerald).
4. **Live I4C / 1930 Cybercrime FIR Dossier & Export**:
   - Updates instantaneously on every turn as mule UPI IDs, secondary backup UPI handles, bank accounts, and IFSC codes are extracted.
   - Includes **Copy FIR JSON**, **Download Official FIR Dossier (`.txt` / `.json`)**, **Inspect `[1, 768] bfloat16` Tensor Heatmap**, and **Broadcast to Phase-3 NPCI Fintech Threat Feed**.

## 5. Acceptance Criteria & Definition of Done
- Passes `python3 skills/web-app-generation/scripts/check_web_app.py` with `0` errors and `0` warnings.
- Every button, tab, scenario switcher, audio synthesizer toggle, and custom input works deterministically.
