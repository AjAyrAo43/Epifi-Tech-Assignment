import React from 'react';
import { Activity } from 'lucide-react';

export default function Navbar({ lastUpdated }) {
  return (
    <header className="navbar glass-panel">
      <div className="brand">
        <div className="brand-icon">
          <Activity size={24} />
        </div>
        <div>
          <h1 className="brand-title">PulseGuard</h1>
        </div>
      </div>
      <div className="live-indicator">
        <span className="pulse-dot"></span>
        <span>LIVE POLLING</span>
        {lastUpdated && (
          <span style={{ opacity: 0.6, fontSize: '0.75rem', marginLeft: '0.3rem' }}>
            ({lastUpdated.toLocaleTimeString()})
          </span>
        )}
      </div>
    </header>
  );
}
