import { useState, useEffect } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import { bloombergAPI } from '../api/bloomberg'

export function Header() {
  const { currentTheme } = useTheme()
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking')

  useEffect(() => {
    checkAPIStatus()
    // Check status every 30 seconds
    const interval = setInterval(checkAPIStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const checkAPIStatus = async () => {
    try {
      // Check Bloomberg Terminal health directly
      const health = await bloombergAPI.healthCheck()
      if (health.success && health.data?.bloomberg_terminal_running) {
        setApiStatus('connected')
      } else {
        setApiStatus('disconnected')
      }
    } catch (error) {
      setApiStatus('disconnected')
    }
  }

  const handleRefresh = async () => {
    setApiStatus('checking')
    await checkAPIStatus()
  }

  const getStatusColor = () => {
    switch (apiStatus) {
      case 'connected': return currentTheme.success
      case 'disconnected': return currentTheme.danger
      case 'checking': return currentTheme.warning
      default: return currentTheme.textSecondary
    }
  }

  const getStatusText = () => {
    switch (apiStatus) {
      case 'connected': return 'Bloomberg Connected'
      case 'disconnected': return 'Bloomberg Disconnected'
      case 'checking': return 'Checking Status...'
      default: return 'Unknown'
    }
  }
  
  return (
    <header style={{
      backgroundColor: currentTheme.surface,
      borderBottom: `1px solid ${currentTheme.border}`,
      padding: '12px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      height: '60px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
        {/* GZC Logo/Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* GZC Logo matching main app */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              fontSize: '24px',
              fontWeight: 'bold',
              color: currentTheme.text
            }}>
              GZC
            </div>
            <div style={{
              backgroundColor: currentTheme.textTertiary,
              width: '1px',
              height: '24px'
            }} />
            <div style={{
              fontSize: '10px',
              fontWeight: '500',
              color: currentTheme.textSecondary,
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              Investment<br />Management
            </div>
          </div>
          <div>
            <h1 style={{ 
              fontSize: '16px', 
              fontWeight: '600', 
              color: currentTheme.text,
              margin: 0
            }}>
              Bloomberg Volatility Surface
            </h1>
            <p style={{ 
              fontSize: '11px', 
              color: currentTheme.textSecondary,
              margin: 0
            }}>
              Real-time FX Option Volatilities
            </p>
          </div>
        </div>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Bloomberg API Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: getStatusColor(),
            boxShadow: `0 0 4px ${getStatusColor()}`
          }} />
          <span style={{
            fontSize: '11px',
            color: currentTheme.textSecondary,
            fontWeight: '500'
          }}>
            {getStatusText()}
          </span>
          <span style={{
            fontSize: '10px',
            color: currentTheme.textTertiary,
            fontFamily: 'monospace'
          }}>
            API: 20.172.249.92:8080
          </span>
        </div>

        {/* Status Refresh Button */}
        <button
          onClick={handleRefresh}
          style={{
            backgroundColor: currentTheme.surfaceAlt,
            color: currentTheme.text,
            border: `1px solid ${currentTheme.border}`,
            borderRadius: '4px',
            padding: '6px 8px',
            fontSize: '11px',
            fontWeight: '500',
            cursor: 'pointer'
          }}
          title="Refresh Bloomberg status"
        >
          ↻
        </button>
        
        {/* Currency Selector */}
        <select 
          style={{
            backgroundColor: currentTheme.background,
            color: currentTheme.text,
            border: `1px solid ${currentTheme.border}`,
            borderRadius: '4px',
            padding: '6px 12px',
            fontSize: '12px',
            cursor: 'pointer'
          }}
          defaultValue="EURUSD"
        >
          <option value="EURUSD">EURUSD</option>
          <option value="USDJPY">USDJPY</option>
          <option value="GBPUSD">GBPUSD</option>
          <option value="USDCHF">USDCHF</option>
        </select>
        
        {/* Refresh Button */}
        <button
          style={{
            backgroundColor: currentTheme.primary,
            color: currentTheme.background,
            border: 'none',
            borderRadius: '4px',
            padding: '6px 16px',
            fontSize: '12px',
            fontWeight: '500',
            cursor: 'pointer'
          }}
        >
          Refresh
        </button>
      </div>
    </header>
  )
}