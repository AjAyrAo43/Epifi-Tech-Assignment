import React from 'react';
import { ExternalLink, Trash2, History, AlertCircle, CheckCircle2, Clock } from 'lucide-react';

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

  const renderStatusBadge = (isUp) => {
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
  };

  const renderLatency = (ms, isUp) => {
    if (ms === null || ms === undefined) return <span style={{ color: 'var(--text-dim)' }}>—</span>;
    let colorClass = 'latency-good';
    if (!isUp) colorClass = 'latency-bad';
    else if (ms > 1000) colorClass = 'latency-warn';

    return <span className={`latency-text ${colorClass}`}>{ms} ms</span>;
  };

  const formatTimestamp = (ts) => {
    if (!ts) return 'Pending check...';
    try {
      const date = new Date(ts);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch (_) {
      return ts;
    }
  };

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
              <th>Last Checked</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {urls.map((item) => (
              <tr key={item.id}>
                <td>
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="url-link"
                  >
                    <span>{item.url}</span>
                    <ExternalLink size={14} style={{ opacity: 0.6 }} />
                  </a>
                </td>
                <td>{renderStatusBadge(item.is_up)}</td>
                <td>
                  {item.last_status_code ? (
                    <span className="latency-text">{item.last_status_code}</span>
                  ) : (
                    <span style={{ color: 'var(--text-dim)' }}>
                      {item.is_up === false ? 'Fail' : '—'}
                    </span>
                  )}
                </td>
                <td>{renderLatency(item.last_response_time_ms, item.is_up)}</td>
                <td className="time-text">{formatTimestamp(item.last_checked_at)}</td>
                <td style={{ textAlign: 'right' }}>
                  <div style={{ display: 'inline-flex', gap: '0.35rem' }}>
                    <button
                      className="action-btn action-btn-info"
                      onClick={() => onViewHistory(item)}
                      title="View Check History"
                    >
                      <History size={16} />
                    </button>
                    <button
                      className="action-btn action-btn-danger"
                      onClick={() => onDeleteUrl(item.id)}
                      title="Delete Monitor"
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
