"""HTTP monitoring worker thread — polls configured sources in a loop."""

import logging
import time

from monitors.http_monitor import check_source

logger = logging.getLogger(__name__)


def http_worker(config, db_path, stop_event, change_event):
    """Infinite polling loop for HTTP sources.

    Iterates through all http_sources, checks each for content changes.
    Sets change_event if any source changed. Sleeps between cycles.
    Exits when stop_event is set.
    """
    logger.info("HTTP worker started")
    sources = config.get("http_sources", [])
    change_threshold = config.get("thresholds", {}).get("content_length_change_pct", 5)

    while not stop_event.is_set():
        for source in sources:
            if stop_event.is_set():
                break

            try:
                result = check_source(source, db_path, change_threshold)
                if result is not None:
                    changed, old_len, new_len = result
                    if changed:
                        logger.info("HTTP change on %s: %s -> %s",
                                    source["name"], old_len, new_len)
                        change_event.set()
                else:
                    logger.debug("HTTP check failed for %s", source["name"])
            except Exception as e:
                logger.error("HTTP worker error checking %s: %s", source["name"], e)

        # Sleep in small increments so we can respond to stop_event quickly
        interval = sources[0].get("check_interval", 60) if sources else 60
        for _ in range(interval):
            if stop_event.is_set():
                break
            time.sleep(1)

    logger.info("HTTP worker stopped")
