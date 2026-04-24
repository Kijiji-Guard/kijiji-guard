import { useState, useEffect } from 'react'
import type { RegulatoryUpdate, WatchResult } from '../types'
import { api } from '../api'

const COUNTRIES = [
  { value: 'all',          label: 'All',         flag: '🌍' },
  { value: 'nigeria',      label: 'Nigeria',     flag: '🇳🇬' },
  { value: 'ghana',        label: 'Ghana',       flag: '🇬🇭' },
  { value: 'kenya',        label: 'Kenya',       flag: '🇰🇪' },
  { value: 'rwanda',       label: 'Rwanda',      flag: '🇷🇼' },
  { value: 'egypt',        label: 'Egypt',       flag: '🇪🇬' },
  { value: 'benin',        label: 'Bénin',       flag: '🇧🇯' },
  { value: 'cote-divoire', label: "Côte d'Ivoire", flag: '🇨🇮' },
]

const SEVERITY_ORDER: Record<string, number> = { HIGH: 0, MEDIUM: 1, LOW: 2 }

const CATEGORY_EMOJI: Record<string, string> = {
  DEADLINE:       '⏰',
  ENFORCEMENT:    '⚖️',
  FINE:           '💰',
  INVESTIGATION:  '🔍',
  NEW_REGULATION: '📋',
  CIRCULAR:       '📢',
  GUIDANCE:       '💡',
  OTHER:          'ℹ️',
}

function severityColor(s: string) {
  if (s === 'HIGH')   return 'var(--fail)'
  if (s === 'MEDIUM') return 'var(--warn)'
  return 'var(--pass)'
}

function severityBadgeClass(s: string) {
  if (s === 'HIGH')   return 'badge badge-fail'
  if (s === 'MEDIUM') return 'badge badge-warn'
  return 'badge badge-pass'
}

function formatDate(d: string) {
  try {
    return new Date(d).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return d
  }
}

const FLAG: Record<string, string> = Object.fromEntries(COUNTRIES.map(c => [c.value, c.flag]))

