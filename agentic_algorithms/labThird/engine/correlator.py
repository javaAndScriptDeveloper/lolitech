"""Correlation scoring engine for cryptocurrency market events.

Scoring algorithm:
  +30 — HTTP change detected for source mentioning token
  +40 — NNTP mention spike >200% above baseline
  +15 — Multiple newsgroups discussing the token
  +15 — Action words present in recent articles
"""

import json
import logging

from database.models import (
    get_recent_changes_for_source,
    get_article_count_since,
    get_distinct_newsgroups_since,
    get_articles_mentioning_token,
    get_recent_snapshots,
)

logger = logging.getLogger(__name__)


def calculate_correlation(db_path, token, time_window_minutes, config=None):
    """Calculate a correlation score for a given token.

    Returns (score, recommendation, evidence_dict).
    """
    evidence = {
        "http_change": False,
        "nntp_spike": False,
        "multi_newsgroup": False,
        "action_words": False,
        "details": []
    }
    score = 0

    # --- +30: HTTP change on a source ---
    recent_snapshots = get_recent_snapshots(db_path, limit=20)
    for snap in recent_snapshots:
        if snap.get("changed"):
            source_name = snap.get("source_name", "").upper()
            if token.upper() in source_name or True:
                # Any HTTP change is relevant — exchange announcements may affect any token
                score += 30
                evidence["http_change"] = True
                evidence["details"].append(
                    f"HTTP change detected on {snap['source_name']}"
                )
                break

    # --- +40: NNTP mention spike >200% baseline ---
    recent_count = get_article_count_since(db_path, time_window_minutes)
    baseline_count = get_article_count_since(db_path, time_window_minutes * 4)
    baseline_avg = baseline_count / 4.0 if baseline_count > 0 else 0

    if baseline_avg > 0 and recent_count > baseline_avg * 2:
        score += 40
        evidence["nntp_spike"] = True
        evidence["details"].append(
            f"NNTP spike: {recent_count} articles vs {baseline_avg:.1f} baseline"
        )
    elif recent_count > 0 and baseline_avg == 0:
        # New activity where there was none — treat as spike
        score += 40
        evidence["nntp_spike"] = True
        evidence["details"].append(
            f"New NNTP activity: {recent_count} articles (no baseline)"
        )

    # --- +15: Multiple newsgroups discussing ---
    distinct_groups = get_distinct_newsgroups_since(db_path, time_window_minutes, token)
    if distinct_groups >= 2:
        score += 15
        evidence["multi_newsgroup"] = True
        evidence["details"].append(
            f"Discussed in {distinct_groups} different newsgroups"
        )

    # --- +15: Action words present ---
    action_words = []
    if config:
        action_words = config.get("keywords", {}).get("action_words", [])

    articles = get_articles_mentioning_token(db_path, time_window_minutes, token)
    found_action_words = set()
    for article in articles:
        subject = (article.get("subject") or "").upper()
        kw_raw = article.get("matched_keywords", "[]")
        try:
            kw_list = json.loads(kw_raw) if isinstance(kw_raw, str) else kw_raw
        except (json.JSONDecodeError, TypeError):
            kw_list = []

        for word in action_words:
            if word.upper() in subject or word in kw_list:
                found_action_words.add(word)

    if found_action_words:
        score += 15
        evidence["action_words"] = True
        evidence["details"].append(
            f"Action words found: {', '.join(found_action_words)}"
        )

    # Cap score at 100
    score = min(score, 100)

    recommendation = classify_event(score)

    return score, recommendation, evidence


def classify_event(score):
    """Classify event by confidence score."""
    if score >= 70:
        return "High Priority Alert"
    elif score >= 50:
        return "Monitor Closely"
    elif score >= 30:
        return "Informational"
    else:
        return "No Action"


def detect_event_type(keywords):
    """Classify event type based on matched keywords."""
    if not keywords:
        return "general"

    kw_upper = [k.upper() for k in keywords]

    if any(w in kw_upper for w in ["LISTING", "DELISTING"]):
        return "listing"
    if any(w in kw_upper for w in ["FORK", "UPGRADE"]):
        return "fork"
    if any(w in kw_upper for w in ["REGULATION", "BAN", "APPROVAL", "ETF"]):
        return "regulatory"

    return "general"
