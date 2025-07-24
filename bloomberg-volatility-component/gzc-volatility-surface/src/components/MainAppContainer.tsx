import { useState } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import { VolatilitySurfaceContainer } from './VolatilitySurfaceContainer'
import { VolatilityHistoricalTable } from './VolatilityHistoricalTable'
import { VolatilityAnalysisTab } from './VolatilityAnalysisTab'

type TabType = 'surface' | 'historical' | 'analysis'

export function MainAppContainer() {
  const { currentTheme } = useTheme()
  const [activeTab, setActiveTab] = useState<TabType>('surface')
  
  return (
    <div style={{
      backgroundColor: currentTheme.background,
      minHeight: '100vh',
      color: currentTheme.text
    }}>
      {/* Tab Navigation */}
      <div style={{
        backgroundColor: currentTheme.surface,
        borderBottom: `1px solid ${currentTheme.border}`,
        padding: '0 16px',
        display: 'flex',
        gap: '24px',
        overflowX: 'auto'
      }}>
        <button
          onClick={() => setActiveTab('surface')}
          style={{
            backgroundColor: 'transparent',
            border: 'none',
            padding: '16px 0',
            color: activeTab === 'surface' ? currentTheme.primary : currentTheme.textSecondary,
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer',
            borderBottom: activeTab === 'surface' ? `2px solid ${currentTheme.primary}` : '2px solid transparent',
            transition: 'all 0.2s ease'
          }}
        >
          Volatility Surface
        </button>
        <button
          onClick={() => setActiveTab('historical')}
          style={{
            backgroundColor: 'transparent',
            border: 'none',
            padding: '16px 0',
            color: activeTab === 'historical' ? currentTheme.primary : currentTheme.textSecondary,
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer',
            borderBottom: activeTab === 'historical' ? `2px solid ${currentTheme.primary}` : '2px solid transparent',
            transition: 'all 0.2s ease'
          }}
        >
          Historical Analysis
        </button>
        <button
          onClick={() => setActiveTab('analysis')}
          style={{
            backgroundColor: 'transparent',
            border: 'none',
            padding: '16px 0',
            color: activeTab === 'analysis' ? currentTheme.primary : currentTheme.textSecondary,
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer',
            borderBottom: activeTab === 'analysis' ? `2px solid ${currentTheme.primary}` : '2px solid transparent',
            transition: 'all 0.2s ease'
          }}
        >
          Volatility Analysis
        </button>
      </div>
      
      {/* Tab Content */}
      <div style={{ padding: '20px', height: 'calc(100vh - 120px)' }}>
        {activeTab === 'surface' ? (
          <VolatilitySurfaceContainer />
        ) : activeTab === 'historical' ? (
          <VolatilityHistoricalTable />
        ) : activeTab === 'analysis' ? (
          <VolatilityAnalysisTab />
        ) : null}
      </div>
    </div>
  )
}