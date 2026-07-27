import React, { useState } from 'react';
import { PlusCircle, Loader2 } from 'lucide-react';

export default function AddUrlForm({ onAddUrl }) {
  const [inputUrl, setInputUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputUrl.trim()) return;

    setError('');
    setLoading(true);

    try {
      await onAddUrl(inputUrl.trim());
      setInputUrl('');
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
            type="text"
            className="url-input"
            placeholder="e.g. https://example.com or api.github.com"
            value={inputUrl}
            onChange={(e) => setInputUrl(e.target.value)}
            disabled={loading}
            required
          />
          <button type="submit" className="submit-btn" disabled={loading || !inputUrl.trim()}>
            {loading ? <Loader2 size={16} className="spin" /> : <PlusCircle size={16} />}
            <span>{loading ? 'Adding...' : 'Add Monitor'}</span>
          </button>
        </div>
        {error && <div className="error-banner">{error}</div>}
      </form>
    </div>
  );
}
