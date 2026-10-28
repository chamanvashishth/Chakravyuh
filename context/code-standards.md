# Code Standards  -  Chakravyuh Engineering Standards

## 1. Language & Runtime Conventions
- **Python Version**: Python 3.11+ (`3.11.2` verified in environment).
- **Formatting & Style**: PEP 8 compliant, 4-space indentation, explicit type annotations across all function signatures and return values (`typing` module: `List`, `Dict`, `Optional`, `Tuple`, `Any`, `Union`).
- **Pydantic Compatibility**: The environment runs `pydantic==1.10.4` and `fastapi==0.92.0`. Always use Pydantic v1 syntax (`BaseModel`, `Field`, `.dict()`, `@validator`) rather than Pydantic v2-only methods (`.model_dump()`), or provide compatibility wrappers so both v1 and v2 environments work seamlessly.

## 2. Module Organization
```
src/chakravyuh/
├── __init__.py
├── config.py                  # Centralized environment & model hyperparameter config
├── main.py                    # FastAPI application entrypoint & ASGI lifecycle
├── models/
│   ├── __init__.py
│   └── schemas.py             # Pydantic schemas for sessions, turns, IOCs, embeddings, dossiers
├── voice/
│   ├── __init__.py
│   └── vachana_vc.py          # vachana-vc-v1 [1, 768] bfloat16 speaker embedding & decoy synthesizer
├── asr/
│   ├── __init__.py
│   └── prisma_asr.py          # Prisma v2.5 8kHz telephonic DSP, VAD, and scam classifier
├── deception/
│   ├── __init__.py
│   └── evon_agent.py          # Evon v3.3 Hinglish state machine & scenario scripts
├── intelligence/
│   ├── __init__.py
│   └── ioc_extractor.py       # Regex + contextual UPI, Bank Account, IFSC, Phone, URL extractor
├── dossier/
│   ├── __init__.py
│   └── i4c_compiler.py        # I4C / 1930 Cybercrime FIR Dossier builder & threat feed formatter
├── storage/
│   ├── __init__.py
│   └── database.py            # SQLite3 WAL-mode repository
└── api/
    ├── __init__.py
    └── routes.py              # REST endpoints + WebSocket /ws/call/{session_id} handler
```

## 3. Error Handling & Resilience
- Never use bare `except:` blocks. Catch specific exceptions (`ValueError`, `KeyError`, `sqlite3.Error`, `WebSocketDisconnect`).
- Return structured JSON error responses (`{"detail": "...", "error_code": "..."}`) with appropriate HTTP status codes (`400`, `404`, `422`, `500`).
- Ensure WebSocket connections clean up active session locks gracefully upon client disconnect.

## 4. Testing Standards
- Use Python's built-in `unittest` together with `fastapi.testclient.TestClient` for synchronous and WebSocket endpoint verification.
- Every core subsystem (`vachana-vc-v1`, `Prisma v2.5`, `Evon v3.3`, `IOCExtractor`, `I4CDossierCompiler`, `SQLiteRepository`, and `FastAPI/WebSocket`) must have dedicated, deterministic tests in `tests/`.
- Tests must use isolated temporary SQLite databases (`tempfile.NamedTemporaryFile` or `:memory:`) so test runs are repeatable and side-effect free.
