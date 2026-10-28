# Feature Spec 10  -  Production Security Hardening & CORS Governance

## 1. Objective
Harden the Chakravyuh FastAPI gateway against cross-origin data leakage and unauthorized access by implementing configurable CORS origin controls and optional API Key authentication for sensitive threat intelligence and session control endpoints.

## 2. Existing Architecture Context
Currently, `src/chakravyuh/main.py` configures `CORSMiddleware` with `allow_origins=["*"]`, exposing all endpoints to any origin. Furthermore, `src/chakravyuh/api/routes.py` has no authentication layer, allowing unauthenticated network actors to read confidential I4C dossiers and query the live threat feed.

## 3. Dependencies
- Standard library: `os`, `typing`
- Installed dependencies: `fastapi`, `pydantic`
- Internal modules: `chakravyuh.config`, `chakravyuh.main`, `chakravyuh.api.routes`

## 4. Exact Files in Scope
- `src/chakravyuh/config.py`
- `src/chakravyuh/main.py`
- `src/chakravyuh/api/routes.py`
- `tests/test_security_and_edge_cases.py`

## 5. Required Behavior
1. **Configurable CORS Allowlist**:
   - `ChakravyuhConfig` reads `CHAKRAVYUH_ALLOWED_ORIGINS` (comma-separated list).
   - Default value: `http://localhost:8000,http://127.0.0.1:8000`.
   - Wildcard `*` is disallowed unless explicitly enabled by setting `CHAKRAVYUH_ALLOW_ALL_ORIGINS=true` in development.
2. **Optional API Key / Header Authentication**:
   - `ChakravyuhConfig` reads `CHAKRAVYUH_API_KEY` (string or None).
   - When set, endpoints mutating sessions (`POST /api/v1/sessions`, `/turn`, `/sip-merge`) or accessing sensitive intelligence (`/api/v1/sessions/{id}/dossier`, `/api/v1/threat-feed/*`) require an `X-API-Key` header matching the configured key.
   - Public inspection endpoints (`GET /api/v1/health`, `GET /api/v1/scenarios`, `GET /`) remain accessible without credentials.
   - When `CHAKRAVYUH_API_KEY` is empty/unset (default for local development and tests), authentication is disabled to preserve backward compatibility with existing tests.

## 6. Security Constraints
- Constant-time comparison (`secrets.compare_digest`) for API key verification to prevent timing attacks.
- Untrusted origins must receive 400/403 or disallowed CORS responses.

## 7. Edge Cases
- Empty or whitespace origins in `CHAKRAVYUH_ALLOWED_ORIGINS` are stripped.
- Invalid or missing `X-API-Key` returns `401 Unauthorized` with structured JSON detail `{"detail": "Invalid or missing API Key", "error_code": "AUTH_REQUIRED"}`.

## 8. Tests
- Verify unauthorized origin does not receive `Access-Control-Allow-Origin: *`.
- Verify configured origin receives appropriate CORS header.
- Verify setting `CHAKRAVYUH_API_KEY` blocks unauthenticated calls with `401` on protected routes.
- Verify setting `CHAKRAVYUH_API_KEY` allows calls with matching `X-API-Key`.
- Verify `GET /api/v1/health` remains open.

## 9. Acceptance Criteria
- Full 19 baseline tests continue to pass without regression.
- New security tests verify CORS restriction and API Key enforcement.

## 10. Explicit Exclusions
- Full OAuth2/OIDC/JWT identity provider integrations (out of scope for standalone honeypot node).

## 11. Definition of Done
- Code implemented in `config.py`, `main.py`, and `routes.py`.
- Unit tests added to `tests/test_security_and_edge_cases.py`.
- All tests pass cleanly.

