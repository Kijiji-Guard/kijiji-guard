export interface Finding {
  check_id: string
  check_name: string
  result: 'PASSED' | 'FAILED' | 'WARN' | 'INFO'
  resource: string
  file_path: string
  regulation: string
  remediation: string
}

export interface ScanSummary {
  total: number
  passed: number
  failed: number
  warned?: number
  pass_rate: number
}

export interface ScanResult {
  id: string
  timestamp: string
  target: string
  country: string
  scan_types: string[]
  findings: Finding[]
  summary: ScanSummary
}

export interface HistoryEntry {
  id: string
  timestamp: string
  target: string
  country: string
  scan_types: string[]
  summary: ScanSummary
}

export interface Regulation {
  country: string
  code: string
  regulation_name: string
  governing_body: string
  penalty_summary: string
  supported_adapters: string[]
}

export type View = 'overview' | 'scan' | 'findings' | 'history' | 'regulations' | 'export'
