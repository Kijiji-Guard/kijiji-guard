import { useState, useEffect } from 'react'
import type { HistoryEntry, ScanResult, View } from '../types'
import { api } from '../api'

interface Props {
  setLastScanResult: (r: ScanResult) => void
  setActiveView: (v: View) => void
}

function passRateColor(rate: number) {
  if (rate >= 70) return 'var(--pass)'
  if (rate >= 50) return 'var(--warn)'
  return 'var(--fail)'
}

export default function History({ setLastScanResult, setActiveView }: Props) {
  const [entries,  setEntries]  = useState<HistoryEntry[]>([])
  const [loading,  setLoading]  = useState(true)
  const [error,    setError]    = useState<string | null>(null)
  const [loading2, setLoading2] = useState<string | null>(null)

  useEffect(() => {
    api.history()
      .then(setEntries)
      .catch(e => setError(e instanceof Error ? e.message : 'Could not load history'))
      .finally(() => setLoading(false))
  }, [])

  async function viewDetails(id: string) {
    setLoading2(id)
    try {
      const full = await api.scanById(id)
      setLastScanResult(full)
      setActiveView('overview')
    } catch {
      alert('Could not load scan details.')
    } finally {
      setLoading2(null)
    }
  }

  return (
    <>
      <div className="page-header">
        <div className="page-title">Scan history</div>
        <div className="page-sub">Last 20 scans</div>
      </div>

      {loading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '24px 0', color: 'var(--text-tertiary)' }}>
          <span className="spinner spinner-dark" />
          Loading…
        </div>
      )}

      {error && (
        <div className="api-error-banner">
          <strong>Could not load scan history</strong>
          <span>{error}</span>
        </div>
      )}

      {!loading && !error && entries.length === 0 && (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon"><ClockEmptyIcon /></div>
            <div className="empty-state-title">No scan history yet</div>
            <div className="empty-state-sub">Run a scan to see it appear here.</div>
          </div>
        </div>
      )}

      {!loading && entries.length > 0 && (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Target</th>
                <th>Country</th>
                <th>Checks</th>
                <th>Pass rate</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {entries.map(e => (
                <tr key={e.id}>
                  <td style={{ whiteSpace: 'nowrap', color: 'var(--text-secondary)', fontSize: 12 }}>
                    {new Date(e.timestamp).toLocaleString(undefined, {
                      month: 'short', day: 'numeric',
                      hour: '2-digit', minute: '2-digit',
                    })}
                  </td>
                  <td className="col-mono">{e.target}</td>
                  <td>{e.country}</td>
                  <td style={{ color: 'var(--text-secondary)' }}>{e.summary.total}</td>
                  <td>
                    <span style={{
                      fontWeight: 600,
                      color: passRateColor(e.summary.pass_rate),
                    }}>
                      {e.summary.pass_rate}%
                    </span>
                  </td>
                  <td>
                    <button
                      className="link-btn"
                      onClick={() => viewDetails(e.id)}
                      disabled={loading2 === e.id}
                    >
                      {loading2 === e.id ? 'Loading…' : 'View details'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}

function ClockEmptyIcon() {
  return (
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  )
}
