import { useState } from 'react'
import type { ScanResult, Finding, View } from '../types'
import { api } from '../api'

interface Props {
  setLastScanResult: (r: ScanResult) => void
  setActiveView: (v: View) => void
  isConnected: boolean
}

type FilterResult = 'all' | 'FAILED' | 'WARN' | 'PASSED' | 'INFO'

const TARGETS = [
  { value: 'auto',         label: 'Auto-detect' },
  { value: 'vercel',       label: 'Vercel' },
  { value: 'supabase',     label: 'Supabase' },
  { value: 'aws',          label: 'AWS (Live API)' },
  { value: 'gcp',          label: 'GCP (Live API)' },
  { value: 'azure',        label: 'Azure (Live API)' },
  { value: 'digitalocean', label: 'DigitalOcean' },
  { value: 'firebase',     label: 'Firebase' },
  { value: 'render',       label: 'Render' },
  { value: 'railway',      label: 'Railway' },
  { value: 'custom',       label: 'Browse file/path…' },
]

const COUNTRIES = [
  { value: 'nigeria',      label: 'Nigeria (NDPA 2023)' },
  { value: 'ghana',        label: 'Ghana (DPA 2012)' },
  { value: 'kenya',        label: 'Kenya (DPA 2019)' },
  { value: 'rwanda',       label: 'Rwanda (Law 058/2021)' },
  { value: 'cote-divoire', label: "Côte d'Ivoire (Loi 2013-450)" },
  { value: 'benin',        label: 'Bénin (Loi 2017-20)' },
  { value: 'egypt',        label: 'Egypt (PDPL 2020)' },
  { value: 'all',          label: 'All countries' },
]

function resultBadgeClass(result: Finding['result']) {
  if (result === 'PASSED') return 'badge badge-pass'
  if (result === 'FAILED') return 'badge badge-fail'
  if (result === 'WARN')   return 'badge badge-warn'
  return 'badge badge-info'
}

