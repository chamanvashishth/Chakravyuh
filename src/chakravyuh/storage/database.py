"""
SQLite3 Persistence Repository for Chakravyuh.

Stores call handover sessions, speaker embedding metadata, chronological transcript
turns, extracted mule IOCs, compiled I4C FIR dossiers, and Phase-3 live threat feed items.
All queries use strict parameterized bindings (`?`) to prevent SQL injection.
Automatically negotiates WAL or MEMORY journal mode if the underlying mount does not
support shared-memory mmap (`-shm`).
"""

import os
import sqlite3
import threading
from typing import List, Optional

from chakravyuh.config import CONFIG
from chakravyuh.models.schemas import (
    CallSession,
    ExtractedIOC,
    I4CDossier,
    ThreatFeedEntry,
)


class ChakravyuhDatabase:
    """Thread-safe SQLite repository backing the Chakravyuh Honeypot."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or CONFIG.sqlite_db_path
        if self.db_path != ":memory:":
            parent_dir = os.path.dirname(os.path.abspath(self.db_path))
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
        self._lock = threading.RLock()
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
        except sqlite3.OperationalError:
            conn.execute("PRAGMA journal_mode=MEMORY;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_schema(self) -> None:
        with self._lock:
            conn = self._connect()
            try:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS call_sessions (
                        session_id TEXT PRIMARY KEY,
                        caller_number TEXT NOT NULL,
                        victim_alias TEXT NOT NULL,
                        status TEXT NOT NULL,
                        scam_category TEXT NOT NULL,
                        claimed_authority TEXT NOT NULL,
                        threat_score REAL NOT NULL,
                        current_stage TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        time_wasted_sec INTEGER NOT NULL,
                        session_json TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS extracted_iocs (
                        ioc_id TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        ioc_type TEXT NOT NULL,
                        value TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        bank_or_provider TEXT NOT NULL,
                        role_classification TEXT NOT NULL,
                        first_seen_turn INTEGER NOT NULL,
                        extracted_at TEXT NOT NULL,
                        ioc_json TEXT NOT NULL,
                        PRIMARY KEY (session_id, ioc_id)
                    );

                    CREATE TABLE IF NOT EXISTS i4c_dossiers (
                        session_id TEXT PRIMARY KEY,
                        dossier_id TEXT NOT NULL,
                        generated_at TEXT NOT NULL,
                        dossier_json TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS threat_feed (
                        feed_id TEXT PRIMARY KEY,
                        ioc_type TEXT NOT NULL,
                        ioc_value TEXT NOT NULL,
                        bank_or_provider TEXT NOT NULL,
                        role_classification TEXT NOT NULL,
                        scam_category TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        source_session_id TEXT NOT NULL,
                        reported_at TEXT NOT NULL,
                        feed_json TEXT NOT NULL
                    );
                    """
                )
                conn.commit()
            finally:
                conn.close()

    def save_session(self, session: CallSession) -> None:
        """Insert or update a CallSession and its extracted IOCs."""
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    """
                    INSERT INTO call_sessions (
                        session_id, caller_number, victim_alias, status,
                        scam_category, claimed_authority, threat_score,
                        current_stage, created_at, updated_at, time_wasted_sec,
                        session_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(session_id) DO UPDATE SET
                        status=excluded.status,
                        scam_category=excluded.scam_category,
                        claimed_authority=excluded.claimed_authority,
                        threat_score=excluded.threat_score,
                        current_stage=excluded.current_stage,
                        updated_at=excluded.updated_at,
                        time_wasted_sec=excluded.time_wasted_sec,
                        session_json=excluded.session_json;
                    """,
                    (
                        session.session_id,
                        session.caller_number,
                        session.victim_alias,
                        session.status.value,
                        session.scam_category.value,
                        session.claimed_authority,
                        session.threat_score,
                        session.current_stage.value,
                        session.created_at,
                        session.updated_at,
                        session.time_wasted_sec,
                        session.json(),
                    ),
                )

                for ioc in session.extracted_iocs:
                    conn.execute(
                        """
                        INSERT INTO extracted_iocs (
                            ioc_id, session_id, ioc_type, value, confidence,
                            bank_or_provider, role_classification, first_seen_turn,
                            extracted_at, ioc_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(session_id, ioc_id) DO NOTHING;
                        """,
                        (
                            ioc.ioc_id,
                            session.session_id,
                            ioc.ioc_type.value,
                            ioc.value,
                            ioc.confidence,
                            ioc.bank_or_provider,
                            ioc.role_classification,
                            ioc.first_seen_turn,
                            ioc.extracted_at,
                            ioc.json(),
                        ),
                    )
                conn.commit()
            finally:
                conn.close()

    def get_session(self, session_id: str) -> Optional[CallSession]:
        """Retrieve a CallSession by session_id."""
        with self._lock:
            conn = self._connect()
            try:
                row = conn.execute(
                    "SELECT session_json FROM call_sessions WHERE session_id = ?;",
                    (session_id,),
                ).fetchone()
                if not row:
                    return None
                return CallSession.parse_raw(row["session_json"])
            finally:
                conn.close()

    def list_sessions(self) -> List[CallSession]:
        """List all recorded honeypot sessions ordered by updated_at descending."""
        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute(
                    "SELECT session_json FROM call_sessions ORDER BY updated_at DESC;"
                ).fetchall()
                return [CallSession.parse_raw(r["session_json"]) for r in rows]
            finally:
                conn.close()

    def save_dossier(self, dossier: I4CDossier) -> None:
        """Persist a compiled I4C FIR Dossier and publish its mule IOCs to the threat feed."""
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    """
                    INSERT INTO i4c_dossiers (session_id, dossier_id, generated_at, dossier_json)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(session_id) DO UPDATE SET
                        dossier_id=excluded.dossier_id,
                        generated_at=excluded.generated_at,
                        dossier_json=excluded.dossier_json;
                    """,
                    (
                        dossier.session_id,
                        dossier.dossier_id,
                        dossier.generated_at,
                        dossier.json(),
                    ),
                )

                all_financial_iocs: List[ExtractedIOC] = (
                    dossier.mule_upi_ids
                    + dossier.mule_bank_accounts
                    + dossier.ifsc_codes
                    + dossier.phishing_urls
                    + dossier.scammer_phones
                )
                for ioc in all_financial_iocs:
                    feed_id = f"FEED-{ioc.ioc_id}"
                    entry = ThreatFeedEntry(
                        feed_id=feed_id,
                        ioc_type=ioc.ioc_type,
                        ioc_value=ioc.value,
                        bank_or_provider=ioc.bank_or_provider,
                        role_classification=ioc.role_classification,
                        scam_category=dossier.scam_category,
                        confidence=ioc.confidence,
                        source_session_id=dossier.session_id,
                    )
                    conn.execute(
                        """
                        INSERT INTO threat_feed (
                            feed_id, ioc_type, ioc_value, bank_or_provider,
                            role_classification, scam_category, confidence,
                            source_session_id, reported_at, feed_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(feed_id) DO UPDATE SET
                            confidence=excluded.confidence,
                            reported_at=excluded.reported_at,
                            feed_json=excluded.feed_json;
                        """,
                        (
                            entry.feed_id,
                            entry.ioc_type.value,
                            entry.ioc_value,
                            entry.bank_or_provider,
                            entry.role_classification,
                            entry.scam_category.value,
                            entry.confidence,
                            entry.source_session_id,
                            entry.reported_at,
                            entry.json(),
                        ),
                    )
                conn.commit()
            finally:
                conn.close()

    def get_dossier(self, session_id: str) -> Optional[I4CDossier]:
        """Fetch the latest compiled I4CDossier for a session."""
        with self._lock:
            conn = self._connect()
            try:
                row = conn.execute(
                    "SELECT dossier_json FROM i4c_dossiers WHERE session_id = ?;",
                    (session_id,),
                ).fetchone()
                if not row:
                    return None
                return I4CDossier.parse_raw(row["dossier_json"])
            finally:
                conn.close()

    def list_threat_feed(self, limit: int = 100) -> List[ThreatFeedEntry]:
        """Return Phase-3 Live Threat Intelligence Feed entries."""
        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute(
                    "SELECT feed_json FROM threat_feed ORDER BY reported_at DESC LIMIT ?;",
                    (int(limit),),
                ).fetchall()
                return [ThreatFeedEntry.parse_raw(r["feed_json"]) for r in rows]
            finally:
                conn.close()

    def check_integrity(self) -> bool:
        """Verify SQLite database structural integrity via PRAGMA quick_check."""
        with self._lock:
            conn = self._connect()
            try:
                row = conn.execute("PRAGMA quick_check;").fetchone()
                return bool(row and row[0] == "ok")
            finally:
                conn.close()

    def backup_database(self, target_path: str) -> str:
        """
        Create a consistent online backup of the SQLite database using SQLite's native backup API.
        """
        target_dir = os.path.dirname(os.path.abspath(target_path))
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
        with self._lock:
            source_conn = self._connect()
            try:
                dest_conn = sqlite3.connect(target_path)
                try:
                    source_conn.backup(dest_conn)
                finally:
                    dest_conn.close()
            finally:
                source_conn.close()
        return target_path
