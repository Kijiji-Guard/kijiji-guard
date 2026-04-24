import { useState, useEffect } from 'react'
import type { ReactElement } from 'react'
import type { View, ScanResult } from '../types'
import { api } from '../api'

interface Props {
  activeView: View
  setActiveView: (v: View) => void
  lastScanResult: ScanResult | null
  isConnected: boolean
}

const NAV: { id: View; label: string; icon: ReactElement; showBadge?: boolean }[] = [
  { id: 'overview',     label: 'Overview',            icon: <GridIcon /> },
  { id: 'scan',         label: 'Run scan',             icon: <PlayIcon /> },
  { id: 'findings',     label: 'Findings',             icon: <ListIcon /> },
  { id: 'history',      label: 'Scan history',         icon: <ClockIcon /> },
  { id: 'watch',        label: 'Regulatory Watch',     icon: <BellIcon />, showBadge: true },
  { id: 'regulations',  label: 'Regulations',          icon: <BookIcon /> },
  { id: 'export',       label: 'Export report',        icon: <DownloadIcon /> },
]

export default function Sidebar({ activeView, setActiveView, lastScanResult, isConnected }: Props) {
  const [highCount, setHighCount] = useState(0)

  useEffect(() => {
    fetchHighCount()
    const interval = setInterval(fetchHighCount, 30 * 60 * 1000) // every 30 min
    return () => clearInterval(interval)
  }, [])

  function fetchHighCount() {
    api.watchAll('all')
      .then(r => setHighCount(r.by_severity?.HIGH ?? 0))
      .catch(() => {})
  }

  const lastTs = lastScanResult
    ? new Date(lastScanResult.timestamp).toLocaleString(undefined, {
        month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit',
      })
    : null

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-name">
          <ShieldIcon />
          Kijiji-Guard
        </div>
        <div className="sidebar-brand-sub">
          <span className="version-badge">v0.1.0</span>
          <span>local</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV.map(({ id, label, icon, showBadge }) => (
          <button
            key={id}
            className={`nav-item ${activeView === id ? 'active' : ''}`}
            onClick={() => setActiveView(id)}
          >
            {icon}
            <span style={{ flex: 1, textAlign: 'left' }}>{label}</span>
            {showBadge && highCount > 0 && (
              <span style={{
                fontSize: 10,
                fontWeight: 700,
                background: 'var(--fail)',
                color: '#fff',
                padding: '1px 6px',
                borderRadius: 20,
                lineHeight: 1.6,
              }}>
                {highCount}
              </span>
            )}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="status-row">
          <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`} />
          <span>{isConnected ? 'API connected' : 'Start API server'}</span>
        </div>
        {!isConnected && (
          <div className="status-hint">
            py -m uvicorn cli.api_server:app{'\n'}--reload --port 8000
          </div>
        )}
        {lastTs && (
          <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-tertiary)' }}>
            Last scan: {lastTs}
          </div>
        )}
      </div>
    </aside>
  )
}

function ShieldIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  )
}
function GridIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
      <rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" />
    </svg>
  )
}
function PlayIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="5 3 19 12 5 21 5 3" />
    </svg>
  )
}
function ListIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="8" y1="6" x2="21" y2="6" /><line x1="8" y1="12" x2="21" y2="12" />
      <line x1="8" y1="18" x2="21" y2="18" />
      <line x1="3" y1="6" x2="3.01" y2="6" /><line x1="3" y1="12" x2="3.01" y2="12" />
      <line x1="3" y1="18" x2="3.01" y2="18" />
    </svg>
  )
}
function ClockIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  )
}
function BellIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  )
}
function BookIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
    </svg>
  )
}
function DownloadIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  )
}
