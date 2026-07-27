import React, { useEffect, useState } from 'react';
import { fetchUrlChecks } from '../api';
import { History, X, CheckCircle, XCircle } from 'lucide-react';

export default function CheckHistoryModal({ urlItem, onClose }) {
  const [checks, setChecks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadChecks() {
      try {
        setLoading(true);
        const data = await fetchUrlChecks(urlItem.id, 30);
        setChecks(data);
      } catch (err) {
        setError(err.message || 'Failed to load check history');
      } finally {
        setLoading(false);
      }
    }
    loadChecks();
  }, [urlItem.id]);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <History size={20} color="var(--primary)" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Check History</h3>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div style={{ marginBottom: '1rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          Endpoint: <strong style={{ color: 'var(--text-main)' }}>{urlItem.url}</strong>
        </div>

        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading check history...
          </div>
        ) : error ? (
          <div className="error-banner">{error}</div>
        ) : checks.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            No health checks recorded yet.
          </div>
        ) : (
          <div className="table-container">
            <table className="url-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>HTTP Code</th>
                  <th>Latency</th>
                  <th>Timestamp (UTC)</th>
                </tr>
              </thead>
              <tbody>
                {checks.map((chk) => (
                  <tr key={chk.id}>
                    <td>
                      {chk.is_up ? (
                        <span className="badge badge-up">
                          <CheckCircle size={12} /> UP
                        </span>
                      ) : (
                        <span className="badge badge-down">
                          <XCircle size={12} /> DOWN
                        </span>
                      )}
                    </td>
                    <td>
                      {chk.status_code ? (
                        <span className="latency-text">{chk.status_code}</span>
                      ) : (
                        <span style={{ color: 'var(--text-dim)' }}>None (Failed)</span>
                      )}
                    </td>
                    <td>
                      {chk.response_time_ms !== null ? (
                        <span className="latency-text">{chk.response_time_ms} ms</span>
                      ) : (
                        '—'
                      )}
                    </td>
                    <td className="time-text">
                      {new Date(chk.checked_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