export default function RunScan({ setLastScanResult, setActiveView, isConnected }: Props) {
  const [target,   setTarget]   = useState('auto')
  const [customPath, setCustomPath] = useState('.')
  const [country,  setCountry]  = useState('nigeria')
  const [credOpen, setCredOpen] = useState(false)
  const [creds,    setCreds]    = useState<Record<string, string>>({})

  const [scanning,  setScanning]  = useState(false)
  const [result,    setResult]    = useState<ScanResult | null>(null)
  const [error,     setError]     = useState<string | null>(null)
  const [filter,    setFilter]    = useState<FilterResult>('all')
  const [expandedRow, setExpandedRow] = useState<string | null>(null)

  async function runScan() {
    if (!isConnected) return
    setScanning(true)
    setError(null)
    setResult(null)
    const effectiveTarget = target === 'custom' ? customPath : target
    try {
      const data = await api.scan(effectiveTarget, country, creds)
      setResult(data)
      setLastScanResult(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Scan failed — is the API server running?')
    } finally {
      setScanning(false)
    }
  }

  function updateCred(key: string, value: string) {
    setCreds(prev => ({ ...prev, [key]: value }))
  }

  const credFields: { target: string; fields: { key: string; label: string }[] }[] = [
    { target: 'vercel',       fields: [{ key: 'vercel_token',           label: 'VERCEL_TOKEN' }] },
    { target: 'supabase',     fields: [{ key: 'supabase_token',         label: 'SUPABASE_ACCESS_TOKEN' }] },
    { target: 'aws',          fields: [{ key: 'aws_access_key_id',      label: 'AWS_ACCESS_KEY_ID' },
                                        { key: 'aws_secret_access_key', label: 'AWS_SECRET_ACCESS_KEY' }] },
    { target: 'digitalocean', fields: [{ key: 'digitalocean_token',     label: 'DIGITALOCEAN_TOKEN' }] },
  ]
  const activeCreds = credFields.find(c => c.target === target)

  const findings = result?.findings ?? []
  const filtered = filter === 'all' ? findings : findings.filter(f => f.result === filter)

  const counts = {
    all:    findings.length,
    FAILED: findings.filter(f => f.result === 'FAILED').length,
    WARN:   findings.filter(f => f.result === 'WARN').length,
    PASSED: findings.filter(f => f.result === 'PASSED').length,
    INFO:   findings.filter(f => f.result === 'INFO').length,
  }

  return (
    <>
      <div className="page-header">
        <div className="page-title">Run scan</div>
        <div className="page-sub">Scan your infrastructure for compliance violations</div>
      </div>

      {!isConnected && (
        <div className="api-error-banner">
          <strong>API server not running</strong>
          <span>Start it with: <code>py -m uvicorn cli.api_server:app --reload --port 8000</code></span>
        </div>
      )}

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">Target</label>
            <select className="form-select" value={target} onChange={e => setTarget(e.target.value)}>
              {TARGETS.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Country / Regulation</label>
            <select className="form-select" value={country} onChange={e => setCountry(e.target.value)}>
              {COUNTRIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
            </select>
          </div>
        </div>

        {target === 'custom' && (
          <div className="form-group" style={{ marginBottom: 14 }}>
            <label className="form-label">File or directory path</label>
            <input
              className="form-input"
              value={customPath}
              onChange={e => setCustomPath(e.target.value)}
              placeholder="e.g. ./terraform or ./infra/main.tf"
            />
          </div>
        )}

        {/* Credentials (collapsible) */}
        {activeCreds && (
          <div style={{ marginBottom: 14 }}>
            <button className="collapsible-toggle" onClick={() => setCredOpen(o => !o)}>
              <span>{credOpen ? '▾' : '▸'}</span>
              Advanced — credentials
            </button>
            {credOpen && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {activeCreds.fields.map(({ key, label }) => (
                  <div className="form-group" key={key}>
                    <label className="form-label">{label}</label>
                    <input
                      type="password"
                      className="form-input"
                      value={creds[key] ?? ''}
                      onChange={e => updateCred(key, e.target.value)}
                      placeholder="••••••••••••••••"
                    />
                  </div>
                ))}
                <p className="form-hint">
                  Tokens are sent to your local API server only. Never stored in the browser.
                </p>
              </div>
            )}
          </div>
        )}

        <button
          className="btn btn-primary btn-lg"
          onClick={runScan}
          disabled={scanning || !isConnected}
          style={{ minWidth: 140 }}
        >
          {scanning ? (
            <>
              <span className="spinner" />
              Scanning…
            </>
          ) : 'Run scan'}
        </button>
      </div>

      {scanning && (
        <div className="scan-running">
          <span className="spinner spinner-dark" />
          <span>Scanning <strong>{target}</strong> for <strong>{country}</strong> compliance…</span>
        </div>
      )}

      {error && (
        <div className="api-error-banner" style={{ marginBottom: 16 }}>
          <strong>Scan error</strong>
          <span>{error}</span>
        </div>
      )}

      {result && (
        <>
          {/* Summary bar */}
          <div className="summary-bar">
            <div className="summary-bar-item">
              <span className="summary-bar-num" style={{ color: 'var(--pass)' }}>{result.summary.passed}</span>
              <span style={{ color: 'var(--text-secondary)' }}>passed</span>
            </div>
            <span style={{ color: 'var(--border-strong)' }}>·</span>
            <div className="summary-bar-item">
              <span className="summary-bar-num" style={{ color: result.summary.failed > 0 ? 'var(--fail)' : undefined }}>
                {result.summary.failed}
              </span>
              <span style={{ color: 'var(--text-secondary)' }}>failed</span>
            </div>
            <span style={{ color: 'var(--border-strong)' }}>·</span>
            <div className="summary-bar-item">
              <span className="summary-bar-num" style={{ color: 'var(--warn)' }}>
                {findings.filter(f => f.result === 'WARN').length}
              </span>
              <span style={{ color: 'var(--text-secondary)' }}>warnings</span>
            </div>
            <span style={{ color: 'var(--border-strong)' }}>·</span>
            <div className="summary-bar-item">
              <span className="summary-bar-num">{result.summary.pass_rate}%</span>
              <span style={{ color: 'var(--text-secondary)' }}>pass rate</span>
            </div>
            <div style={{ marginLeft: 'auto' }}>
              <button
                className="btn btn-sm"
                onClick={() => { setLastScanResult(result); setActiveView('overview') }}
              >
                View in Overview
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="filter-bar">
            {(['all', 'FAILED', 'WARN', 'PASSED', 'INFO'] as const).map(f => (
              <button
                key={f}
                className={`filter-pill ${filter === f ? 'active' : ''}`}
                onClick={() => setFilter(f)}
              >
                {f === 'all' ? 'All' : f}
                <span className="pill-count">{counts[f]}</span>
              </button>
            ))}
          </div>

          {/* Findings table */}
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Check ID</th>
                  <th>Name</th>
                  <th>Resource</th>
                  <th>Regulation</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((f, i) => {
                  const rowKey = `${f.check_id}-${i}`
                  const isExpanded = expandedRow === rowKey
                  return (
                    <>
                      <tr
                        key={rowKey}
                        className={isExpanded ? 'expanded' : ''}
                        style={{ cursor: 'pointer' }}
                        onClick={() => setExpandedRow(isExpanded ? null : rowKey)}
                      >
                        <td><span className={resultBadgeClass(f.result)}>{f.result}</span></td>
                        <td className="col-mono">{f.check_id}</td>
                        <td>{f.check_name}</td>
                        <td className="col-muted">{f.resource}</td>
                        <td className="col-muted">{f.regulation}</td>
                      </tr>
                      {isExpanded && (
                        <tr key={`${rowKey}-rem`} className="remediation-row">
                          <td colSpan={5}>
                            <div className="remediation-label">Remediation</div>
                            {f.remediation}
                          </td>
                        </tr>
                      )}
                    </>
                  )
                })}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-tertiary)', padding: 24 }}>
                      No findings match this filter.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  )
}