export default function Watch() {
  const [result,          setResult]          = useState<WatchResult | null>(null)
  const [loading,         setLoading]         = useState(true)
  const [error,           setError]           = useState<string | null>(null)
  const [countryFilter,   setCountryFilter]   = useState('all')
  const [severityFilter,  setSeverityFilter]  = useState('all')

  useEffect(() => {
    loadData()
  }, [])

  function loadData() {
    setLoading(true)
    setError(null)
    api.watchAll('all')
      .then(setResult)
      .catch(e => setError(e instanceof Error ? e.message : 'Could not connect to API server'))
      .finally(() => setLoading(false))
  }

  const updates = result?.updates ?? []

  const filtered = [...updates]
    .filter(u => countryFilter === 'all' || u.country === countryFilter)
    .filter(u => severityFilter === 'all' || u.severity === severityFilter)
    .sort((a, b) =>
      (SEVERITY_ORDER[a.severity] ?? 2) - (SEVERITY_ORDER[b.severity] ?? 2) ||
      b.published_date.localeCompare(a.published_date)
    )

  const highCount = updates.filter(u => u.severity === 'HIGH').length

  return (
    <>
      <div className="page-header">
        <div className="page-title">KijijiWatch 🔔</div>
        <div className="page-sub">Live regulatory intelligence across 7 African countries</div>
      </div>

      {error && (
        <div className="api-error-banner" style={{ marginBottom: 16 }}>
          <strong>Could not load regulatory updates</strong>
          <span>{error}</span>
          <span>Make sure the API server is running: <code>py -m uvicorn cli.api_server:app --reload --port 8000</code></span>
        </div>
      )}

      {/* Country filter pills */}
      <div className="filter-bar" style={{ marginBottom: 8 }}>
        {COUNTRIES.map(c => (
          <button
            key={c.value}
            className={`filter-pill ${countryFilter === c.value ? 'active' : ''}`}
            onClick={() => setCountryFilter(c.value)}
          >
            {c.flag} {c.label}
          </button>
        ))}
      </div>

      {/* Severity filter */}
      <div className="filter-bar" style={{ marginBottom: 16 }}>
        {(['all', 'HIGH', 'MEDIUM', 'LOW'] as const).map(s => (
          <button
            key={s}
            className={`filter-pill ${severityFilter === s ? 'active' : ''}`}
            onClick={() => setSeverityFilter(s)}
          >
            {s === 'all' ? 'All' : s === 'HIGH' ? '🔴 High' : s === 'MEDIUM' ? '🟡 Medium' : '🟢 Low'}
            <span className="pill-count">
              {s === 'all'
                ? updates.length
                : updates.filter(u => u.severity === s).length}
            </span>
          </button>
        ))}

        <button className="btn btn-sm" onClick={loadData} style={{ marginLeft: 'auto' }}>
          ↻ Refresh
        </button>
      </div>

      {loading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '24px 0', color: 'var(--text-tertiary)' }}>
          <span className="spinner spinner-dark" />
          Fetching latest regulatory updates…
        </div>
      )}

      {!loading && filtered.length === 0 && !error && (
        <div className="card">
          <div className="empty-state">
            <div style={{ fontSize: 32 }}>✅</div>
            <div className="empty-state-title">No regulatory updates found</div>
            <div className="empty-state-sub">All countries are up to date.</div>
          </div>
        </div>
      )}

      {/* Update cards */}
      {!loading && filtered.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {filtered.map(u => (
            <UpdateCard key={u.id} update={u} />
          ))}
        </div>
      )}

      {/* High-priority warning */}
      {highCount > 0 && !loading && (
        <div style={{
          marginTop: 20,
          padding: '12px 16px',
          background: '#fdf0f0',
          border: '0.5px solid #f5c6c6',
          borderRadius: 'var(--radius)',
          fontSize: 13,
          color: '#8b1a1a',
          fontWeight: 500,
        }}>
          ⚠️ {highCount} high-priority regulatory update{highCount > 1 ? 's' : ''} require your attention.
          Review immediately to avoid penalties and enforcement action.
        </div>
      )}
    </>
  )
}

function UpdateCard({ update: u }: { update: RegulatoryUpdate }) {
  const borderColor = severityColor(u.severity)
  const countryLabel = COUNTRIES.find(c => c.value === u.country)?.label ?? u.country

  return (
    <div style={{
      background: 'var(--bg-primary)',
      border: '0.5px solid var(--border-strong)',
      borderLeft: `3px solid ${borderColor}`,
      borderRadius: 'var(--radius)',
      padding: '14px 16px',
    }}>
      {/* Top row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
        <span className={severityBadgeClass(u.severity)}>{u.severity}</span>
        <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
          {CATEGORY_EMOJI[u.category] ?? 'ℹ️'} {u.category}
        </span>
        <span style={{
          fontSize: 11,
          color: 'var(--text-tertiary)',
          background: 'var(--bg-tertiary)',
          padding: '2px 8px',
          borderRadius: 20,
        }}>
          {u.authority}
        </span>
      </div>

      {/* Title */}
      <div style={{ fontSize: 14, fontWeight: 500, marginBottom: 6, lineHeight: 1.4 }}>
        {u.title}
      </div>

      {/* Summary */}
      {u.summary !== u.title && (
        <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8, lineHeight: 1.5 }}>
          {u.summary}
        </div>
      )}

      {/* Tags */}
      {u.tags.length > 0 && (
        <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap', marginBottom: 8 }}>
          {u.tags.map(t => (
            <span key={t} className="adapter-pill">{t}</span>
          ))}
        </div>
      )}

      {/* Bottom row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 12, color: 'var(--text-tertiary)' }}>
        <span>{FLAG[u.country] ?? '🌍'} {countryLabel}</span>
        <span>·</span>
        <span>{formatDate(u.published_date)}</span>
        {u.source_url && (
          <>
            <span>·</span>
            <a
              href={u.source_url}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: 'var(--brand)', textDecoration: 'none' }}
            >
              View source →
            </a>
          </>
        )}
      </div>
    </div>
  )
}
