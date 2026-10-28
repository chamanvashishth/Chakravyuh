# Feature Spec 15  -  External Integration Contracts & Protocol Verification

## 1. Objective
Formalize the exact interface boundaries, data contracts, and protocol schemas for Phase 2 (SIP/WebRTC PSTN Carrier Bridge) and Phase 3 (NPCI / Fintech Fraud Engine Webhooks), explicitly distinguishing high-fidelity protocol simulation from authorized live carrier and banking connectivity.

## 2. Existing Architecture Context
`src/chakravyuh/telecom/sip_webrtc_bridge.py` compands G.711 mu-law audio and generates RFC 3261/3515 text signaling. `src/chakravyuh/threat_intel/npci_fraud_engine.py` provides pre-transaction screening and HMAC-SHA256 signed STIX-3.0 bundle generation.

## 3. Dependencies
- Standard library: `hashlib`, `hmac`, `json`
- Internal modules: `chakravyuh.telecom.sip_webrtc_bridge`, `chakravyuh.threat_intel.npci_fraud_engine`

## 4. Exact Files in Scope
- `src/chakravyuh/telecom/sip_webrtc_bridge.py`
- `src/chakravyuh/threat_intel/npci_fraud_engine.py`
- `tests/test_phase2_and_phase3_services.py`

## 5. Required Behavior
1. **RFC 3261 / 3515 SIP Contract Compliance**:
   - Validate generated `SIP REFER` message headers: `Refer-To`, `Referred-By`, `CSeq`, `Call-ID`, `Content-Type: application/sdp`.
   - Validate SDP session description: `v=0`, `c=IN IP4 ...`, `m=audio ... RTP/AVP 0`, `a=rtpmap:0 PCMU/8000/1`.
2. **STIX-3.0 / NPCI Threat Bundle Compliance**:
   - Validate JSON schema of the signed STIX-3.0 bundle: `id`, `spec_version`, `indicators`, `npci_directive`.
   - Verify HMAC-SHA256 signature verification helper.
3. **Transparent Architectural Boundary**:
   - Clear docstrings identifying simulated interfaces vs live carrier prerequisites (SIP proxy URI, IMS credentials, TLS mutual auth).

## 6. Security Constraints
- Secret key for HMAC-SHA256 signing configurable via environment (`NPCI_WEBHOOK_SECRET`).
- Defend against replay attacks by including UTC timestamp and checking expiry (< 300s).

## 7. Edge Cases
- Session with zero extracted IOCs generating an empty STIX bundle.
- Signature verification with invalid or altered payload bytes.

## 8. Tests
- Validate HMAC signature verification succeeds for untampered bundles and fails for tampered bytes.
- Verify SDP parser validates required G.711 attributes.

## 9. Acceptance Criteria
- All Phase 2 & 3 tests pass.
- Contract validation and HMAC verification verified.

## 10. Explicit Exclusions
- Uncertified carrier live trunking or mock banking clearing switches.

## 11. Definition of Done
- Contracts formalized and tested.

