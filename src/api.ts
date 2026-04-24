import type { ScanResult, HistoryEntry, Regulation, WatchResult } from './types'

const BASE = 'http://localhost:8000'

export const api = {
  health: (): Promise<{ status: string; version: string }> =>
    fetch(`${BASE}/health`).then(r => r.json()),

  scan: (target: string, country: string, credentials: Record<string, string> = {}): Promise<ScanResult> =>
    fetch(`${BASE}/scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target, country, credentials }),
    }).then(r => r.json()),

  history: (): Promise<HistoryEntry[]> =>
    fetch(`${BASE}/scan/history`).then(r => r.json()),

  scanById: (id: string): Promise<ScanResult> =>
    fetch(`${BASE}/scan/history/${id}`).then(r => r.json()),

  regulations: (): Promise<Regulation[]> =>
    fetch(`${BASE}/regulations`).then(r => r.json()),

  htmlReport: (scanResult: ScanResult): Promise<string> =>
    fetch(`${BASE}/report/html`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scanResult),
    }).then(r => r.text()),

  watch: (country: string): Promise<WatchResult> =>
    fetch(`${BASE}/watch/${country}`).then(r => r.json()),

  watchAll: (country: string): Promise<WatchResult> =>
    fetch(`${BASE}/watch/${country}/all`).then(r => r.json()),
}
