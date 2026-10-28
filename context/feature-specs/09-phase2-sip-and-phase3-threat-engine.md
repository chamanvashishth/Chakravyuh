# Feature Spec 09  -  Phase 2 SIP/WebRTC Bridge & Phase 3 NPCI Fraud Engine API

## 1. Objective
Upgrade Phase 2 (SIP/WebRTC Call Forwarding & Merge Bridge) and Phase 3 (Live Fintech / NPCI Fraud Engine API) from static dossier metadata into active, stateful backend microservices and interactive UI controls.

## 2. Context & Dependencies
- Depends on: `src/chakravyuh/models/schemas.py`, `src/chakravyuh/api/routes.py`, `src/chakravyuh/storage/database.py`.

## 3. Exact Implementation Scope
- `src/chakravyuh/telecom/__init__.py`
- `src/chakravyuh/telecom/sip_webrtc_bridge.py`
- `src/chakravyuh/threat_intel/__init__.py`
- `src/chakravyuh/threat_intel/npci_fraud_engine.py`
- `src/chakravyuh/api/routes.py`
- `tests/test_phase2_and_phase3_services.py`
- `artifacts/file_generation/ttl=63d/output/chakravyuh_command_center.html`

## 4. Required Behavior
1. **Phase 2 SIP/WebRTC Call Merge Bridge (`SIPWebRTCBridgeService`)**:
   - Generates RFC 3261 / 3GPP TS 24.229 compliant `SIP INVITE`, `SIP 200 OK`, and `SIP REFER` signaling dialogs with SDP (`v=0`, `m=audio ... RTP/AVP 0`, `a=rtpmap:0 PCMU/8000/1`).
   - Implements ITU-T G.711 $\mu$-law (`PCMU/8000`) 8-bit logarithmic audio compression and decompression (`encode_pcm16_to_ulaw` and `decode_ulaw_to_pcm16`) for 8 kHz PSTN carrier RTP packets.
   - Manages victim line mute state (`VICTIM_MUTED_AT_IMS_BRIDGE`) so the human victim can stay on the merged call silently while `vachana-vc-v1` speaks to the scammer.
   - Exposed via `POST /api/v1/sessions/{session_id}/sip-merge`.
2. **Phase 3 Live Threat Feed & Fintech Fraud Engine (`NPCIFraudEngineService`)**:
   - Provides a real-time pre-transaction screening endpoint (`POST /api/v1/threat-feed/check-transaction`) where any UPI PSP (GPay, PhonePe, Paytm) or bank IMPS switch can query a beneficiary VPA, bank account number, or IFSC code before executing a transfer.
   - Returns `BLOCK_TRANSACTION` (`risk_score=99.0`, `reason="FLAGGED_BY_CHAKRAVYUH_HONEYPOT"`, `dossier_id`, `scam_category`) if the recipient matches any extracted mule IOC, or `ALLOW_TRANSACTION` (`risk_score=5.0`) if clean.
   - Provides `POST /api/v1/threat-feed/broadcast/{session_id}` to dispatch signed HMAC-SHA256 webhook alerts to registered fintech endpoints.

## 5. Acceptance Criteria & Definition of Done
- G.711 $\mu$-law encode/decode round-trip preserves 8 kHz telephonic waveform correlation `> 0.99`.
- `POST /api/v1/sessions/{session_id}/sip-merge` returns valid SIP `REFER` dialog + SDP and updates session state.
- `POST /api/v1/threat-feed/check-transaction` blocks transactions to extracted mule UPIs/bank accounts and allows clean handles.
