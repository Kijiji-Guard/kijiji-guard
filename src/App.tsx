import { useState, useEffect } from 'react'
import type { View, ScanResult } from './types'
import { api } from './api'
import Sidebar from './components/Sidebar'
import Overview from './components/Overview'
import RunScan from './components/RunScan'
import Findings from './components/Findings'
import History from './components/History'
import Regulations from './components/Regulations'
import ExportReport from './components/ExportReport'

export default function App() {
  const [activeView, setActiveView] = useState<View>('overview')
  const [lastScanResult, setLastScanResult] = useState<ScanResult | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  useEffect(() => {
    api.health()
      .then(() => setIsConnected(true))
      .catch(() => setIsConnected(false))
  }, [])

  function navigate(view: View) {
    setActiveView(view)
    setMobileNavOpen(false)
  }

  const sidebarProps = {
    activeView,
    setActiveView: navigate,
    lastScanResult,
    isConnected,
  }

  return (
    <>
      {/* Mobile top bar */}
      <div className="mobile-bar">
        <div className="mobile-brand">
          <ShieldIcon size={18} />
          Kijiji-Guard
        </div>
        <button className="hamburger" onClick={() => setMobileNavOpen(true)}>
          <MenuIcon />
        </button>
      </div>

      {/* Mobile drawer */}
      <div className={`mobile-nav-drawer ${mobileNavOpen ? 'open' : ''}`}>
        <div className="mobile-nav-overlay" onClick={() => setMobileNavOpen(false)} />
        <div className="mobile-nav-panel">
          <Sidebar {...sidebarProps} />
        </div>
      </div>

      <div className="app-layout">
        <Sidebar {...sidebarProps} />
        <main className="main-content">
          <div className="page-inner">
            {activeView === 'overview' && (
              <Overview
                lastScanResult={lastScanResult}
                setActiveView={navigate}
                isConnected={isConnected}
              />
            )}
            {activeView === 'scan' && (
              <RunScan
                setLastScanResult={setLastScanResult}
                setActiveView={navigate}
                isConnected={isConnected}
              />
            )}
            {activeView === 'findings' && (
              <Findings lastScanResult={lastScanResult} />
            )}
            {activeView === 'history' && (
              <History
                setLastScanResult={setLastScanResult}
                setActiveView={navigate}
              />
            )}
            {activeView === 'regulations' && (
              <Regulations setActiveView={navigate} />
            )}
            {activeView === 'export' && (
              <ExportReport lastScanResult={lastScanResult} />
            )}
          </div>
        </main>
      </div>
    </>
  )
}

function ShieldIcon({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  )
}

function MenuIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="3" y1="6" x2="21" y2="6" />
      <line x1="3" y1="12" x2="21" y2="12" />
      <line x1="3" y1="18" x2="21" y2="18" />
    </svg>
  )
}
