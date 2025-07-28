import { useState, useEffect, useMemo } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import { portfolioService } from '../services/portfolioService'
import type { Portfolio, NewPositionForm, PortfolioValuation } from '../types/portfolio'
import { ChevronDown, Plus, Trash2, RefreshCw, Database } from 'lucide-react'

type DataMode = 'live' | 'eod' | 'historical'
type PortfolioType = 'active' | 'virtual'

export function PortfolioTab() {
  const { currentTheme } = useTheme()
  const [portfolioType, setPortfolioType] = useState<PortfolioType>('active')
  const [dataMode, setDataMode] = useState<DataMode>('live')
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0])
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string | null>(null)
  const [portfolios, setPortfolios] = useState<Portfolio[]>([])
  const [portfolioValuation, setPortfolioValuation] = useState<PortfolioValuation | null>(null)
  const [isAddingPosition, setIsAddingPosition] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [isSyncing, setIsSyncing] = useState(false)
  const [syncStatus, setSyncStatus] = useState<string | null>(null)
  const [newPosition, setNewPosition] = useState<NewPositionForm>({
    ticker: '',
    description: '',
    quantity: 0,
    entryPrice: undefined
  })

  // Load portfolios
  useEffect(() => {
    loadPortfolios()
  }, [portfolioType])

  // Update valuation when portfolio changes
  useEffect(() => {
    if (selectedPortfolioId) {
      updateValuation()
    }
  }, [selectedPortfolioId])

  const loadPortfolios = () => {
    const allPortfolios = portfolioService.getAllPortfolios()
    const filteredPortfolios = allPortfolios.filter(p => p.type === portfolioType)
    setPortfolios(filteredPortfolios)
    
    // Select first portfolio if none selected
    if (!selectedPortfolioId && filteredPortfolios.length > 0) {
      setSelectedPortfolioId(filteredPortfolios[0].id)
    }
  }

  const updateValuation = () => {
    if (selectedPortfolioId) {
      try {
        const valuation = portfolioService.calculateValuation(selectedPortfolioId)
        setPortfolioValuation(valuation)
      } catch (error) {
        console.error('Failed to calculate valuation:', error)
      }
    }
  }

  const selectedPortfolio = useMemo(() => {
    return portfolios.find(p => p.id === selectedPortfolioId) || null
  }, [portfolios, selectedPortfolioId])

  const handleCreatePortfolio = () => {
    const name = prompt('Enter portfolio name:')
    if (name) {
      const description = prompt('Enter portfolio description (optional):')
      const newPortfolio = portfolioService.createPortfolio(name, description || undefined, 'USD', portfolioType)
      loadPortfolios()
      setSelectedPortfolioId(newPortfolio.id)
    }
  }

  const handleDeletePortfolio = () => {
    if (selectedPortfolioId && confirm('Are you sure you want to delete this portfolio?')) {
      portfolioService.deletePortfolio(selectedPortfolioId)
      setSelectedPortfolioId(null)
      loadPortfolios()
    }
  }

  const handleAddPosition = async () => {
    if (!selectedPortfolioId || !newPosition.ticker || newPosition.quantity === 0) return

    try {
      await portfolioService.addPosition(selectedPortfolioId, newPosition)
      setNewPosition({
        ticker: '',
        description: '',
        quantity: 0,
        entryPrice: undefined
      })
      setIsAddingPosition(false)
      loadPortfolios()
      updateValuation()
    } catch (error) {
      alert(`Failed to add position: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  const handleRemovePosition = (positionId: string) => {
    if (confirm('Are you sure you want to remove this position?')) {
      portfolioService.removePosition(positionId)
      loadPortfolios()
      updateValuation()
    }
  }

  const handleRefreshPrices = async () => {
    if (!selectedPortfolioId) return
    
    setIsRefreshing(true)
    try {
      await portfolioService.updateAllPrices(selectedPortfolioId)
      loadPortfolios()
      updateValuation()
    } catch (error) {
      console.error('Failed to refresh prices:', error)
      alert('Failed to refresh some prices')
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleSyncDatabase = async () => {
    setIsSyncing(true)
    setSyncStatus('Checking database sync status...')
    
    try {
      // Check sync status first
      const checkResponse = await fetch('/api/trades/sync-check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!checkResponse.ok) {
        throw new Error(`HTTP ${checkResponse.status}: ${checkResponse.statusText}`)
      }
      
      const syncData = await checkResponse.json()
      
      if (syncData.status === 'error') {
        throw new Error(syncData.error)
      }
      
      if (!syncData.sync_required) {
        setSyncStatus(`✅ Database synchronized (${syncData.fx_trades.source} FX trades, ${syncData.fx_options.source} FX options)`)
        setTimeout(() => setSyncStatus(null), 3000)
        return
      }
      
      // Perform sync
      setSyncStatus(`Syncing ${syncData.fx_trades.missing + syncData.fx_options.missing} new trades...`)
      
      const syncResponse = await fetch('/api/trades/perform-sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (!syncResponse.ok) {
        throw new Error(`HTTP ${syncResponse.status}: ${syncResponse.statusText}`)
      }
      
      const syncResult = await syncResponse.json()
      
      if (syncResult.status === 'error') {
        throw new Error(syncResult.error)
      }
      
      setSyncStatus(`✅ Sync complete! Migrated ${syncResult.migrated_fx_trades} FX trades and ${syncResult.migrated_fx_options} FX options`)
      setTimeout(() => setSyncStatus(null), 5000)
      
    } catch (error) {
      console.error('Database sync failed:', error)
      setSyncStatus(`❌ Sync failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
      setTimeout(() => setSyncStatus(null), 5000)
    } finally {
      setIsSyncing(false)
    }
  }

  const formatNumber = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return '-'
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 4
    }).format(value)
  }

  const formatPercent = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return '-'
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {/* Header Controls */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: currentTheme.surface,
        padding: '8px',
        borderRadius: '6px',
        border: `1px solid ${currentTheme.border}`
      }}>
        {/* Left side - Portfolio Type and Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Portfolio Type Toggle */}
          <div style={{
            display: 'flex',
            backgroundColor: currentTheme.background,
            borderRadius: '4px',
            padding: '1px',
            border: `1px solid ${currentTheme.border}`
          }}>
            <button
              onClick={() => setPortfolioType('active')}
              style={{
                padding: '3px 8px',
                backgroundColor: portfolioType === 'active' ? currentTheme.primary : 'transparent',
                color: portfolioType === 'active' ? '#ffffff' : currentTheme.textSecondary,
                border: 'none',
                borderRadius: '3px',
                fontSize: '11px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              Active
            </button>
            <button
              onClick={() => setPortfolioType('virtual')}
              style={{
                padding: '3px 8px',
                backgroundColor: portfolioType === 'virtual' ? currentTheme.primary : 'transparent',
                color: portfolioType === 'virtual' ? '#ffffff' : currentTheme.textSecondary,
                border: 'none',
                borderRadius: '3px',
                fontSize: '11px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              Virtual
            </button>
          </div>

          {/* Portfolio Dropdown */}
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '4px 8px',
                backgroundColor: currentTheme.background,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '4px',
                color: currentTheme.text,
                fontSize: '12px',
                fontWeight: '500',
                cursor: 'pointer',
                minWidth: '160px',
                justifyContent: 'space-between'
              }}
            >
              <span>{selectedPortfolio ? selectedPortfolio.name : 'Select Portfolio'}</span>
              <ChevronDown size={12} style={{
                transform: isDropdownOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: 'transform 0.2s ease'
              }} />
            </button>

            {isDropdownOpen && (
              <div style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                marginTop: '2px',
                backgroundColor: currentTheme.surface,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '4px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                zIndex: 1000,
                maxHeight: '200px',
                overflowY: 'auto'
              }}>
                {portfolios.map(portfolio => (
                  <button
                    key={portfolio.id}
                    onClick={() => {
                      setSelectedPortfolioId(portfolio.id)
                      setIsDropdownOpen(false)
                    }}
                    style={{
                      display: 'block',
                      width: '100%',
                      padding: '6px 8px',
                      backgroundColor: selectedPortfolioId === portfolio.id ? currentTheme.background : 'transparent',
                      border: 'none',
                      textAlign: 'left',
                      color: currentTheme.text,
                      fontSize: '11px',
                      cursor: 'pointer',
                      transition: 'background-color 0.2s ease'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = currentTheme.background}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = selectedPortfolioId === portfolio.id ? currentTheme.background : 'transparent'}
                  >
                    <div style={{ fontWeight: '500' }}>{portfolio.name}</div>
                    {portfolio.description && (
                      <div style={{ fontSize: '10px', color: currentTheme.textSecondary, marginTop: '1px' }}>
                        {portfolio.description}
                      </div>
                    )}
                  </button>
                ))}
                <div style={{ borderTop: `1px solid ${currentTheme.border}`, padding: '4px' }}>
                  <button
                    onClick={() => {
                      handleCreatePortfolio()
                      setIsDropdownOpen(false)
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '4px 6px',
                      backgroundColor: 'transparent',
                      border: 'none',
                      color: currentTheme.primary,
                      fontSize: '11px',
                      fontWeight: '500',
                      cursor: 'pointer',
                      width: '100%'
                    }}
                  >
                    <Plus size={12} />
                    Create New Portfolio
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Portfolio Actions */}
          {selectedPortfolio && (
            <button
              onClick={handleDeletePortfolio}
              style={{
                padding: '4px',
                backgroundColor: 'transparent',
                border: 'none',
                color: currentTheme.error,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              title="Delete Portfolio"
            >
              <Trash2 size={12} />
            </button>
          )}
        </div>

        {/* Right side - Data Mode */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            display: 'flex',
            backgroundColor: currentTheme.background,
            borderRadius: '4px',
            padding: '1px',
            border: `1px solid ${currentTheme.border}`
          }}>
            <button
              onClick={() => setDataMode('live')}
              style={{
                padding: '3px 8px',
                backgroundColor: dataMode === 'live' ? currentTheme.primary : 'transparent',
                color: dataMode === 'live' ? '#ffffff' : currentTheme.textSecondary,
                border: 'none',
                borderRadius: '3px',
                fontSize: '11px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              Live
            </button>
            <button
              onClick={() => setDataMode('eod')}
              style={{
                padding: '3px 8px',
                backgroundColor: dataMode === 'eod' ? currentTheme.primary : 'transparent',
                color: dataMode === 'eod' ? '#ffffff' : currentTheme.textSecondary,
                border: 'none',
                borderRadius: '3px',
                fontSize: '11px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              EOD
            </button>
            <button
              onClick={() => setDataMode('historical')}
              style={{
                padding: '3px 8px',
                backgroundColor: dataMode === 'historical' ? currentTheme.primary : 'transparent',
                color: dataMode === 'historical' ? '#ffffff' : currentTheme.textSecondary,
                border: 'none',
                borderRadius: '3px',
                fontSize: '11px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              Date
            </button>
          </div>
          
          {dataMode === 'historical' && (
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              style={{
                padding: '3px 6px',
                backgroundColor: currentTheme.background,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '3px',
                color: currentTheme.text,
                fontSize: '11px'
              }}
            />
          )}
        </div>
      </div>

      {/* Main Content */}
      {selectedPortfolio ? (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {/* Portfolio Summary */}
          {portfolioValuation && (
            <div style={{
              backgroundColor: currentTheme.surface,
              padding: '8px',
              borderRadius: '6px',
              border: `1px solid ${currentTheme.border}`,
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
              gap: '12px'
            }}>
              <div>
                <div style={{ fontSize: '10px', color: currentTheme.textSecondary, marginBottom: '2px' }}>
                  Total Positions
                </div>
                <div style={{ fontSize: '16px', fontWeight: '600' }}>
                  {portfolioValuation.totalPositions}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '10px', color: currentTheme.textSecondary, marginBottom: '2px' }}>
                  Market Value ({portfolioValuation.baseCurrency})
                </div>
                <div style={{ fontSize: '16px', fontWeight: '600' }}>
                  {formatNumber(portfolioValuation.totalMarketValue)}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '10px', color: currentTheme.textSecondary, marginBottom: '2px' }}>
                  Unrealized P&L
                </div>
                <div style={{
                  fontSize: '16px',
                  fontWeight: '600',
                  color: portfolioValuation.totalUnrealizedPnL >= 0 ? currentTheme.success : currentTheme.error
                }}>
                  {formatNumber(portfolioValuation.totalUnrealizedPnL)}
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <button
                  onClick={handleSyncDatabase}
                  disabled={isSyncing}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: '4px 8px',
                    backgroundColor: currentTheme.info,
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontWeight: '500',
                    cursor: isSyncing ? 'not-allowed' : 'pointer',
                    opacity: isSyncing ? 0.7 : 1
                  }}
                >
                  <Database size={11} style={{
                    animation: isSyncing ? 'spin 1s linear infinite' : 'none'
                  }} />
                  {isSyncing ? 'Syncing...' : 'Sync DB'}
                </button>
                <button
                  onClick={handleRefreshPrices}
                  disabled={isRefreshing}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: '4px 8px',
                    backgroundColor: currentTheme.primary,
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontWeight: '500',
                    cursor: isRefreshing ? 'not-allowed' : 'pointer',
                    opacity: isRefreshing ? 0.7 : 1
                  }}
                >
                  <RefreshCw size={11} style={{
                    animation: isRefreshing ? 'spin 1s linear infinite' : 'none'
                  }} />
                  {isRefreshing ? 'Refreshing...' : 'Refresh Prices'}
                </button>
              </div>
            </div>
          )}

          {/* Sync Status */}
          {syncStatus && (
            <div style={{
              backgroundColor: currentTheme.surface,
              padding: '8px',
              borderRadius: '6px',
              border: `1px solid ${currentTheme.border}`,
              fontSize: '11px',
              color: currentTheme.text,
              textAlign: 'center'
            }}>
              {syncStatus}
            </div>
          )}

          {/* Positions Table */}
          <div style={{
            flex: 1,
            backgroundColor: currentTheme.surface,
            borderRadius: '6px',
            border: `1px solid ${currentTheme.border}`,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column'
          }}>
            {/* Table Header */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '6px 8px',
              borderBottom: `1px solid ${currentTheme.border}`
            }}>
              <h3 style={{ fontSize: '13px', fontWeight: '600', margin: 0 }}>Positions</h3>
              <button
                onClick={() => setIsAddingPosition(true)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '3px 6px',
                  backgroundColor: currentTheme.primary,
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '11px',
                  fontWeight: '500',
                  cursor: 'pointer'
                }}
              >
                <Plus size={11} />
                Add Position
              </button>
            </div>

            {/* Add Position Form */}
            {isAddingPosition && (
              <div style={{
                padding: '8px',
                backgroundColor: currentTheme.background,
                borderBottom: `1px solid ${currentTheme.border}`,
                display: 'grid',
                gridTemplateColumns: '2fr 2fr 1fr 1fr auto',
                gap: '6px',
                alignItems: 'end'
              }}>
                <div>
                  <label style={{ fontSize: '10px', color: currentTheme.textSecondary, display: 'block', marginBottom: '2px' }}>
                    Ticker
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., EURUSDV1M BGN CURNCY"
                    value={newPosition.ticker}
                    onChange={(e) => setNewPosition({ ...newPosition, ticker: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '3px 6px',
                      backgroundColor: currentTheme.surface,
                      border: `1px solid ${currentTheme.border}`,
                      borderRadius: '3px',
                      color: currentTheme.text,
                      fontSize: '11px'
                    }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '10px', color: currentTheme.textSecondary, display: 'block', marginBottom: '2px' }}>
                    Description
                  </label>
                  <input
                    type="text"
                    placeholder="Optional"
                    value={newPosition.description}
                    onChange={(e) => setNewPosition({ ...newPosition, description: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '3px 6px',
                      backgroundColor: currentTheme.surface,
                      border: `1px solid ${currentTheme.border}`,
                      borderRadius: '3px',
                      color: currentTheme.text,
                      fontSize: '11px'
                    }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '10px', color: currentTheme.textSecondary, display: 'block', marginBottom: '2px' }}>
                    Quantity
                  </label>
                  <input
                    type="number"
                    placeholder="0"
                    value={newPosition.quantity || ''}
                    onChange={(e) => setNewPosition({ ...newPosition, quantity: parseFloat(e.target.value) || 0 })}
                    style={{
                      width: '100%',
                      padding: '3px 6px',
                      backgroundColor: currentTheme.surface,
                      border: `1px solid ${currentTheme.border}`,
                      borderRadius: '3px',
                      color: currentTheme.text,
                      fontSize: '11px'
                    }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '10px', color: currentTheme.textSecondary, display: 'block', marginBottom: '2px' }}>
                    Entry Price
                  </label>
                  <input
                    type="number"
                    placeholder="Optional"
                    value={newPosition.entryPrice || ''}
                    onChange={(e) => setNewPosition({ ...newPosition, entryPrice: parseFloat(e.target.value) || undefined })}
                    style={{
                      width: '100%',
                      padding: '3px 6px',
                      backgroundColor: currentTheme.surface,
                      border: `1px solid ${currentTheme.border}`,
                      borderRadius: '3px',
                      color: currentTheme.text,
                      fontSize: '11px'
                    }}
                  />
                </div>
                <div style={{ display: 'flex', gap: '4px' }}>
                  <button
                    onClick={handleAddPosition}
                    style={{
                      padding: '3px 8px',
                      backgroundColor: currentTheme.success,
                      color: '#ffffff',
                      border: 'none',
                      borderRadius: '3px',
                      fontSize: '11px',
                      fontWeight: '500',
                      cursor: 'pointer'
                    }}
                  >
                    Add
                  </button>
                  <button
                    onClick={() => {
                      setIsAddingPosition(false)
                      setNewPosition({ ticker: '', description: '', quantity: 0, entryPrice: undefined })
                    }}
                    style={{
                      padding: '3px 8px',
                      backgroundColor: currentTheme.background,
                      color: currentTheme.text,
                      border: `1px solid ${currentTheme.border}`,
                      borderRadius: '3px',
                      fontSize: '11px',
                      fontWeight: '500',
                      cursor: 'pointer'
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Table Content */}
            <div style={{ flex: 1, overflowY: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: `1px solid ${currentTheme.border}` }}>
                    <th style={{ padding: '6px 8px', textAlign: 'left', fontSize: '10px', fontWeight: '600', color: currentTheme.textSecondary }}>
                      Ticker
                    </th>
                    <th style={{ padding: '6px 8px', textAlign: 'left', fontSize: '10px', fontWeight: '600', color: currentTheme.textSecondary }}>
                      Description
                    </th>
                    <th style={{ padding: '6px 8px', textAlign: 'right', fontSize: '10px', fontWeight: '600', color: currentTheme.textSecondary }}>
                      Quantity
                    </th>
                    <th style={{ padding: '6px 8px', textAlign: 'right', fontSize: '10px', fontWeight: '600', color: currentTheme.textSecondary }}>
                      Entry Price
                    </th>
                    <th style={{ padding: '6px 8px', textAlign: 'right', fontSize: '10px', fontWeight: '600', color: currentTheme.textSecondary }}>
                      Current Price
                    </th>
                    <th style={{ padding: '6px 8px', textAlign: 'right', fontSize: '10px', fontWeight: '600', color: currentTheme.textSecondary }}>
                      Market Value
                    </th>
                    <th style={{ padding: '6px 8px', textAlign: 'right', fontSize: '10px', fontWeight: '600', color: currentTheme.textSecondary }}>
                      P&L
                    </th>
                    <th style={{ padding: '6px 8px', textAlign: 'center', fontSize: '10px', fontWeight: '600', color: currentTheme.textSecondary }}>
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {portfolioValuation?.positionValueSummary.map((summary) => {
                    const position = selectedPortfolio.positions.find(p => p.id === summary.positionId)
                    if (!position) return null
                    
                    return (
                      <tr key={position.id} style={{ borderBottom: `1px solid ${currentTheme.border}` }}>
                        <td style={{ padding: '6px 8px', fontSize: '11px', fontFamily: 'monospace' }}>
                          {position.ticker}
                        </td>
                        <td style={{ padding: '6px 8px', fontSize: '11px', color: currentTheme.textSecondary }}>
                          {position.description || '-'}
                        </td>
                        <td style={{ padding: '6px 8px', textAlign: 'right', fontSize: '11px', fontWeight: '500' }}>
                          {formatNumber(summary.quantity)}
                        </td>
                        <td style={{ padding: '6px 8px', textAlign: 'right', fontSize: '11px' }}>
                          {formatNumber(summary.entryPrice)}
                        </td>
                        <td style={{ padding: '6px 8px', textAlign: 'right', fontSize: '11px' }}>
                          {formatNumber(summary.currentPrice)}
                        </td>
                        <td style={{ padding: '6px 8px', textAlign: 'right', fontSize: '11px', fontWeight: '500' }}>
                          {formatNumber(summary.marketValue)}
                        </td>
                        <td style={{ padding: '6px 8px', textAlign: 'right', fontSize: '11px' }}>
                          <div style={{
                            color: summary.unrealizedPnL !== null && summary.unrealizedPnL >= 0 ? currentTheme.success : currentTheme.error,
                            lineHeight: '1.2'
                          }}>
                            {formatNumber(summary.unrealizedPnL)}
                          </div>
                          <div style={{ fontSize: '9px', color: currentTheme.textSecondary, lineHeight: '1' }}>
                            {formatPercent(summary.pnlPercent)}
                          </div>
                        </td>
                        <td style={{ padding: '6px 8px', textAlign: 'center' }}>
                          <button
                            onClick={() => handleRemovePosition(position.id)}
                            style={{
                              padding: '2px',
                              backgroundColor: 'transparent',
                              border: 'none',
                              color: currentTheme.error,
                              cursor: 'pointer',
                              display: 'inline-flex',
                              alignItems: 'center',
                              justifyContent: 'center'
                            }}
                            title="Remove Position"
                          >
                            <Trash2 size={11} />
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
              
              {selectedPortfolio.positions.length === 0 && (
                <div style={{
                  padding: '24px',
                  textAlign: 'center',
                  color: currentTheme.textSecondary,
                  fontSize: '12px'
                }}>
                  No positions in this portfolio. Click "Add Position" to start.
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: currentTheme.textSecondary,
          fontSize: '12px'
        }}>
          {portfolios.length === 0 ? 'Create a portfolio to get started' : 'Select a portfolio'}
        </div>
      )}

      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  )
}