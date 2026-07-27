import React from 'react';
import { Globe, CheckCircle2, AlertTriangle, Clock } from 'lucide-react';

export default function StatsOverview({ urls }) {
  const total = urls.length;
  const upCount = urls.filter(u => u.is_up === true).length;
  const downCount = urls.filter(u => u.is_up === false).length;
  
  const validLatencies = urls
    .filter(u => u.is_up === true && typeof u.last_response_time_ms === 'number')
    .map(u => u.last_response_time_ms);
    
  const avgLatency = validLatencies.length > 0
    ? Math.round(validLatencies.reduce((a, b) => a + b, 0) / validLatencies.length)
    : 0;

  return (
    <div className="stats-grid">
      <div className="stat-card glass-panel">
        <div className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Globe size={16} color="var(--primary)" /> Monitored Targets
        </div>
        <div className="stat-value" style={{ color: 'var(--text-main)' }}>{total}</div>
      </div>

      <div className="stat-card glass-panel">
        <div className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <CheckCircle2 size={16} color="var(--success)" /> Operational (UP)
        </div>
        <div className="stat-value" style={{ color: 'var(--success)' }}>{upCount}</div>
      </div>

      <div className="stat-card glass-panel">
        <div className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <AlertTriangle size={16} color="var(--danger)" /> Degraded (DOWN)
        </div>
        <div className="stat-value" style={{ color: downCount > 0 ? 'var(--danger)' : 'var(--text-muted)' }}>
          {downCount}
        </div>
      </div>

      <div className="stat-card glass-panel">
        <div className="stat-label" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Clock size={16} color="var(--warning)" /> Avg Latency
        </div>
        <div className="stat-value" style={{ color: 'var(--primary)' }}>
          {avgLatency > 0 ? `${avgLatency} ms` : '—'}
        </div>
      </div>
    </div>
  );
}
