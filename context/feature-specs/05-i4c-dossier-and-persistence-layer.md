# Feature Spec 05  -  I4C / Cybercrime FIR Dossier Compiler & SQLite Persistence

## 1. Objective
Implement the thread-safe SQLite persistence layer (`database.py`) and the automated **I4C (Indian Cyber Crime Coordination Centre) / 1930 National Cyber Crime Reporting Portal Dossier Compiler** (`i4c_compiler.py`), plus Phase 2 SIP/WebRTC signaling payload generators and Phase 3 Live Fintech Threat Feed dispatchers.

## 2. Context & Dependencies
- Depends on: `sqlite3`, `json`, `hashlib`, `datetime`, `src/chakravyuh/models/schemas.py`.

## 3. Exact Implementation Scope
- `src/chakravyuh/storage/__init__.py`
- `src/chakravyuh/storage/database.py`
- `src/chakravyuh/dossier/__init__.py`
- `src/chakravyuh/dossier/i4c_compiler.py`

## 4. Required Behavior
1. **SQLite Repository (`ChakravyuhDatabase`)**:
   - Initializes tables: `call_sessions`, `transcript_turns`, `extracted_iocs`, `i4c_dossiers`, `threat_feed_events`.
   - Uses parameterized SQL queries exclusively (`?` placeholders) to prevent SQL injection.
   - Supports full CRUD for sessions, turns, IOCs, and compiled dossiers.
2. **I4C Dossier Compiler (`I4CDossierCompiler`)**:
   - Aggregates session metadata, `vachana-vc-v1` speaker-embedding cryptographic audit trail, categorized IOCs (Mule UPI IDs, Bank Accounts, IFSCs, Phishing Links, Scammer Phones), and timestamped transcripts into an official I4C / 1930 FIR Dossier.
   - Generates both structured JSON (`I4CDossier`) and a formatted Markdown/Text **Official Cybercrime FIR Evidence Report** ready for law enforcement filing under **BNS Section 318(4) (Cheating) & IT Act Section 66D (Cheating by personation using computer resource)**.
   - Generates **Phase 2 SIP/WebRTC Call Merge (`REFER` / `INVITE` SDP)** payloads and **Phase 3 NPCI / Fintech Mule Freeze Webhook** payloads.

## 5. Acceptance Criteria & Definition of Done
- Dossier accurately categorizes all extracted IOCs, attaches BNS 318(4) / IT Act 66D legal citations, and persists to SQLite.
- Database operations pass concurrency and SQL-injection resilience tests.
