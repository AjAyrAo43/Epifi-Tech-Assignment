import React, { useState } from 'react';
import { PlusCircle, Loader2 } from 'lucide-react';

export default function AddUrlForm({ onAddUrl }) {
  const [inputUrl, setInputUrl] = useState('');
  const [inputName, setInputName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputUrl.trim()) return;

    setError('');
    setLoading(true);

    try {
      await onAddUrl(inputUrl.trim(), inputName.trim());
      setInputUrl('');
      setInputName('');
    } catch (err) {
      setError(err.message || 'Failed to add URL');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-card glass-panel">
      <div className="form-title">
        <PlusCircle size={18} color="var(--primary)" />
        <span>Register New Endpoint</span>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="url-input-group">
          <input
            id="url-input"
            type="text"
            className="url-input"
            placeholder="https://example.com or api.github.com"
            value={inputUrl}
            onChange={(e) => setInputUrl(e.target.value)}
            disabled={loading}
            required
            aria-label="Target URL to monitor"
          />
          <input
            id="name-input"
            type="text"
            className="url-input name-input"
            placeholder="Friendly name (optional)"
            value={inputName}
            onChange={(e) => setInputName(e.target.value)}
            disabled={loading}
            aria-label="Friendly display name"
          />
          <button
            type="submit"
            className="submit-btn"
            disabled={loading || !inputUrl.trim()}
            aria-label="Add monitor"
          >
            {loading ? <Loader2 size={16} className="spin" /> : <PlusCircle size={16} />}
            <span>{loading ? 'Adding…' : 'Add Monitor'}</span>
          </button>
        </div>
        {error && <div className="error-banner" role="alert">{error}</div>}
      </form>
    </div>
  );
}
