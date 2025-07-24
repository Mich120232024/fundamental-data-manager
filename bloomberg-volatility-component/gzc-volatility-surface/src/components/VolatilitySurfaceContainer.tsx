import { useState, useEffect } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import { bloombergAPI, VolatilityData, STANDARD_TENORS } from '../api/bloomberg'
import { VolatilitySurfaceTable } from './VolatilitySurfaceTable'

// Major FX pairs for volatility trading
const CURRENCY_PAIRS = [
  // Major USD pairs
  'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
  // EUR crosses
  'EURGBP', 'EURJPY', 'EURCHF', 'EURAUD', 'EURCAD', 'EURNZD',
  // GBP crosses
  'GBPJPY', 'GBPCHF', 'GBPAUD', 'GBPCAD', 'GBPNZD',
  // JPY crosses
  'AUDJPY', 'CADJPY', 'NZDJPY', 'CHFJPY',
  // Other crosses
  'AUDCAD', 'AUDCHF', 'AUDNZD', 'CADCHF', 'NZDCAD', 'NZDCHF'
]

export function VolatilitySurfaceContainer() {
  const { currentTheme } = useTheme()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<VolatilityData[]>([])
  const [selectedCurrency, setSelectedCurrency] = useState('EURUSD')
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [dataMode, setDataMode] = useState<'live' | 'eod' | 'historical'>('live')
  const [selectedDate, setSelectedDate] = useState<string>('')
  
  useEffect(() => {
    loadVolatilityData()
  }, [selectedCurrency, dataMode, selectedDate])
  
  const loadVolatilityData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // First check if API is healthy
      // await bloombergAPI.healthCheck() // Skip health check for now
      
      let surfaceData: VolatilityData[]
      
      if (dataMode === 'live') {
        // Fetch REAL Bloomberg volatility surface data - Only populated tenors
        surfaceData = await bloombergAPI.getVolatilitySurface(selectedCurrency)
      } else if (dataMode === 'eod') {
        // Get latest EOD data (yesterday)
        const yesterday = new Date()
        yesterday.setDate(yesterday.getDate() - 1)
        const dateStr = yesterday.toISOString().split('T')[0].replace(/-/g, '')
        console.log('Fetching EOD data for currency:', selectedCurrency, 'date:', dateStr)
        surfaceData = await bloombergAPI.getVolatilitySurface(selectedCurrency, STANDARD_TENORS, dateStr)
      } else {
        // Historical data with selected date
        if (!selectedDate) {
          setError('Please select a date for historical data')
          setLoading(false)
          return
        }
        const dateStr = selectedDate.replace(/-/g, '')
        console.log('Fetching historical data for currency:', selectedCurrency, 'date:', selectedDate, 'formatted as:', dateStr)
        surfaceData = await bloombergAPI.getVolatilitySurface(selectedCurrency, STANDARD_TENORS, dateStr)
        console.log('Historical data result:', surfaceData.length, 'tenors received')
      }
      
      // Filter out empty tenors (no data at all)
      const filteredData = surfaceData.filter(row => {
        return row.atm_bid !== null || row.atm_ask !== null ||
               row.rr_5d_bid !== null || row.rr_5d_ask !== null ||
               row.rr_10d_bid !== null || row.rr_10d_ask !== null ||
               row.rr_15d_bid !== null || row.rr_15d_ask !== null ||
               row.rr_25d_bid !== null || row.rr_25d_ask !== null ||
               row.rr_35d_bid !== null || row.rr_35d_ask !== null ||
               row.bf_5d_bid !== null || row.bf_5d_ask !== null ||
               row.bf_10d_bid !== null || row.bf_10d_ask !== null ||
               row.bf_15d_bid !== null || row.bf_15d_ask !== null ||
               row.bf_25d_bid !== null || row.bf_25d_ask !== null ||
               row.bf_35d_bid !== null || row.bf_35d_ask !== null
      })
      
      console.log(`Filtered ${surfaceData.length} tenors down to ${filteredData.length} with data`)
      setData(filteredData)
      setLastUpdate(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load Bloomberg data')
      console.error('Bloomberg API Error:', err)
    } finally {
      setLoading(false)
    }
  }
  
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '400px',
        color: currentTheme.primary
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', marginBottom: '8px' }}>Loading...</div>
          <div style={{ fontSize: '12px', color: currentTheme.textSecondary }}>
            Fetching Bloomberg data
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <div style={{
      backgroundColor: currentTheme.surface,
      borderRadius: '8px',
      border: `1px solid ${currentTheme.border}`,
      overflow: 'hidden'
    }}>
      <div style={{
        padding: '16px',
        borderBottom: `1px solid ${currentTheme.border}`,
        backgroundColor: currentTheme.background,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h2 style={{ 
            margin: 0, 
            fontSize: '14px', 
            fontWeight: '600',
            color: currentTheme.text
          }}>
            {selectedCurrency} Volatility Surface - {dataMode === 'live' ? 'Real-time' : dataMode === 'eod' ? 'Latest EOD' : `Historical (${selectedDate})`} Bloomberg Data
          </h2>
          {lastUpdate && (
            <div style={{
              fontSize: '11px',
              color: currentTheme.textSecondary,
              marginTop: '4px'
            }}>
              Last updated: {lastUpdate.toLocaleTimeString()}
            </div>
          )}
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
          <select
            value={dataMode}
            onChange={(e) => setDataMode(e.target.value as 'live' | 'eod' | 'historical')}
            style={{
              backgroundColor: currentTheme.surface,
              color: currentTheme.text,
              border: `1px solid ${currentTheme.border}`,
              borderRadius: '4px',
              padding: '6px 8px',
              fontSize: '12px',
              fontWeight: '500',
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            <option value="live">Live</option>
            <option value="eod">Latest EOD</option>
            <option value="historical">Historical</option>
          </select>
          
          {dataMode === 'historical' && (
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              max={new Date().toISOString().split('T')[0]}
              style={{
                backgroundColor: currentTheme.surface,
                color: currentTheme.text,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '4px',
                padding: '5px 8px',
                fontSize: '12px',
                fontWeight: '500',
                cursor: 'pointer',
                outline: 'none'
              }}
            />
          )}
          
          <select
            value={selectedCurrency}
            onChange={(e) => setSelectedCurrency(e.target.value)}
            style={{
              backgroundColor: currentTheme.surface,
              color: currentTheme.text,
              border: `1px solid ${currentTheme.border}`,
              borderRadius: '4px',
              padding: '6px 8px',
              fontSize: '12px',
              fontWeight: '500',
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            {CURRENCY_PAIRS.map(pair => (
              <option key={pair} value={pair}>{pair}</option>
            ))}
          </select>
          
          <button
            onClick={loadVolatilityData}
            disabled={loading}
            style={{
              backgroundColor: currentTheme.primary,
              color: currentTheme.background,
              border: 'none',
              borderRadius: '4px',
              padding: '6px 12px',
              fontSize: '11px',
              fontWeight: '500',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1
            }}
          >
            {loading ? 'Refreshing...' : 'Refresh Now'}
          </button>
        </div>
      </div>
      <VolatilitySurfaceTable data={data} />
    </div>
  )
}