import { useState } from 'react'
import type { ScanResult, Finding, View } from '../types'

interface Props {
  lastScanResult: ScanResult | null
  setActiveView: (v: View) => void
  isConnected: boolean
}

const TARGETS = ['auto', 'vercel', 'supabase', 'aws', 'gcp', 'azure', 'digitalocean', 'firebase', 'render', 'railway']
const COUNTRIES = [
  { value: 'nigeria', label: 'Nigeria' },
  { value: 'ghana', label: 'Ghana' },
  { value: 'kenya', label: 'Kenya' },
  { value: 'rwanda', label: 'Rwanda' },
  { value: 'cote-divoire', label: "Côte d'Ivoire" },
  { value: 'benin', label: 'Bénin' },
  { value: 'egypt', label: 'Egypt' },
  { value: 'all', label: 'All countries' },
]

function passRateColor(rate: number) {
  if (rate >= 70) return 'var(--pass)'
  if (rate >= 50) return 'var(--warn)'
  return 'var(--fail)'
}

function resultBadgeClass(result: Finding['result']) {
  if (result === 'PASSED') return 'badge badge-pass'
  if (result === 'FAILED') return 'badge badge-fail'
  if (result === 'WARN')   return 'badge badge-warn'
  return 'badge badge-info'
}

function regulationPrefix(reg: string) {
  return reg.split(',')[0].trim()
}

function groupByRegulation(findings: Finding[]) {
  const groups: Record<string, { passed: number; total: number }> = {}
  for (const f of findings) {
    const key = regulationPrefix(f.regulation)
    if (!groups[key]) groups[key] = { passed: 0, total: 0 }
    groups[key].total++
    if (f.result === 'PASSED') groups[key].passed++
  }
  return groups
}

export default function Overview({ lastScanResult, setActiveView, isConnected }: Props) {
  const [quickTarget, setQuickTarget]   = useState('auto')
  const [quickCountry, setQuickCountry] = useState('nigeria')

  if (!lastScanResult) {
    return (
      <>
        <div className="page-header">
          <div className="page-title">Overview</div>
          <div className="page-sub">Compliance posture at a glance</div>
        </div>
        {!isConnected && (
          <div className="api-error-banner">
            <strong>API server not running</strong>
            <span>Start it with: <code>py -m uvicorn cli.api_server:app --reload --port 8000</code></span>
          </div>
        )}
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon">
              <ShieldEmptyIcon />
            </div>
            <div className="empty-state-title">No scans yet</div>
            <div className="empty-state-sub">
              Run your first scan to see your compliance posture here.
            </div>
            <button className="btn btn-primary btn-lg" onClick={() => setActiveView('scan')}>
              Run your first scan
            </button>
          </div>
        </div>
      </>
    )
  }

  const { summary, findings, target, country, scan_types, timestamp } = lastScanResult
  const warned = findings.filter(f => f.result === 'WARN').length
  const critical = [...findings]
    .filter(f => f.result === 'FAILED' || f.result === 'WARN')
    .sort((a, b) => (a.result === 'FAILED' ? -1 : 1) - (b.result === 'FAILED' ? -1 : 1))
    .slice(0, 5)
  const regGroups = groupByRegulation(findings)
  const ts = new Date(timestamp).toLocaleString(undefined, {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })

  return (
    <>
      <div className="page-header">
        <div className="page-title">Overview</div>
        <div className="page-sub">Compliance posture at a glance</div>
      </div>

      {/* Metric cards */}
      <div className="metric-grid">
        <div className="metric-card">
          <div className="metric-label">Pass rate</div>
          <div className="metric-value" style={{ color: passRateColor(summary.pass_rate) }}>
            {summary.pass_rate}%
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Total checks</div>
          <div className="metric-value">{summary.total}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Failed</div>
          <div className="metric-value" style={{ color: summary.failed > 0 ? 'var(--fail)' : undefined }}>
            {summary.failed}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Warnings</div>
          <div className="metric-value" style={{ color: warned > 0 ? 'var(--warn)' : undefined }}>
            {warned}
          </div>
        </div>
      </div>

      {/* Two-column section */}
      <div className="two-col">
        {/* Left: critical findings */}
        <div className="card">
          <div className="section-title">Critical findings</div>
          {critical.length === 0 ? (
            <div style={{ fontSize: 13, color: 'var(--pass)', padding: '8px 0' }}>
              All checks passed — no critical findings.
            </div>
          ) : (
            <>
              {critical.map((f, i) => (
                <div className="finding-item" key={i}>
                  <span className={`finding-dot ${f.result === 'FAILED' ? 'fail' : 'warn'}`} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div className="finding-name">{f.check_name}</div>
                    <div className="finding-meta">
                      {f.resource} · {f.check_id} · {regulationPrefix(f.regulation)}
                    </div>
                  </div>
                  <span className={resultBadgeClass(f.result)}>{f.result}</span>
                </div>
              ))}
              <button
                className="link-btn"
                style={{ marginTop: 10, display: 'block' }}
                onClick={() => setActiveView('findings')}
              >
                View all findings →
              </button>
            </>
          )}
        </div>

        {/* Right: regulation bars + quick scan */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div className="card">
            <div className="section-title">Compliance by regulation</div>
            {Object.entries(regGroups).map(([reg, { passed, total }]) => {
              const pct = total > 0 ? Math.round((passed / total) * 100) : 0
              const color = pct >= 70 ? 'var(--pass)' : pct >= 50 ? 'var(--warn)' : 'var(--fail)'
              return (
                <div className="progress-row" key={reg}>
                  <div className="progress-label" title={reg}>{reg}</div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${pct}%`, background: color }} />
                  </div>
                  <div className="progress-pct">{pct}%</div>
                </div>
              )
            })}
            {Object.keys(regGroups).length === 0 && (
              <div style={{ fontSize: 13, color: 'var(--text-tertiary)' }}>No findings grouped yet.</div>
            )}
          </div>

          <div className="card">
            <div className="section-title">Quick scan</div>
            <div className="quick-scan-row">
              <div className="form-group">
                <label className="form-label">Target</label>
                <select className="form-select" value={quickTarget} onChange={e => setQuickTarget(e.target.value)}>
                  {TARGETS.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Country</label>
                <select className="form-select" value={quickCountry} onChange={e => setQuickCountry(e.target.value)}>
                  {COUNTRIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                </select>
              </div>
              <button
                className="btn btn-primary"
                onClick={() => setActiveView('scan')}
                style={{ marginTop: 18 }}
              >
                Run scan
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Scan info bar */}
      <div className="scan-info-bar">
        <span>Scanned:</span>
        <strong>{scan_types.join(', ')}</strong>
        <span>·</span>
        <span>{ts}</span>
        <span>·</span>
        <strong>{country}</strong>
        <span style={{ marginLeft: 4 }}>({target})</span>
      </div>
    </>
  )
}

function ShieldEmptyIcon() {
  return (
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  )
}
