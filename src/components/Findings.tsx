import { useState } from 'react'
import type { ScanResult, Finding } from '../types'
import { api } from '../api'

interface Props {
  lastScanResult: ScanResult | null
}

type FilterResult = 'all' | 'FAILED' | 'WARN' | 'PASSED' | 'INFO'
type SortKey = 'severity' | 'check_id' | 'regulation'

function resultBadgeClass(result: Finding['result']) {
  if (result === 'PASSED') return 'badge badge-pass'
  if (result === 'FAILED') return 'badge badge-fail'
  if (result === 'WARN')   return 'badge badge-warn'
  return 'badge badge-info'
}

const SEVERITY_ORDER: Record<Finding['result'], number> = {
  FAILED: 0, WARN: 1, INFO: 2, PASSED: 3,
}

function sortFindings(findings: Finding[], key: SortKey): Finding[] {
  return [...findings].sort((a, b) => {
    if (key === 'severity')   return SEVERITY_ORDER[a.result] - SEVERITY_ORDER[b.result]
    if (key === 'check_id')   return a.check_id.localeCompare(b.check_id)
    if (key === 'regulation') return a.regulation.localeCompare(b.regulation)
    return 0
  })
}

function downloadBlob(content: string, filename: string, type: string) {
  const blob = new Blob([content], { type })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export default function Findings({ lastScanResult }: Props) {
  const [filter,       setFilter]       = useState<FilterResult>('all')
  const [search,       setSearch]       = useState('')
  const [sort,         setSort]         = useState<SortKey>('severity')
  const [expandedRow,  setExpandedRow]  = useState<string | null>(null)
  const [htmlLoading,  setHtmlLoading]  = useState(false)

  if (!lastScanResult) {
    return (
      <>
        <div className="page-header">
          <div className="page-title">Findings</div>
          <div className="page-sub">Browse and filter all compliance check results</div>
        </div>
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon"><ListEmptyIcon /></div>
            <div className="empty-state-title">No scan results</div>
            <div className="empty-state-sub">Run a scan first to browse findings here.</div>
          </div>
        </div>
      </>
    )
  }

  const findings = lastScanResult.findings
  const counts = {
    all:    findings.length,
    FAILED: findings.filter(f => f.result === 'FAILED').length,
    WARN:   findings.filter(f => f.result === 'WARN').length,
    PASSED: findings.filter(f => f.result === 'PASSED').length,
    INFO:   findings.filter(f => f.result === 'INFO').length,
  }

  const filtered = sortFindings(
    findings.filter(f => {
      const matchFilter = filter === 'all' || f.result === filter
      const q = search.toLowerCase()
      const matchSearch = !q ||
        f.check_name.toLowerCase().includes(q) ||
        f.resource.toLowerCase().includes(q) ||
        f.check_id.toLowerCase().includes(q)
      return matchFilter && matchSearch
    }),
    sort,
  )

  async function downloadHtml() {
    setHtmlLoading(true)
    try {
      const html = await api.htmlReport(lastScanResult!)
      downloadBlob(html, `kijiji-report-${lastScanResult!.country}.html`, 'text/html')
    } catch {
      alert('Could not generate HTML report. Is the API server running?')
    } finally {
      setHtmlLoading(false)
    }
  }

  function downloadJson() {
    downloadBlob(
      JSON.stringify(lastScanResult, null, 2),
      `kijiji-report-${lastScanResult.country}.json`,
      'application/json',
    )
  }

  return (
    <>
      <div className="page-header">
        <div className="page-title">Findings</div>
        <div className="page-sub">
          {lastScanResult.target} · {lastScanResult.country} ·{' '}
          {new Date(lastScanResult.timestamp).toLocaleDateString()}
        </div>
      </div>

      {/* Toolbar */}
      <div className="filter-bar" style={{ marginBottom: 10 }}>
        <input
          className="search-input"
          placeholder="Search by name or resource…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
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
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>Sort:</span>
          <select
            className="form-select"
            value={sort}
            onChange={e => setSort(e.target.value as SortKey)}
            style={{ padding: '4px 8px', fontSize: 12 }}
          >
            <option value="severity">Severity</option>
            <option value="check_id">Check ID</option>
            <option value="regulation">Regulation</option>
          </select>
        </div>
      </div>

      {/* Export buttons */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
        <button className="btn btn-sm" onClick={downloadJson}>
          <DownloadIcon /> Download JSON
        </button>
        <button className="btn btn-sm" onClick={downloadHtml} disabled={htmlLoading}>
          {htmlLoading ? <><span className="spinner spinner-dark" style={{ width: 12, height: 12 }} /> Generating…</> : <><DownloadIcon /> Download HTML report</>}
        </button>
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
              <th>File</th>
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
                    <td className="col-muted col-mono" style={{ maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {f.file_path}
                    </td>
                    <td className="col-muted">{f.regulation}</td>
                  </tr>
                  {isExpanded && (
                    <tr key={`${rowKey}-rem`} className="remediation-row">
                      <td colSpan={6}>
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
                <td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-tertiary)', padding: 24 }}>
                  No findings match this filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  )
}

function ListEmptyIcon() {
  return (
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="8" y1="6" x2="21" y2="6" /><line x1="8" y1="12" x2="21" y2="12" />
      <line x1="8" y1="18" x2="21" y2="18" />
      <line x1="3" y1="6" x2="3.01" y2="6" /><line x1="3" y1="12" x2="3.01" y2="12" />
      <line x1="3" y1="18" x2="3.01" y2="18" />
    </svg>
  )
}

function DownloadIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  )
}
