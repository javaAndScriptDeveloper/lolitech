"""Flask application — web server and thread orchestrator."""

import json
import os
import signal
import sys
import threading
import time
import logging

from flask import Flask, render_template, jsonify, request

from database.init_db import init_db
from database.models import (
    get_recent_snapshots,
    get_recent_articles,
    get_recent_events,
)
from monitors.http_worker import http_worker
from monitors.nntp_worker import nntp_worker
from engine.correlator_worker import correlator_worker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

app = Flask(__name__)

# Thread synchronization
stop_event = threading.Event()
change_event = threading.Event()
article_event = threading.Event()

# Global state
config = {}
start_time = None
worker_threads = []


def load_config():
    global config
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    return config


def save_config(new_config):
    global config
    with open(CONFIG_PATH, "w") as f:
        json.dump(new_config, f, indent=4)
    config = new_config


def get_db_path():
    return os.path.join(BASE_DIR, config.get("db_path", "labThird.db"))


def start_workers():
    global worker_threads, start_time
    start_time = time.time()
    db_path = get_db_path()

    threads = [
        threading.Thread(
            target=http_worker,
            args=(config, db_path, stop_event, change_event),
            name="http-worker",
            daemon=True,
        ),
        threading.Thread(
            target=nntp_worker,
            args=(config, db_path, stop_event, article_event),
            name="nntp-worker",
            daemon=True,
        ),
        threading.Thread(
            target=correlator_worker,
            args=(config, db_path, stop_event, change_event, article_event),
            name="correlator-worker",
            daemon=True,
        ),
    ]

    for t in threads:
        t.start()
        logger.info("Started thread: %s", t.name)

    worker_threads = threads


def graceful_shutdown(signum=None, frame=None):
    logger.info("Shutting down...")
    stop_event.set()
    for t in worker_threads:
        t.join(timeout=5)
    logger.info("All workers stopped")
    sys.exit(0)


# --- Routes ---

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/conf")
def conf_page():
    return render_template("conf.html")


@app.route("/api/status")
def api_status():
    uptime = time.time() - start_time if start_time else 0
    thread_status = {}
    for t in worker_threads:
        thread_status[t.name] = {
            "alive": t.is_alive(),
        }
    return jsonify({
        "uptime_seconds": int(uptime),
        "uptime_human": _format_uptime(uptime),
        "threads": thread_status,
        "config_loaded": bool(config),
    })


@app.route("/api/http-changes")
def api_http_changes():
    db_path = get_db_path()
    limit = request.args.get("limit", 50, type=int)
    snapshots = get_recent_snapshots(db_path, limit=limit)
    return jsonify(snapshots)


@app.route("/api/nntp-feed")
def api_nntp_feed():
    db_path = get_db_path()
    limit = request.args.get("limit", 50, type=int)
    articles = get_recent_articles(db_path, limit=limit)
    return jsonify(articles)


@app.route("/api/alerts")
def api_alerts():
    db_path = get_db_path()
    limit = request.args.get("limit", 50, type=int)
    events = get_recent_events(db_path, limit=limit)
    return jsonify(events)


@app.route("/api/config", methods=["GET"])
def api_get_config():
    return jsonify(config)


@app.route("/api/config", methods=["POST"])
def api_set_config():
    try:
        new_config = request.get_json()
        if not new_config:
            return jsonify({"error": "No JSON body provided"}), 400

        # Basic validation
        if "http_sources" not in new_config and "keywords" not in new_config:
            return jsonify({"error": "Config must include http_sources or keywords"}), 400

        save_config(new_config)
        logger.info("Configuration updated")
        return jsonify({"status": "ok", "message": "Configuration saved"})
    except Exception as e:
        logger.error("Config update failed: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/history")
def api_history():
    db_path = get_db_path()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    limit = per_page
    # Simple offset-based pagination
    events = get_recent_events(db_path, limit=page * per_page)
    start = (page - 1) * per_page
    paginated = events[start:start + per_page]
    return jsonify({
        "page": page,
        "per_page": per_page,
        "events": paginated,
    })


def _format_uptime(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}h {minutes}m {secs}s"


if __name__ == "__main__":
    load_config()
    db_path = get_db_path()
    init_db(db_path)

    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    start_workers()

    port = config.get("web_port", 8080)
    logger.info("Starting web server on port %d", port)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
