# Feature Spec 06  -  FastAPI REST & WebSocket Duplex Streaming Gateway

## 1. Objective
Expose Chakravyuh's complete capabilities over a production-grade FastAPI REST API and full-duplex WebSocket streaming endpoint (`/ws/call/{session_id}`).

## 2. Context & Dependencies
- Depends on: `fastapi`, `starlette.websockets`, `src/chakravyuh/voice`, `src/chakravyuh/asr`, `src/chakravyuh/deception`, `src/chakravyuh/intelligence`, `src/chakravyuh/dossier`, `src/chakravyuh/storage`.

## 3. Exact Implementation Scope
- `src/chakravyuh/api/__init__.py`
- `src/chakravyuh/api/routes.py`
- `src/chakravyuh/main.py`

## 4. Required Endpoints & Contracts
- `GET /api/v1/health`: Returns system status, active models (`vachana-vc-v1`, `Prisma v2.5`, `Evon v3.3`), and tensor specification (`[1, 768] torch.bfloat16`).
- `POST /api/v1/sessions`: Initiates a call handover session, runs `vachana-vc-v1` on the 10-second reference clip, stores the `[1, 768]` `bfloat16` embedding, and returns session details.
- `GET /api/v1/sessions/{session_id}`: Retrieves session state, transcript history, and extracted IOCs.
- `POST /api/v1/sessions/{session_id}/turn`: Processes a scammer turn (audio base64 or text) through `Prisma v2.5` -> `IOCExtractor` -> `Evon v3.3` -> `vachana-vc-v1` -> `I4CDossierCompiler` and returns the complete turn response + updated dossier.
- `POST /api/v1/sessions/{session_id}/simulate-scenario`: Runs or steps through a built-in hackathon scenario (`DIGITAL_ARREST`, `FEDEX_PARCEL`, `KYC_BANK_FRAUD`).
- `GET /api/v1/sessions/{session_id}/dossier`: Returns the structured I4C FIR Dossier JSON and formatted legal FIR report.
- `GET /api/v1/threat-feed`: Phase 3 Live Threat Intelligence API returning flagged mule UPI IDs and bank accounts for fintech fraud engines.
- `WS /ws/call/{session_id}`: Real-time duplex WebSocket accepting `{"type": "scammer_turn", "text": "...", "audio_b64": "..."}` or `{"type": "next_scenario_step"}` and streaming back `prisma_asr_telemetry`, `ioc_alert`, `evon_deception_reply`, `vachana_vc_audio`, and `dossier_update` events.

## 5. Acceptance Criteria & Definition of Done
- All REST and WebSocket endpoints pass `fastapi.testclient.TestClient` integration tests with `200 OK` and valid schema payloads.
