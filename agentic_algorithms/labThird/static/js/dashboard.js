// Dashboard — polls API endpoints and renders data

const POLL_INTERVAL = 30000; // 30 seconds
let pollTimer = null;

document.addEventListener("DOMContentLoaded", () => {
    pollUpdates();
    pollTimer = setInterval(pollUpdates, POLL_INTERVAL);
    requestNotificationPermission();
});

function pollUpdates() {
    fetchJSON("/api/alerts", updateAlertsPanel);
    fetchJSON("/api/http-changes", updateHTTPTable);
    fetchJSON("/api/nntp-feed", updateNNTPTable);
    fetchJSON("/api/status", updateStatusBar);
}

function fetchJSON(url, callback) {
    fetch(url)
        .then(r => {
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return r.json();
        })
        .then(callback)
        .catch(err => {
            console.error(`Error fetching ${url}:`, err);
        });
}

// --- Alerts Panel ---

function updateAlertsPanel(events) {
    const container = document.getElementById("alerts-body");
    if (!container) return;

    const countEl = document.getElementById("alerts-count");
    if (countEl) countEl.textContent = events.length;

    if (events.length === 0) {
        container.innerHTML = '<div class="empty-state">No alerts yet. Monitoring...</div>';
        return;
    }

    container.innerHTML = events.map(ev => {
        const severity = getSeverityClass(ev.confidence_score);
        const evidence = parseJSON(ev.nntp_evidence);
        const details = evidence.details ? evidence.details.join("; ") : "";

        return `
            <div class="alert-card ${severity}">
                <div class="alert-header">
                    <span class="token">${esc(ev.token)}</span>
                    <span class="score ${severity}">${ev.confidence_score}</span>
                </div>
                <div class="event-type">${esc(ev.event_type || "general")}</div>
                <div class="recommendation">${esc(ev.recommendation)}</div>
                ${details ? `<div class="recommendation">${esc(details)}</div>` : ""}
                <div class="timestamp">${formatTimestamp(ev.created_at)}</div>
            </div>
        `;
    }).join("");

    // Browser notification for high-priority
    const highPriority = events.filter(e => e.confidence_score >= 70);
    if (highPriority.length > 0 && Notification.permission === "granted") {
        const latest = highPriority[0];
        new Notification("Crypto Alert", {
            body: `${latest.token}: ${latest.recommendation} (score: ${latest.confidence_score})`,
        });
    }
}

function getSeverityClass(score) {
    if (score >= 70) return "high";
    if (score >= 50) return "monitor";
    return "info";
}

// --- HTTP Table ---

function updateHTTPTable(snapshots) {
    const tbody = document.getElementById("http-tbody");
    if (!tbody) return;

    const countEl = document.getElementById("http-count");
    if (countEl) countEl.textContent = snapshots.length;

    if (snapshots.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">No data yet</td></tr>';
        return;
    }

    tbody.innerHTML = snapshots.map(s => `
        <tr>
            <td>${esc(s.source_name)}</td>
            <td>${s.content_length !== null ? s.content_length : "N/A"}</td>
            <td class="${s.changed ? 'change-yes' : 'change-no'}">
                ${s.changed ? "CHANGED" : "—"}
            </td>
            <td>${formatTimestamp(s.checked_at)}</td>
        </tr>
    `).join("");
}

// --- NNTP Table ---

function updateNNTPTable(articles) {
    const tbody = document.getElementById("nntp-tbody");
    if (!tbody) return;

    const countEl = document.getElementById("nntp-count");
    if (countEl) countEl.textContent = articles.length;

    if (articles.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">No articles yet</td></tr>';
        return;
    }

    tbody.innerHTML = articles.map(a => {
        const keywords = parseJSON(a.matched_keywords);
        const kwHTML = Array.isArray(keywords)
            ? keywords.map(k => `<span class="keyword">${esc(k)}</span>`).join(" ")
            : "";
        return `
            <tr>
                <td>${esc(a.newsgroup)}</td>
                <td>${esc(a.subject || "")}</td>
                <td>${kwHTML || '<span class="change-no">—</span>'}</td>
                <td>${formatTimestamp(a.fetched_at)}</td>
            </tr>
        `;
    }).join("");
}

// --- Status Bar ---

function updateStatusBar(status) {
    const el = document.getElementById("uptime");
    if (el) el.textContent = status.uptime_human || "—";

    const threads = status.threads || {};
    for (const [name, info] of Object.entries(threads)) {
        const dot = document.getElementById(`dot-${name}`);
        if (dot) {
            dot.className = `status-dot ${info.alive ? "online" : "offline"}`;
        }
    }
}

// --- Utils ---

function formatTimestamp(iso) {
    if (!iso) return "—";
    const date = new Date(iso + (iso.includes("Z") || iso.includes("+") ? "" : "Z"));
    const now = new Date();
    const diff = (now - date) / 1000;

    if (diff < 60) return "just now";
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleDateString();
}

function requestNotificationPermission() {
    if ("Notification" in window && Notification.permission === "default") {
        Notification.requestPermission();
    }
}

function esc(str) {
    if (str === null || str === undefined) return "";
    const div = document.createElement("div");
    div.textContent = String(str);
    return div.innerHTML;
}

function parseJSON(val) {
    if (!val) return {};
    if (typeof val === "object") return val;
    try { return JSON.parse(val); }
    catch { return {}; }
}
