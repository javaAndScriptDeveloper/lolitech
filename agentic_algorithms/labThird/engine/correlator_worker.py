"""Correlator worker thread — event-driven correlation analysis."""

import json
import logging

from engine.correlator import calculate_correlation, detect_event_type
from database.models import insert_market_event, get_articles_mentioning_token

logger = logging.getLogger(__name__)


def correlator_worker(config, db_path, stop_event, change_event, article_event):
    """Event-driven correlation worker.

    Waits for either change_event or article_event (with 30s timeout).
    When triggered, runs correlation for each configured token and
    inserts market_events if score >= threshold.
    """
    logger.info("Correlator worker started")
    tokens = config.get("keywords", {}).get("tokens", [])
    thresholds = config.get("thresholds", {})
    time_window = thresholds.get("time_window_minutes", 60)
    min_score = thresholds.get("min_alert_score", 30)

    while not stop_event.is_set():
        # Wait for either event or timeout (30s periodic check)
        triggered = change_event.wait(timeout=15) or article_event.wait(timeout=15)

        if stop_event.is_set():
            break

        # Clear events so we don't re-trigger immediately
        change_event.clear()
        article_event.clear()

        for token in tokens:
            if stop_event.is_set():
                break

            try:
                score, recommendation, evidence = calculate_correlation(
                    db_path, token, time_window, config
                )

                if score >= min_score:
                    # Gather keyword evidence for event type detection
                    articles = get_articles_mentioning_token(
                        db_path, time_window, token
                    )
                    all_keywords = []
                    for article in articles:
                        try:
                            kw = article.get("matched_keywords", "[]")
                            kw_list = json.loads(kw) if isinstance(kw, str) else kw
                            all_keywords.extend(kw_list)
                        except (json.JSONDecodeError, TypeError):
                            pass

                    event_type = detect_event_type(all_keywords)
                    http_source = None
                    if evidence.get("http_change"):
                        for detail in evidence.get("details", []):
                            if "HTTP change" in detail:
                                http_source = detail
                                break

                    insert_market_event(
                        db_path,
                        token=token,
                        event_type=event_type,
                        confidence_score=score,
                        recommendation=recommendation,
                        http_source=http_source,
                        nntp_evidence=evidence
                    )
                    logger.info("Market event: %s %s (score=%d, %s)",
                                token, event_type, score, recommendation)
            except Exception as e:
                logger.error("Correlator error for %s: %s", token, e)

    logger.info("Correlator worker stopped")
