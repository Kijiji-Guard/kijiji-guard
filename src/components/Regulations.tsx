import { useState, useEffect } from 'react'
import type { Regulation, View } from '../types'
import { api } from '../api'

interface Props {
  setActiveView: (v: View) => void
}

const FLAGS: Record<string, string> = {
  nigeria:      '🇳🇬',
  ghana:        '🇬🇭',
  kenya:        '🇰🇪',
  rwanda:       '🇷🇼',
  'cote-divoire': '🇨🇮',
  benin:        '🇧🇯',
  egypt:        '🇪🇬',
}

export default function Regulations({ setActiveView }: Props) {
  const [regulations, setRegulations] = useState<Regulation[]>([])
  const [loading,     setLoading]     = useState(true)
  const [error,       setError]       = useState<string | null>(null)

  useEffect(() => {
    api.regulations()
      .then(setRegulations)
      .catch(e => setError(e instanceof Error ? e.message : 'Could not load regulations'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <>
      <div className="page-header">
        <div className="page-title">Regulations</div>
        <div className="page-sub">African data protection laws mapped by Kijiji-Guard</div>
      </div>

      {loading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '24px 0', color: 'var(--text-tertiary)' }}>
          <span className="spinner spinner-dark" />
          Loading…
        </div>
      )}

      {error && (
        <div className="api-error-banner">
          <strong>Could not load regulations</strong>
          <span>{error}</span>
        </div>
      )}

      {!loading && !error && (
        <div className="reg-grid">
          {regulations.map(reg => (
            <div className="card" key={reg.code}>
              <div className="reg-card-header">
                <span className="reg-flag">{FLAGS[reg.code] ?? '🌍'}</span>
                <span className="reg-country">{reg.country}</span>
              </div>
              <div className="reg-name">{reg.regulation_name}</div>
              <div className="reg-body">
                <strong>Governing body:</strong> {reg.governing_body}
              </div>
              <div className="penalty-box">
                <strong>Penalties:</strong> {reg.penalty_summary}
              </div>
              <div className="adapter-list">
                {reg.supported_adapters.map(a => (
                  <span className="adapter-pill" key={a}>{a}</span>
                ))}
              </div>
              <div style={{ marginTop: 12 }}>
                <button
                  className="link-btn"
                  onClick={() => setActiveView('findings')}
                >
                  View checks →
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  )
}
