# Feature Spec 11  -  Durable Storage, Directory Creation & Recovery

## 1. Objective
Migrate the default SQLite storage location from the ephemeral OS temp directory (`/tmp` / `%TEMP%`) to a persistent, durable application data directory (`data/chakravyuh_honeypot.db`), ensuring directory auto-creation, database connection resilience, and reliable backup/export functionality.

## 2. Existing Architecture Context
Currently, `ChakravyuhConfig.sqlite_db_path` defaults to `os.path.join(tempfile.gettempdir(), "chakravyuh_honeypot.db")`. In container, cloud, or system restart environments, this directory can be wiped, causing complete loss of honeypot session records and evidentiary FIR dossiers.

## 3. Dependencies
- Standard library: `os`, `pathlib`, `sqlite3`, `shutil`, `datetime`
- Internal modules: `chakravyuh.config`, `chakravyuh.storage.database`

## 4. Exact Files in Scope
- `src/chakravyuh/config.py`
- `src/chakravyuh/storage/database.py`
- `tests/test_security_and_edge_cases.py`

## 5. Required Behavior
1. **Durable Default Location**:
   - `sqlite_db_path` defaults to a durable path in the repository/data folder (e.g. `./data/chakravyuh_honeypot.db`), while respecting `CHAKRAVYUH_DB_PATH`.
   - `ChakravyuhDatabase.__init__` automatically creates parent directories (`os.makedirs(..., exist_ok=True)`) if they do not exist.
2. **Safe Backup & Export Helper**:
   - Add `backup_database(target_path: str) -> str` method to `ChakravyuhDatabase` using SQLite's native `conn.backup()` API to create consistent online snapshots without locking out active WebSocket connections.
3. **Integrity Check**:
   - Add `check_integrity() -> bool` method executing `PRAGMA quick_check;` to verify database health on startup.

## 6. Security Constraints
- SQLite files must not be created in world-writable directories without proper file mode permissions.
- Backup destination path must be validated to prevent arbitrary file overwrites.

## 7. Edge Cases
- Handling in-memory databases (`:memory:`) without failing on `os.makedirs`.
- Handling read-only mounts gracefully.

## 8. Tests
- Test that default path parent directory is auto-created.
- Test online backup creation via `backup_database()` and verify backed-up DB contains identical rows.
- Test `check_integrity()` returns `True` for healthy databases.

## 9. Acceptance Criteria
- Storage operates reliably in persistent directory.
- All existing tests pass without regression.

## 10. Explicit Exclusions
- External PostgreSQL/MySQL drivers (SQLite with WAL mode remains the invariant per Part III F).

## 11. Definition of Done
- Storage path and backup capabilities implemented.
- Unit tests added and verified passing.

