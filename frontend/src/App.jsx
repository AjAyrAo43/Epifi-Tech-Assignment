import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import StatsOverview from './components/StatsOverview';
import AddUrlForm from './components/AddUrlForm';
import UrlList from './components/UrlList';
import CheckHistoryModal from './components/CheckHistoryModal';
import { fetchUrls, addUrl, deleteUrl } from './api';

const POLL_INTERVAL_MS = 5000;

export default function App() {
  const [urls, setUrls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);
  const [selectedUrlForHistory, setSelectedUrlForHistory] = useState(null);
  const [toasts, setToasts] = useState([]);

  // ------------------------------------------------------------------
  // Toast notification helpers
  // ------------------------------------------------------------------
  const pushToast = useCallback((message, type = 'success') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3500);
  }, []);

  // ------------------------------------------------------------------
  // Data polling
  // ------------------------------------------------------------------
  const loadUrls = useCallback(async (isInitial = false) => {
    try {
      if (isInitial) setLoading(true);
      const data = await fetchUrls();
      setUrls(data);
      setLastUpdated(new Date());
      setFetchError('');
    } catch (err) {
      console.error('Polling error:', err);
      setFetchError(err.message || 'Unable to connect to monitoring service.');
    } finally {
      if (isInitial) setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUrls(true);
    const interval = setInterval(() => loadUrls(false), POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [loadUrls]);

  // ------------------------------------------------------------------
  // Handlers
  // ------------------------------------------------------------------
  const handleAddUrl = async (urlStr, name) => {
    await addUrl(urlStr, name);
    await loadUrls(false);
    pushToast(`Now monitoring ${urlStr}`, 'success');
  };

  const handleDeleteUrl = async (id, urlStr) => {
    if (!window.confirm('Stop monitoring this URL?')) return;
    try {
      await deleteUrl(id);
      setUrls(prev => prev.filter(u => u.id !== id));
      pushToast(`Removed ${urlStr || 'URL'} from monitoring.`, 'info');
    } catch (err) {
      pushToast(err.message || 'Failed to delete URL', 'error');
    }
  };

  // ------------------------------------------------------------------
  // Render
  // ------------------------------------------------------------------
  return (
    <div className="container">
      <Navbar lastUpdated={lastUpdated} />

      {fetchError && (
        <div className="error-banner" style={{ marginBottom: '1.5rem' }}>
          <strong>Service Alert:</strong> {fetchError} (Retrying every 5s…)
        </div>
      )}

      <StatsOverview urls={urls} />

      <AddUrlForm onAddUrl={handleAddUrl} />

      {loading ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading monitored targets…
        </div>
      ) : (
        <UrlList
          urls={urls}
          onDeleteUrl={handleDeleteUrl}
          onViewHistory={(item) => setSelectedUrlForHistory(item)}
        />
      )}

      {selectedUrlForHistory && (
        <CheckHistoryModal
          urlItem={selectedUrlForHistory}
          onClose={() => setSelectedUrlForHistory(null)}
        />
      )}

      {/* Toast notifications */}
      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast toast-${t.type}`}>
            {t.message}
          </div>
        ))}
      </div>
    </div>
  );
}
