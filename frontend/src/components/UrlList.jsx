import React from 'react';
import { ExternalLink, Trash2, History, AlertCircle, CheckCircle2, Clock } from 'lucide-react';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Format an ISO timestamp into a human-readable relative time string. */
function relativeTime(ts) {
  if (!ts) return 'Pending check…';
  try {
    // SQLite strips timezone info, so naive datetimes come back without 'Z'.
    // Without 'Z', JS interprets them as LOCAL time (e.g. IST = UTC+5:30),
    // making checks appear ~5h older than they really are.
    // Appending 'Z' forces correct UTC interpretation.
    const utcTs = ts.endsWith('Z') || ts.includes('+') ? ts : ts + 'Z';
    const diffMs = Date.now() - new Date(utcTs).getTime();
    const diffSec = Math.floor(diffMs / 1000);
    if (diffSec < 5) return 'just now';
    if (diffSec < 60) return `${diffSec}s ago`;
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHr = Math.floor(diffMin / 60);
    if (diffHr < 24) return `${diffHr}h ago`;
    return `${Math.floor(diffHr / 24)}d ago`;
  } catch {
    return ts;
  }
}

function StatusBadge({ isUp }) {
  if (isUp === null || isUp === undefined) {
    return (
      <span className="badge badge-pending">
        <Clock size={12} /> PENDING
      </span>
    );
  }
  if (isUp === true) {
    return (
      <span className="badge badge-up">
        <CheckCircle2 size={12} /> UP
      </span>
    );
  }
  return (
    <span className="badge badge-down">
      <AlertCircle size={12} /> DOWN
    </span>
  );
}

function Latency({ ms, isUp }) {
  if (ms === null || ms === undefined) return <span style={{ color: 'var(--text-dim)' }}>—</span>;
  const colorClass = !isUp ? 'latency-bad' : ms > 1000 ? 'latency-warn' : 'latency-good';
  return <span className={`latency-text ${colorClass}`}>{Math.round(ms)} ms</span>;
}

function UptimePill({ pct }) {
  if (pct === null || pct === undefined) return <span style={{ color: 'var(--text-dim)' }}>—</span>;
  const color = pct >= 99 ? 'var(--success)' : pct >= 90 ? 'var(--warning)' : 'var(--danger)';
  return (
    <span className="latency-text" style={{ color }}>
      {pct.toFixed(1)}%
    </span>
  );
}

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------
export default function UrlList({ urls, onDeleteUrl, onViewHistory }) {
  if (urls.length === 0) {
    return (
      <div className="glass-panel empty-state">
        <AlertCircle className="empty-icon" />
        <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', fontWeight: 700 }}>No Monitored Endpoints</h3>
        <p style={{ fontSize: '0.9rem' }}>Add a URL above (e.g., https://example.com) to begin automated status checks.</p>
      </div>
    );
  }

  return (
    <div className="glass-panel" style={{ padding: '0.5rem 0' }}>
      <div className="table-container">
        <table className="url-table">
          <thead>
            <tr>
              <th>Target Endpoint</th>
              <th>Status</th>
              <th>HTTP Code</th>
              <th>Response Time</th>
              <th>Uptime %</th>
              <th>Checks</th>
              <th>Last Checked</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {urls.map((item) => (
              <tr key={item.id}>
                <td>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                    {item.name && (
                      <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--primary)' }}>
                        {item.name}
                      </span>
                    )}
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noreferrer"
                      className="url-link"
                    >
                      <span>{item.url}</span>
                      <ExternalLink size={13} style={{ opacity: 0.5 }} />
                    </a>
                  </div>
                </td>
                <td><StatusBadge isUp={item.is_up} /></td>
                <td>
                  {item.last_status_code ? (
                    <span className="latency-text">{item.last_status_code}</span>
                  ) : (
                    <span style={{ color: 'var(--text-dim)' }}>
                      {item.is_up === false ? 'Fail' : '—'}
                    </span>
                  )}
                </td>
                <td><Latency ms={item.last_response_time_ms} isUp={item.is_up} /></td>
                <td><UptimePill pct={item.uptime_percentage} /></td>
                <td>
                  <span className="latency-text" style={{ color: 'var(--text-muted)' }}>
                    {item.total_checks ?? 0}
                  </span>
                </td>
                <td className="time-text">{relativeTime(item.last_checked_at)}</td>
                <td style={{ textAlign: 'right' }}>
                  <div style={{ display: 'inline-flex', gap: '0.35rem' }}>
                    <button
                      className="action-btn action-btn-info"
                      onClick={() => onViewHistory(item)}
                      title="View Check History"
                      aria-label={`View check history for ${item.url}`}
                    >
                      <History size={16} />
                    </button>
                    <button
                      className="action-btn action-btn-danger"
                      onClick={() => onDeleteUrl(item.id, item.url)}
                      title="Delete Monitor"
                      aria-label={`Delete monitor for ${item.url}`}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
