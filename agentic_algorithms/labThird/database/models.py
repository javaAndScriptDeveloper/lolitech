"""Data access functions using raw sqlite3. Each function opens its own
connection for thread safety (SQLite WAL mode allows concurrent reads)."""

import sqlite3
import json
import logging

logger = logging.getLogger(__name__)


def _connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# --- HTTP Snapshots ---

def insert_http_snapshot(db_path, source_name, url, content_length, changed):
    conn = _connect(db_path)
    try:
        conn.execute(
            "INSERT INTO http_snapshots (source_name, url, content_length, changed) "
            "VALUES (?, ?, ?, ?)",
            (source_name, url, content_length, int(changed))
        )
        conn.commit()
    finally:
        conn.close()


def get_latest_snapshot(db_path, source_name):
    """Return the most recent snapshot for a source, or None."""
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM http_snapshots WHERE source_name = ? "
            "ORDER BY checked_at DESC LIMIT 1",
            (source_name,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_recent_snapshots(db_path, limit=50):
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM http_snapshots ORDER BY checked_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# --- NNTP Articles ---

def insert_nntp_article(db_path, message_id, newsgroup, subject, author,
                        posted_date, matched_keywords, relevance_score):
    conn = _connect(db_path)
    try:
        kw_json = json.dumps(matched_keywords) if isinstance(matched_keywords, list) else matched_keywords
        conn.execute(
            "INSERT OR IGNORE INTO nntp_articles "
            "(message_id, newsgroup, subject, author, posted_date, matched_keywords, relevance_score) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (message_id, newsgroup, subject, author, posted_date, kw_json, relevance_score)
        )
        conn.commit()
    finally:
        conn.close()


def get_recent_articles(db_path, limit=50):
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM nntp_articles ORDER BY fetched_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_article_count_since(db_path, minutes, newsgroup=None):
    conn = _connect(db_path)
    try:
        if newsgroup:
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM nntp_articles "
                "WHERE fetched_at >= datetime('now', ? || ' minutes') AND newsgroup = ?",
                (f"-{minutes}", newsgroup)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM nntp_articles "
                "WHERE fetched_at >= datetime('now', ? || ' minutes')",
                (f"-{minutes}",)
            ).fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()


def get_distinct_newsgroups_since(db_path, minutes, token):
    """Count distinct newsgroups mentioning a token within time window."""
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT COUNT(DISTINCT newsgroup) as cnt FROM nntp_articles "
            "WHERE fetched_at >= datetime('now', ? || ' minutes') "
            "AND (subject LIKE ? OR matched_keywords LIKE ?)",
            (f"-{minutes}", f"%{token}%", f"%{token}%")
        ).fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()


def get_articles_mentioning_token(db_path, minutes, token):
    """Get articles mentioning a token within time window."""
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM nntp_articles "
            "WHERE fetched_at >= datetime('now', ? || ' minutes') "
            "AND (subject LIKE ? OR matched_keywords LIKE ?)",
            (f"-{minutes}", f"%{token}%", f"%{token}%")
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# --- Market Events ---

def insert_market_event(db_path, token, event_type, confidence_score,
                        recommendation, http_source, nntp_evidence):
    conn = _connect(db_path)
    try:
        evidence_json = json.dumps(nntp_evidence) if isinstance(nntp_evidence, (list, dict)) else nntp_evidence
        conn.execute(
            "INSERT INTO market_events "
            "(token, event_type, confidence_score, recommendation, http_source, nntp_evidence) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (token, event_type, confidence_score, recommendation, http_source, evidence_json)
        )
        conn.commit()
    finally:
        conn.close()


def get_recent_events(db_path, limit=50):
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM market_events ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_recent_changes_for_source(db_path, source_name, minutes):
    """Check if there were HTTP changes for a source within time window."""
    conn = _connect(db_path)
    try:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM http_snapshots "
            "WHERE source_name = ? AND changed = 1 "
            "AND checked_at >= datetime('now', ? || ' minutes')",
            (source_name, f"-{minutes}")
        ).fetchone()
        return row["cnt"] if row else 0
    finally:
        conn.close()
