# Feature Spec 14  -  Observability, Structured Logging & Error Management

## 1. Objective
Establish centralized structured logging, request correlation IDs, standardized error schemas, and robust WebSocket lifecycle management across the Chakravyuh FastAPI gateway.

## 2. Existing Architecture Context
Currently, errors in `routes.py` and `database.py` print to standard output or raise basic HTTPExceptions. WebSocket disconnections catch `WebSocketDisconnect` without session cleanup or audit telemetry.

## 3. Dependencies
- Standard library: `logging`, `uuid`, `time`, `json`
- Installed libraries: `fastapi`, `starlette`

## 4. Exact Files in Scope
- `src/chakravyuh/api/routes.py`
- `src/chakravyuh/main.py`
- `tests/test_integration_api_and_ws.py`

## 5. Required Behavior
1. **Correlation ID & Middleware**:
   - Add a lightweight request-id middleware injecting `X-Request-ID` into every HTTP response header.
2. **Standardized Error Responses**:
   - Ensure all `HTTPException` and validation errors follow a uniform JSON schema: `{"detail": str, "error_code": str, "request_id": str, "timestamp": str}`.
3. **WebSocket Lifecycle & Disconnect Resilience**:
   - Clean up active session caches upon client disconnection.
   - Guard against malformed JSON messages with structured error frames before closing.

## 6. Security Constraints
- Do not log sensitive victim reference audio bytes or unencrypted passwords in server logs.

## 7. Edge Cases
- Client drops WebSocket during mid-turn synthesis without completing handshake.
- Malformed binary frame sent to JSON WebSocket.

## 8. Tests
- Verify `X-Request-ID` header exists on HTTP responses.
- Verify structured error JSON schema on 404 and 422 errors.
- Verify WebSocket cleanly closes on malformed JSON without raising unhandled server crash.

## 9. Acceptance Criteria
- Full 19 regression tests pass.
- New observability tests pass.

## 10. Explicit Exclusions
- External Prometheus/Grafana or ELK agent dependencies (Ponytail standard-library logging).

## 11. Definition of Done
- Middleware and error handlers in place; tests passing.

