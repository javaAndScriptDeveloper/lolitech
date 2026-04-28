"""Raw TCP socket HTTP HEAD monitor.

Demonstrates low-level HTTP protocol implementation without urllib/requests.
"""

import socket
import time
import logging

from database.models import insert_http_snapshot, get_latest_snapshot

logger = logging.getLogger(__name__)


def send_http_head(host, path="/", timeout=10):
    """Send a raw HTTP HEAD request via TCP socket.

    Returns (status_code, content_length, headers_dict) or None on failure.
    """
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, 80))

        request = (
            f"HEAD {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Connection: close\r\n"
            f"User-Agent: CryptoMonitor/1.0 (Academic Project)\r\n"
            f"\r\n"
        )
        sock.sendall(request.encode("utf-8"))

        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
            if b"\r\n\r\n" in response:
                break

        response_text = response.decode("utf-8", errors="replace")
        lines = response_text.split("\r\n")

        if not lines:
            return None

        # Parse status line: "HTTP/1.1 200 OK"
        status_parts = lines[0].split(" ", 2)
        if len(status_parts) < 2:
            return None
        status_code = int(status_parts[1])

        # Parse headers
        headers = {}
        for line in lines[1:]:
            if not line:
                break
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()

        content_length = None
        if "content-length" in headers:
            try:
                content_length = int(headers["content-length"])
            except ValueError:
                pass

        return (status_code, content_length, headers)

    except (socket.timeout, socket.error, OSError) as e:
        logger.warning("HTTP HEAD failed for %s%s: %s", host, path, e)
        return None
    except Exception as e:
        logger.error("Unexpected error in HTTP HEAD for %s%s: %s", host, path, e)
        return None
    finally:
        if sock:
            try:
                sock.close()
            except OSError:
                pass


def check_source(source_config, db_path, change_threshold_pct=5):
    """Check a single HTTP source for changes.

    Returns (changed, old_length, new_length) or None on failure.
    """
    host = source_config["host"]
    path = source_config.get("path", "/")
    name = source_config["name"]

    # Exponential backoff retry: 3 attempts (1s, 2s, 4s)
    result = None
    for attempt in range(3):
        result = send_http_head(host, path)
        if result is not None:
            break
        wait = 2 ** attempt
        logger.info("Retrying %s in %ds (attempt %d/3)", name, wait, attempt + 1)
        time.sleep(wait)

    if result is None:
        logger.warning("All attempts failed for %s", name)
        insert_http_snapshot(db_path, name, f"http://{host}{path}", None, False)
        return None

    status_code, content_length, headers = result
    url = f"http://{host}{path}"

    # Compare with previous snapshot
    previous = get_latest_snapshot(db_path, name)
    changed = False

    if previous and previous["content_length"] is not None and content_length is not None:
        old_len = previous["content_length"]
        if old_len > 0:
            pct_change = abs(content_length - old_len) / old_len * 100
            changed = pct_change >= change_threshold_pct
        elif content_length != old_len:
            changed = True
    elif previous is None and content_length is not None:
        # First snapshot — not a change
        changed = False

    insert_http_snapshot(db_path, name, url, content_length, changed)

    old_len = previous["content_length"] if previous else None
    if changed:
        logger.info("CHANGE DETECTED on %s: %s -> %s", name, old_len, content_length)

    return (changed, old_len, content_length)
