"""NNTP monitoring worker thread — polls newsgroup servers in a loop."""

import logging
import time

from monitors.nntp_monitor import fetch_new_articles

logger = logging.getLogger(__name__)


def nntp_worker(config, db_path, stop_event, article_event):
    """Infinite polling loop for NNTP sources.

    Iterates through all nntp_sources, fetches new articles and scans keywords.
    Sets article_event if high-relevance articles found. Sleeps between cycles.
    Exits when stop_event is set.
    """
    logger.info("NNTP worker started")
    sources = config.get("nntp_sources", [])
    keywords = config.get("keywords", {})
    min_matches = keywords.get("min_keyword_matches", 2)

    while not stop_event.is_set():
        for source in sources:
            if stop_event.is_set():
                break

            try:
                articles = fetch_new_articles(source, keywords, db_path)
                high_relevance = [
                    a for a in articles
                    if len(a.get("matched_keywords", [])) >= min_matches
                ]
                if high_relevance:
                    logger.info("Found %d high-relevance articles from %s",
                                len(high_relevance), source["server"])
                    article_event.set()
            except Exception as e:
                logger.error("NNTP worker error for %s: %s", source["server"], e)

        interval = sources[0].get("check_interval", 120) if sources else 120
        for _ in range(interval):
            if stop_event.is_set():
                break
            time.sleep(1)

    logger.info("NNTP worker stopped")
