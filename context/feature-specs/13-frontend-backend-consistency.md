# Feature Spec 13  -  Frontend-Backend Consistency & Hybrid Operation

## 1. Objective
Synchronize the Split-Screen Command Center UI (`src/chakravyuh/static/index.html`) with the FastAPI backend REST and WebSocket APIs, enabling real live interaction while preserving standalone offline demonstration capability.

## 2. Existing Architecture Context
Currently, `index.html` runs purely client-side simulation with 250+ lines of duplicated JavaScript regex and state-machine logic. When served from `GET /` on the FastAPI server, it never sends HTTP requests or connects to `/ws/call/{session_id}`.

## 3. Dependencies
- Web technologies: Vanilla JS (ES6+), HTML5 Canvas, Web Audio API, Tailwind CSS CDN
- Backend endpoints: `GET /api/v1/health`, `POST /api/v1/sessions`, `POST /api/v1/sessions/{id}/turn`, `WS /ws/call/{session_id}`

## 4. Exact Files in Scope
- `src/chakravyuh/static/index.html`
- `tests/test_integration_api_and_ws.py`

## 5. Required Behavior
1. **Auto-Detection of Backend Gateway**:
   - On load, probe `GET /api/v1/health` with a short timeout (1500 ms).
   - If reachable: Set `state.liveBackendConnected = true`, display `"⚡ LIVE BACKEND CONNECTED"`, and initialize an active session via `POST /api/v1/sessions`.
   - If unreachable (standalone demo or file:/// URI): Gracefully fall back to client-side simulation (`state.liveBackendConnected = false`), displaying `"OFFLINE SIMULATION DEMO"`.
2. **Dual-Mode Turn Processing**:
   - In Live Mode: Submit scammer turns via `POST /api/v1/sessions/{session_id}/turn` (or WebSocket). Update UI state directly from the backend's `TurnProcessingResponse` (extracted IOCs, deception stage, synthesized voice WAV, and I4C dossier).
   - In Offline Mode: Continue running client-side simulated turn generator as a fallback.
3. **Phishing Containment**:
   - Ensure all rendered IOC URLs, APK download links, and scammer payloads are escaped and defanged (`textContent` / inert spans, never raw clickable `<a>` tags with malicious hrefs).

## 6. Security Constraints
- Zero XSS vulnerability from scammer-controlled strings.
- Defanged URLs: render `hxxps://` or plain text without hyperlink activation.

## 7. Edge Cases
- Network drop mid-call transitions seamlessly without crashing the UI.
- Browser audio autoplay restrictions handled via user gesture.

## 8. Tests
- TestClient verification that `GET /` returns HTML containing live backend connection hooks.
- Integration test simulating REST turn processing matching frontend data models.

## 9. Acceptance Criteria
- Running server and opening UI connects to the live backend.
- When running standalone without server, UI continues to work.
- Zero dead buttons; all tabs functional.

## 10. Explicit Exclusions
- Introducing large JavaScript frameworks (React/Vue/Angular)  -  Ponytail minimalist single-file HTML preserved.

## 11. Definition of Done
- Dual-mode connection logic implemented in `src/chakravyuh/static/index.html`.
- Verified in browser or automated test.

