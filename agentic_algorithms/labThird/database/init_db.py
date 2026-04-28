"""Database initialization — creates tables with WAL journal mode."""

import sqlite3
import logging

logger = logging.getLogger(__name__)


def init_db(db_path):
    """Create the SQLite database and tables if they don't exist."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS http_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,
            url TEXT NOT NULL,
            content_length INTEGER,
            changed INTEGER DEFAULT 0,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS nntp_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT UNIQUE,
            newsgroup TEXT NOT NULL,
            subject TEXT,
            author TEXT,
            posted_date TEXT,
            matched_keywords TEXT,
            relevance_score REAL DEFAULT 0,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS market_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT NOT NULL,
            event_type TEXT,
            confidence_score REAL NOT NULL,
            recommendation TEXT,
            http_source TEXT,
            nntp_evidence TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_http_source ON http_snapshots(source_name);
        CREATE INDEX IF NOT EXISTS idx_http_time ON http_snapshots(checked_at);
        CREATE INDEX IF NOT EXISTS idx_nntp_group ON nntp_articles(newsgroup);
        CREATE INDEX IF NOT EXISTS idx_nntp_time ON nntp_articles(fetched_at);
        CREATE INDEX IF NOT EXISTS idx_events_token ON market_events(token);
        CREATE INDEX IF NOT EXISTS idx_events_time ON market_events(created_at);
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized at %s", db_path)
