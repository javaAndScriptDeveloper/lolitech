"""Raw TCP socket NNTP monitor.

Implements NNTP protocol (RFC 3977) at the socket level for educational purposes.
"""

import socket
import re
import logging

from database.models import insert_nntp_article

logger = logging.getLogger(__name__)


def nntp_connect(server, port=119, timeout=10):
    """Connect to an NNTP server and read the welcome banner.

    Returns (socket, banner_text) or (None, error_message).
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((server, port))
        banner = _read_line(sock)
        if banner and banner.startswith("200"):
            logger.info("Connected to NNTP server %s: %s", server, banner.strip())
            return sock, banner
        elif banner and banner.startswith("201"):
            logger.info("Connected (read-only) to %s: %s", server, banner.strip())
            return sock, banner
        else:
            logger.warning("Unexpected NNTP banner from %s: %s", server, banner)
            sock.close()
            return None, banner or "No banner received"
    except (socket.timeout, socket.error, OSError) as e:
        logger.warning("NNTP connect failed for %s:%d: %s", server, port, e)
        return None, str(e)


def _read_line(sock):
    """Read a single CRLF-terminated line from socket."""
    data = b""
    while not data.endswith(b"\r\n"):
        chunk = sock.recv(1)
        if not chunk:
            break
        data += chunk
    return data.decode("utf-8", errors="replace")


def nntp_command(sock, command):
    """Send an NNTP command and read the single-line response."""
    sock.sendall((command + "\r\n").encode("utf-8"))
    return _read_line(sock)


def nntp_read_multiline(sock):
    """Read a dot-terminated multi-line NNTP response.

    Lines starting with '..' are unescaped. Reading stops at a lone '.\\r\\n'.
    """
    lines = []
    buf = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
        while b"\r\n" in buf:
            line, buf = buf.split(b"\r\n", 1)
            decoded = line.decode("utf-8", errors="replace")
            if decoded == ".":
                return lines
            if decoded.startswith(".."):
                decoded = decoded[1:]
            lines.append(decoded)
    return lines


def nntp_group(sock, group):
    """Select a newsgroup. Returns (count, first, last) or None."""
    response = nntp_command(sock, f"GROUP {group}")
    if not response or not response.startswith("211"):
        logger.warning("GROUP %s failed: %s", group, response)
        return None
    # 211 count first last groupname
    parts = response.strip().split()
    if len(parts) >= 4:
        return int(parts[1]), int(parts[2]), int(parts[3])
    return None


def nntp_head(sock, article_id):
    """Fetch article headers. Returns dict of headers or None."""
    response = nntp_command(sock, f"HEAD {article_id}")
    if not response or not response.startswith("221"):
        return None
    raw_lines = nntp_read_multiline(sock)
    return parse_headers(raw_lines)


def nntp_article(sock, article_id):
    """Fetch full article (headers + body). Returns (headers_dict, body_text) or None."""
    response = nntp_command(sock, f"ARTICLE {article_id}")
    if not response or not response.startswith("220"):
        return None
    raw_lines = nntp_read_multiline(sock)

    # Split headers and body at blank line
    headers_lines = []
    body_lines = []
    in_body = False
    for line in raw_lines:
        if not in_body and line == "":
            in_body = True
            continue
        if in_body:
            body_lines.append(line)
        else:
            headers_lines.append(line)

    headers = parse_headers(headers_lines)
    body = "\n".join(body_lines)
    return headers, body


def nntp_quit(sock):
    """Send QUIT and close connection."""
    try:
        nntp_command(sock, "QUIT")
    except (socket.error, OSError):
        pass
    finally:
        try:
            sock.close()
        except OSError:
            pass


def parse_headers(raw_lines):
    """Parse NNTP header lines into a dict. Handles folded headers."""
    headers = {}
    current_key = None
    for line in raw_lines:
        if not line:
            continue
        if line[0] in (" ", "\t") and current_key:
            headers[current_key] += " " + line.strip()
        elif ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            headers[current_key] = value.strip()
    return headers


def scan_keywords(text, keywords_config):
    """Scan text for configured keywords.

    Returns (matched_keywords_list, relevance_score).
    Score: +10 per token match, +20 per action word match.
    """
    if not text:
        return [], 0.0

    text_upper = text.upper()
    matched = []
    score = 0.0

    for token in keywords_config.get("tokens", []):
        if token.upper() in text_upper:
            matched.append(token)
            score += 10

    for word in keywords_config.get("action_words", []):
        if word.upper() in text_upper:
            matched.append(word)
            score += 20

    return matched, score


def fetch_new_articles(source_config, keywords_config, db_path, max_articles=20):
    """Connect to NNTP server, fetch recent articles, scan for keywords.

    Returns list of article dicts with matched keywords, or empty list on failure.
    """
    server = source_config["server"]
    port = source_config.get("port", 119)
    groups = source_config.get("groups", [])
    results = []

    sock, banner = nntp_connect(server, port)
    if sock is None:
        logger.warning("Cannot connect to %s — skipping", server)
        return results

    try:
        for group_name in groups:
            group_info = nntp_group(sock, group_name)
            if group_info is None:
                continue

            count, first, last = group_info
            # Fetch the most recent articles (up to max_articles)
            start = max(first, last - max_articles + 1)

            for article_num in range(start, last + 1):
                try:
                    article_data = nntp_article(sock, article_num)
                    if article_data is None:
                        continue

                    headers, body = article_data
                    subject = headers.get("Subject", "")
                    author = headers.get("From", "")
                    date = headers.get("Date", "")
                    msg_id = headers.get("Message-ID", f"<{article_num}@{group_name}>")

                    full_text = f"{subject} {body}"
                    matched, score = scan_keywords(full_text, keywords_config)

                    insert_nntp_article(
                        db_path, msg_id, group_name, subject, author,
                        date, matched, score
                    )

                    if matched:
                        results.append({
                            "message_id": msg_id,
                            "newsgroup": group_name,
                            "subject": subject,
                            "author": author,
                            "date": date,
                            "matched_keywords": matched,
                            "relevance_score": score
                        })
                except Exception as e:
                    logger.warning("Error fetching article %d from %s: %s",
                                   article_num, group_name, e)
                    continue
    finally:
        nntp_quit(sock)

    return results
