# Security & Privacy Audit Report  -  Chakravyuh v1.0.0

## 1. Threat Model & Security Posture
Because **Chakravyuh** processes adversarial input from active cybercriminals (voice streams, phishing URLs, malicious `.apk` links, and crafted text strings) and utilizes voice-cloning technology (`vachana-vc-v1`), the architecture enforces strict defensive boundaries across four domains:

### 1.1 Voice Cloning Ethics, Consent & Non-Repudiation
- **Ephemeral Reference Audio**: The 10-second user reference clip is immediately transformed into a `[1, 768]` `torch.bfloat16` speaker-embedding tensor (`1536 bytes`). Raw victim reference audio is not persisted to the database.
- **Cryptographic Frame Watermarking**: Every synthesized voice packet emitted by `vachana-vc-v1` computes a SHA-256 watermark binding `(speaker_embedding_bfloat16_bytes || reply_text || wav_pcm_header)`. This digest is logged in the I4C FIR Dossier (`voice_clone_audit.embedding_sha256`), ensuring forensic investigators can provably distinguish AI honeypot decoy turns from human victim statements.

### 1.2 Injection & Malicious Payload Containment
- **SQL Injection Prevention**: Verified in `tests/test_security_and_edge_cases.py`. Every SQLite statement in `src/chakravyuh/storage/database.py` uses parameterized `?` bindings exclusively.
- **Defanged Phishing & APK Artifacts**: Extracted phishing URLs (`https://...` and `.apk` droppers) are rendered strictly as inert text inside the Command Center UI and I4C FIR Dossier (`textContent` / escaped strings) so an operator or judge cannot accidentally trigger a malicious link.
- **Input Size & DoS Bounds**: `TurnInputRequest` enforces `min_length=1`, `max_length=4096`, and strips whitespace-only payloads (`HTTP 422`), preventing regex catastrophic backtracking (ReDoS) or memory exhaustion.

### 1.3 Data Storage & Journal Resilience
- SQLite connections negotiate `WAL` or `MEMORY` journaling cleanly with thread-safe `RLock` synchronization, preventing database corruption under concurrent WebSocket streams.
- Persistent database path defaults to durable local storage (`data/chakravyuh_honeypot.db`) rather than ephemeral `/tmp`, with automatic directory initialization and safe online backup snapshotting via `backup_database()`.

### 1.4 CORS Governance & Gateway Boundaries
- Evaluated and remediated in Unit 10: The application gateway strictly enforces configured origin allowlists via `CHAKRAVYUH_ALLOWED_ORIGINS` (defaulting to local origins `http://localhost:8000`, `http://127.0.0.1:8000`). Wildcard `*` is explicitly disabled in production mode, blocking cross-origin reconnaissance attacks.

### 1.5 Authentication & Threat Intelligence Non-Repudiation
- Optional API Key / Bearer authentication (`X-API-Key`) protects sensitive endpoints (session mutation, dossier retrieval, and threat feed lookups) using constant-time digest comparison (`secrets.compare_digest`).
- All Phase-3 threat intelligence STIX-3.0 bundles include cryptographic HMAC-SHA256 signatures, validated by `verify_broadcast_signature()` against tampering or payload modification.
