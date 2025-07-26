import { useState, useEffect } from 'react'
import { useTheme } from '../contexts/ThemeContext'

interface OptionParameters {
  currencyPair: string
  tenor: string
  strike: number
  optionType: 'call' | 'put'
  notional: number
}

interface OptionPrice {
  premium: number
  delta: number
  gamma: number
  vega: number
  theta: number
  impliedVol: number
}

export function OptionsPricingTab() {
  const { currentTheme } = useTheme()
  
  // Option parameters
  const [params, setParams] = useState<OptionParameters>({
    currencyPair: 'EURUSD',
    tenor: '1M',
    strike: 1.0850, // Current spot + forward
    optionType: 'call',
    notional: 1000000
  })
  
  // Pricing results
  const [pricing, setPricing] = useState<OptionPrice | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Market data - NO FALLBACKS, only real Bloomberg data
  const [spotRate, setSpotRate] = useState<number | null>(null)
  const [forwardRate, setForwardRate] = useState<number | null>(null)
  const [forwardPoints, setForwardPoints] = useState<number | null>(null)
  const [volatility, setVoltaility] = useState<number | null>(null)
  const [riskFreeRate, setRiskFreeRate] = useState<number | null>(null)
  const [eurRate, setEurRate] = useState<number | null>(null)
  const [usdRate, setUsdRate] = useState<number | null>(null)
  
  // Garman-Kohlhagen pricing function for FX options
  const calculateOptionPrice = (
    F: number, // Forward price (not spot!)
    K: number, // Strike price
    T: number, // Time to expiry (years)
    rDomestic: number, // Domestic risk-free rate (quote currency)
    vol: number, // Volatility
    optType: 'call' | 'put'
  ): OptionPrice => {
    // Convert percentage inputs
    const rDecimal = rDomestic / 100
    const volDecimal = vol / 100
    
    // For FX options, we use forward price directly
    // Garman-Kohlhagen model: d1 uses F instead of S
    const d1 = (Math.log(F / K) + (0.5 * volDecimal * volDecimal) * T) / (volDecimal * Math.sqrt(T))
    const d2 = d1 - volDecimal * Math.sqrt(T)
    
    // Standard normal CDF - using accurate approximation
    const normCDF = (x: number) => {
      // Abramowitz and Stegun approximation
      const a1 =  0.254829592
      const a2 = -0.284496736
      const a3 =  1.421413741
      const a4 = -1.453152027
      const a5 =  1.061405429
      const p  =  0.3275911
      
      const sign = x >= 0 ? 1 : -1
      x = Math.abs(x) / Math.sqrt(2)
      
      const t = 1.0 / (1.0 + p * x)
      const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x)
      
      return 0.5 * (1.0 + sign * y)
    }
    
    const Nd1 = normCDF(d1)
    const Nd2 = normCDF(d2)
    const nd1 = Math.exp(-0.5 * d1 * d1) / Math.sqrt(2 * Math.PI)
    
    let premium: number
    let delta: number
    
    // Garman-Kohlhagen formula for FX options
    // Premium is in quote currency terms (e.g., USD for EURUSD)
    const discountFactor = Math.exp(-rDecimal * T)
    
    if (optType === 'call') {
      // Call: discounted [F*N(d1) - K*N(d2)]
      premium = discountFactor * (F * Nd1 - K * Nd2)
      delta = discountFactor * Nd1
    } else {
      // Put: discounted [K*N(-d2) - F*N(-d1)]
      premium = discountFactor * (K * (1 - Nd2) - F * (1 - Nd1))
      delta = discountFactor * (Nd1 - 1)
    }
    
    // DEBUG: Log detailed pricing calculation
    console.log('=== PRICING CALCULATION DEBUG ===')
    console.log('Forward (F):', F)
    console.log('Strike (K):', K)
    console.log('Time (T):', T)
    console.log('Risk-free rate (r):', rDecimal)
    console.log('Volatility:', volDecimal)
    console.log('d1:', d1)
    console.log('d2:', d2)
    console.log('N(d1):', Nd1)
    console.log('N(d2):', Nd2)
    console.log('Discount factor:', discountFactor)
    console.log('Raw premium:', premium)
    console.log('Premium %:', premium * 100)
    
    // Greeks for FX options (using forward price)
    const gamma = discountFactor * nd1 / (F * volDecimal * Math.sqrt(T))
    const vega = discountFactor * F * nd1 * Math.sqrt(T) / 100 // Per 1% vol change
    const theta = -(F * nd1 * volDecimal / (2 * Math.sqrt(T)) * discountFactor + 
                   rDecimal * premium) / 365 // Per day
    
    return {
      premium,
      delta,
      gamma,
      vega,
      theta,
      impliedVol: vol
    }
  }
  
  // Fetch market data and calculate pricing
  const fetchMarketData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Fetch spot rate
      const endpoint = import.meta.env.DEV 
        ? 'http://localhost:8000/api/bloomberg/reference'
        : 'http://20.172.249.92:8080/api/bloomberg/reference'
      const spotResponse = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer test',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          securities: [`${params.currencyPair} Curncy`],
          fields: ['PX_LAST']
        })
      })
      const spotData = await spotResponse.json()
      // STRICT: Only use real Bloomberg data, no fallbacks
      if (!spotData.success || !spotData.data?.securities_data?.[0]?.success) {
        throw new Error(`EURUSD spot rate failed: ${JSON.stringify(spotData)}`)
      }
      const currentSpot = spotData.data.securities_data[0].fields?.PX_LAST
      if (!currentSpot) {
        throw new Error(`EURUSD spot rate is null`)
      }
      
      // Fetch volatility (ATM) - NO FALLBACKS
      const volResponse = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer test',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          securities: [`${params.currencyPair}V${params.tenor.replace('M', '')}M BGN Curncy`],
          fields: ['PX_LAST']
        })
      })
      const volData = await volResponse.json()
      
      if (!volData.success || !volData.data?.securities_data?.[0]?.success) {
        throw new Error(`${params.currencyPair} ${params.tenor} volatility failed: ${JSON.stringify(volData)}`)
      }
      const currentVol = volData.data.securities_data[0].fields?.PX_LAST
      if (!currentVol) {
        throw new Error(`${params.currencyPair} ${params.tenor} volatility is null`)
      }
      
      // Fetch EUR and USD interest rates
      const [baseCcy, quoteCcy] = params.currencyPair.slice(0, 3) === 'EUR' ? ['EUR', 'USD'] : ['USD', params.currencyPair.slice(3, 6)]
      
      // Get EUR rate (1M EURIBOR)
      const eurResponse = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer test',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          securities: ['EUR001M Index'],
          fields: ['PX_LAST']
        })
      })
      const eurData = await eurResponse.json()
      const eurDepoRate = eurData.data?.securities_data?.[0]?.fields?.PX_LAST
      if (!eurDepoRate) {
        throw new Error('EUR001M Index rate failed - no fallback allowed')
      }
      
      // Get USD rate (1M SOFR)
      const usdResponse = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer test',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          securities: ['US0001M Index'],
          fields: ['PX_LAST']
        })
      })
      const usdData = await usdResponse.json()
      const usdDepoRate = usdData.data?.securities_data?.[0]?.fields?.PX_LAST
      if (!usdDepoRate) {
        throw new Error('US0001M Index rate failed - no fallback allowed')
      }
      
      // Calculate tenor in years
      const tenorYears = params.tenor === '1W' ? 1/52 : 
                        params.tenor === '2W' ? 2/52 :
                        params.tenor === '1M' ? 1/12 : 
                        params.tenor === '2M' ? 2/12 :
                        params.tenor === '3M' ? 3/12 : 1/12
      
      // Calculate forward rate using interest rate parity
      const rBase = baseCcy === 'EUR' ? eurDepoRate : usdDepoRate
      const rQuote = quoteCcy === 'USD' ? usdDepoRate : eurDepoRate
      const calculatedForward = currentSpot * Math.exp((rQuote - rBase) * tenorYears / 100)
      const calculatedForwardPoints = (calculatedForward - currentSpot) * 10000
      
      // Update market data with REAL Bloomberg values
      setSpotRate(currentSpot)
      setVoltaility(currentVol)
      setForwardRate(calculatedForward)
      setForwardPoints(calculatedForwardPoints)
      setEurRate(eurDepoRate)
      setUsdRate(usdDepoRate)
      setRiskFreeRate(rQuote) // Use quote currency rate for Black-Scholes
      
      // Only calculate if we have ALL real data
      if (currentSpot && currentVol && rQuote) {
        // DEBUG: Log precision discrepancy
        console.log('=== PRECISION DEBUG ===')
        console.log('calculatedForward (F):', calculatedForward)
        console.log('params.strike (K):', params.strike)
        console.log('F - K difference:', calculatedForward - params.strike)
        console.log('Difference in basis points:', (calculatedForward - params.strike) * 10000)
        
        const price = calculateOptionPrice(
          calculatedForward, // Use forward rate for options pricing
          params.strike,
          tenorYears,
          rQuote,
          currentVol,
          params.optionType
        )
        setPricing(price)
      } else {
        throw new Error('Incomplete market data - cannot calculate option price')
      }
      
    } catch (err) {
      setError(`Failed to fetch market data: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setLoading(false)
    }
  }
  
  // Auto-update on parameter changes
  useEffect(() => {
    fetchMarketData()
  }, [params.currencyPair, params.tenor, params.strike, params.optionType])
  
  return (
    <div style={{ 
      backgroundColor: currentTheme.background,
      color: currentTheme.text,
      height: '100%'
    }}>
      <div style={{ display: 'flex', gap: '20px', height: '100%' }}>
        {/* Parameters Panel - Bloomberg Style */}
        <div style={{
          width: '240px',
          backgroundColor: currentTheme.surface,
          padding: '8px',
          borderRadius: '2px',
          border: `1px solid ${currentTheme.border}`,
          height: 'fit-content'
        }}>
          <div style={{ margin: '0 0 8px 0', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase' }}>
            OPTION PARAMETERS
          </div>
          
          {/* Currency Pair */}
          <div style={{ marginBottom: '8px' }}>
            <label style={{ display: 'block', fontSize: '9px', fontWeight: '600', marginBottom: '2px', color: currentTheme.textSecondary, textTransform: 'uppercase' }}>
              CCY PAIR
            </label>
            <select
              value={params.currencyPair}
              onChange={(e) => setParams(prev => ({ ...prev, currencyPair: e.target.value }))}
              style={{
                width: '100%',
                padding: '4px',
                backgroundColor: currentTheme.background,
                color: currentTheme.text,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '2px',
                fontSize: '11px',
                fontFamily: 'monospace'
              }}
            >
              <option value="EURUSD">EUR/USD</option>
              <option value="GBPUSD">GBP/USD</option>
              <option value="USDJPY">USD/JPY</option>
              <option value="USDCHF">USD/CHF</option>
            </select>
          </div>
          
          {/* Tenor */}
          <div style={{ marginBottom: '8px' }}>
            <label style={{ display: 'block', fontSize: '9px', fontWeight: '600', marginBottom: '2px', color: currentTheme.textSecondary, textTransform: 'uppercase' }}>
              TENOR
            </label>
            <select
              value={params.tenor}
              onChange={(e) => setParams(prev => ({ ...prev, tenor: e.target.value }))}
              style={{
                width: '100%',
                padding: '4px',
                backgroundColor: currentTheme.background,
                color: currentTheme.text,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '2px',
                fontSize: '11px',
                fontFamily: 'monospace'
              }}
            >
              <option value="1W">1W</option>
              <option value="2W">2W</option>
              <option value="1M">1M</option>
              <option value="2M">2M</option>
              <option value="3M">3M</option>
            </select>
          </div>
          
          {/* Strike */}
          <div style={{ marginBottom: '8px' }}>
            <label style={{ display: 'block', fontSize: '9px', fontWeight: '600', marginBottom: '2px', color: currentTheme.textSecondary, textTransform: 'uppercase' }}>
              STRIKE
            </label>
            <div style={{ display: 'flex', gap: '4px', marginBottom: '4px' }}>
              <button
                onClick={() => {
                  if (forwardRate) {
                    // CRITICAL FIX: Use full precision for ATMF strike
                    setParams(prev => ({ ...prev, strike: forwardRate }))
                    console.log('ATMF: Setting strike to exact forward:', forwardRate)
                  }
                }}
                disabled={!forwardRate}
                style={{
                  padding: '2px 6px',
                  backgroundColor: forwardRate && Math.abs(params.strike - forwardRate) < 0.0001 ? currentTheme.primary : currentTheme.background,
                  color: forwardRate && Math.abs(params.strike - forwardRate) < 0.0001 ? 'white' : currentTheme.text,
                  border: `1px solid ${currentTheme.border}`,
                  borderRadius: '2px',
                  cursor: forwardRate ? 'pointer' : 'not-allowed',
                  fontSize: '9px',
                  fontWeight: '600',
                  fontFamily: 'monospace'
                }}
              >
                ATMF
              </button>
              <button
                onClick={() => {
                  if (spotRate) {
                    setParams(prev => ({ ...prev, strike: spotRate }))
                  }
                }}
                disabled={!spotRate}
                style={{
                  padding: '2px 6px',
                  backgroundColor: spotRate && Math.abs(params.strike - spotRate) < 0.0001 ? currentTheme.primary : currentTheme.background,
                  color: spotRate && Math.abs(params.strike - spotRate) < 0.0001 ? 'white' : currentTheme.text,
                  border: `1px solid ${currentTheme.border}`,
                  borderRadius: '2px',
                  cursor: spotRate ? 'pointer' : 'not-allowed',
                  fontSize: '9px',
                  fontWeight: '600',
                  fontFamily: 'monospace'
                }}
              >
                ATMS
              </button>
            </div>
            <input
              type="number"
              step="0.0001"
              value={params.strike}
              onChange={(e) => setParams(prev => ({ ...prev, strike: parseFloat(e.target.value) || 0 }))}
              style={{
                width: '100%',
                padding: '4px',
                backgroundColor: currentTheme.background,
                color: currentTheme.text,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '2px',
                fontSize: '11px',
                fontFamily: 'monospace'
              }}
            />
          </div>
          
          {/* Option Type */}
          <div style={{ marginBottom: '8px' }}>
            <label style={{ display: 'block', fontSize: '9px', fontWeight: '600', marginBottom: '2px', color: currentTheme.textSecondary, textTransform: 'uppercase' }}>
              TYPE
            </label>
            <div style={{ display: 'flex', gap: '4px' }}>
              <button
                onClick={() => setParams(prev => ({ ...prev, optionType: 'call' }))}
                style={{
                  flex: 1,
                  padding: '4px',
                  backgroundColor: params.optionType === 'call' ? currentTheme.primary : currentTheme.background,
                  color: params.optionType === 'call' ? 'white' : currentTheme.text,
                  border: `1px solid ${currentTheme.border}`,
                  borderRadius: '2px',
                  cursor: 'pointer',
                  fontSize: '10px',
                  fontWeight: '600',
                  fontFamily: 'monospace',
                  textTransform: 'uppercase'
                }}
              >
                CALL
              </button>
              <button
                onClick={() => setParams(prev => ({ ...prev, optionType: 'put' }))}
                style={{
                  flex: 1,
                  padding: '4px',
                  backgroundColor: params.optionType === 'put' ? currentTheme.primary : currentTheme.background,
                  color: params.optionType === 'put' ? 'white' : currentTheme.text,
                  border: `1px solid ${currentTheme.border}`,
                  borderRadius: '2px',
                  cursor: 'pointer',
                  fontSize: '10px',
                  fontWeight: '600',
                  fontFamily: 'monospace',
                  textTransform: 'uppercase'
                }}
              >
                PUT
              </button>
            </div>
          </div>
          
          {/* Notional */}
          <div style={{ marginBottom: '8px' }}>
            <label style={{ display: 'block', fontSize: '9px', fontWeight: '600', marginBottom: '2px', color: currentTheme.textSecondary, textTransform: 'uppercase' }}>
              NOTIONAL
            </label>
            <input
              type="number"
              step="10000"
              value={params.notional}
              onChange={(e) => setParams(prev => ({ ...prev, notional: parseFloat(e.target.value) || 0 }))}
              style={{
                width: '100%',
                padding: '4px',
                backgroundColor: currentTheme.background,
                color: currentTheme.text,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '2px',
                fontSize: '11px',
                fontFamily: 'monospace'
              }}
            />
          </div>
          
          <button
            onClick={fetchMarketData}
            disabled={loading}
            style={{
              width: '100%',
              padding: '6px',
              backgroundColor: currentTheme.primary,
              color: 'white',
              border: 'none',
              borderRadius: '2px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '10px',
              fontWeight: '700',
              fontFamily: 'monospace',
              textTransform: 'uppercase'
            }}
          >
            {loading ? 'CALCULATING...' : 'CALCULATE'}
          </button>
        </div>
        
        {/* Results Panel - Bloomberg Style */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {/* Compact Market Data Grid */}
          <div style={{
            backgroundColor: currentTheme.surface,
            padding: '8px',
            border: `1px solid ${currentTheme.border}`,
            borderRadius: '2px'
          }}>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(2, 1fr)', 
              gap: '1px',
              backgroundColor: currentTheme.border
            }}>
              {/* Row 1 */}
              <div style={{ backgroundColor: currentTheme.surface, padding: '4px 6px', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '10px', color: currentTheme.textSecondary }}>SPOT</span>
                <span style={{ fontSize: '11px', fontFamily: 'monospace', fontWeight: '600', color: currentTheme.primary }}>
                  {spotRate ? spotRate.toFixed(5) : '-.-----'}
                </span>
              </div>
              <div style={{ backgroundColor: currentTheme.surface, padding: '4px 6px', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '10px', color: currentTheme.textSecondary }}>FWD</span>
                <span style={{ fontSize: '11px', fontFamily: 'monospace', fontWeight: '600', color: currentTheme.primary }}>
                  {forwardRate ? forwardRate.toFixed(5) : '-.-----'}
                </span>
              </div>
              
              {/* Row 2 */}
              <div style={{ backgroundColor: currentTheme.surface, padding: '4px 6px', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '10px', color: currentTheme.textSecondary }}>PTS</span>
                <span style={{ fontSize: '11px', fontFamily: 'monospace', fontWeight: '600', color: forwardPoints && forwardPoints > 0 ? '#4ade80' : '#ef4444' }}>
                  {forwardPoints ? (forwardPoints > 0 ? '+' : '') + forwardPoints.toFixed(2) : '-.--'}
                </span>
              </div>
              <div style={{ backgroundColor: currentTheme.surface, padding: '4px 6px', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '10px', color: currentTheme.textSecondary }}>VOL</span>
                <span style={{ fontSize: '11px', fontFamily: 'monospace', fontWeight: '600', color: currentTheme.primary }}>
                  {volatility ? volatility.toFixed(2) + '%' : '--.--'}
                </span>
              </div>
              
              {/* Row 3 */}
              <div style={{ backgroundColor: currentTheme.surface, padding: '4px 6px', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '10px', color: currentTheme.textSecondary }}>EUR</span>
                <span style={{ fontSize: '11px', fontFamily: 'monospace', fontWeight: '600' }}>
                  {eurRate ? eurRate.toFixed(3) + '%' : '-.---'}
                </span>
              </div>
              <div style={{ backgroundColor: currentTheme.surface, padding: '4px 6px', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '10px', color: currentTheme.textSecondary }}>USD</span>
                <span style={{ fontSize: '11px', fontFamily: 'monospace', fontWeight: '600' }}>
                  {usdRate ? usdRate.toFixed(3) + '%' : '-.---'}
                </span>
              </div>
            </div>
          </div>
          
          {/* Pricing Results - Bloomberg Style */}
          {pricing && (
            <>
              {/* Premium Section */}
              <div style={{
                backgroundColor: currentTheme.surface,
                padding: '8px',
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '2px'
              }}>
                <div style={{ marginBottom: '6px' }}>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
                    <span style={{ fontSize: '10px', color: currentTheme.textSecondary }}>PREMIUM</span>
                    <span style={{ fontSize: '16px', fontFamily: 'monospace', fontWeight: '700', color: currentTheme.primary }}>
                      {(pricing.premium * 100).toFixed(4)}%
                    </span>
                    <span style={{ fontSize: '12px', fontFamily: 'monospace', fontWeight: '600' }}>
                      ${(pricing.premium * params.notional).toLocaleString()}
                    </span>
                    <span style={{ fontSize: '10px', fontFamily: 'monospace', color: currentTheme.textSecondary }}>
                      ({(pricing.premium * 10000).toFixed(1)} pips)
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Greeks Grid - Bloomberg Style */}
              <div style={{
                backgroundColor: currentTheme.surface,
                padding: '8px',
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '2px'
              }}>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(4, 1fr)', 
                  gap: '1px',
                  backgroundColor: currentTheme.border
                }}>
                  <div style={{ backgroundColor: currentTheme.surface, padding: '4px 6px' }}>
                    <div style={{ fontSize: '9px', color: currentTheme.textSecondary }}>DELTA</div>
                    <div style={{ fontSize: '11px', fontFamily: 'monospace', fontWeight: '600' }}>
                      {(pricing.delta * 100).toFixed(2)}%
                    </div>
                  </div>
                  <div style={{ backgroundColor: currentTheme.surface, padding: '4px 6px' }}>
                    <div style={{ fontSize: '9px', color: currentTheme.textSecondary }}>GAMMA</div>
                    <div style={{ fontSize: '11px', fontFamily: 'monospace', fontWeight: '600' }}>
                      {pricing.gamma.toFixed(5)}
                    </div>
                  </div>
                  <div style={{ backgroundColor: currentTheme.surface, padding: '4px 6px' }}>
                    <div style={{ fontSize: '9px', color: currentTheme.textSecondary }}>VEGA</div>
                    <div style={{ fontSize: '11px', fontFamily: 'monospace', fontWeight: '600' }}>
                      ${(pricing.vega * params.notional).toFixed(0)}
                    </div>
                  </div>
                  <div style={{ backgroundColor: currentTheme.surface, padding: '4px 6px' }}>
                    <div style={{ fontSize: '9px', color: currentTheme.textSecondary }}>THETA</div>
                    <div style={{ fontSize: '11px', fontFamily: 'monospace', fontWeight: '600' }}>
                      ${(pricing.theta * params.notional).toFixed(0)}
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Delta Hedge - Bloomberg Style */}
              <div style={{
                backgroundColor: currentTheme.surface,
                padding: '8px',
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '2px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <span style={{ fontSize: '10px', color: currentTheme.textSecondary }}>DELTA HEDGE</span>
                    <span style={{ fontSize: '11px', color: currentTheme.textSecondary, marginLeft: '8px' }}>
                      ({params.optionType === 'call' ? 'Sell' : 'Buy'} {params.currencyPair.slice(0, 3)})
                    </span>
                  </div>
                  <span style={{ 
                    fontSize: '14px', 
                    fontFamily: 'monospace', 
                    fontWeight: '700', 
                    color: pricing.delta < 0 ? '#ef4444' : '#4ade80' 
                  }}>
                    {params.currencyPair.slice(0, 3)} {(-pricing.delta * params.notional).toLocaleString(undefined, { 
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2 
                    })}
                  </span>
                </div>
              </div>
            </>
          )}
          
          {error && (
            <div style={{
              backgroundColor: '#ff4444',
              color: 'white',
              padding: '16px',
              borderRadius: '8px',
              marginTop: '20px'
            }}>
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}