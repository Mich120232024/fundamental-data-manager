import { useState, useEffect, useCallback, useRef } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import { bloombergAPI } from '../api/bloomberg'
import { ValidatedVolatilityData } from '../api/DataValidator'
import { getQualityColor } from '../utils/dataValidation'
import * as d3 from 'd3'
import { PlotlyVolatilitySurface } from './PlotlyVolatilitySurface'
import { ErrorRetryBanner } from './ErrorRetryBanner'
import { ALL_FX_PAIRS } from '../constants/currencies'

// Define constants outside component to prevent recreating on each render
const TENORS = ['ON', '1W', '2W', '1M', '2M', '3M', '6M', '9M', '1Y', '18M']

export function VolatilityAnalysisTab() {
  const { currentTheme } = useTheme()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedPair, setSelectedPair] = useState('EURUSD')
  const [selectedTenor] = useState('1M')
  const [surfaceData, setSurfaceData] = useState<ValidatedVolatilityData[]>([])
  const [loadingProgress, setLoadingProgress] = useState<string>('')
  const [visibleTenorsForSmile, setVisibleTenorsForSmile] = useState<Set<string>>(new Set(['1M', '3M', '6M']))
  const [dataQualityScore, setDataQualityScore] = useState<number>(0)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [spotRates, setSpotRates] = useState<Record<string, number>>({})
  
  const smileChartRef = useRef<HTMLDivElement>(null)
  const termChartRef = useRef<HTMLDivElement>(null)
  
  // All FX pairs from constants
  const currencyPairs = [...ALL_FX_PAIRS]


  // Fetch spot rates for all currency pairs
  const fetchSpotRates = useCallback(async () => {
    try {
      // Build list of spot tickers
      const spotTickers = currencyPairs.map(pair => `${pair} Curncy`)
      
      const endpoint = import.meta.env.DEV 
        ? 'http://localhost:8000/api/bloomberg/reference'
        : 'http://20.172.249.92:8080/api/bloomberg/reference'
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer test',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          securities: spotTickers,
          fields: ['PX_LAST']
        })
      })
      
      if (!response.ok) {
        console.error('Failed to fetch spot rates:', response.statusText)
        return
      }
      
      const result = await response.json()
      
      if (result.success && result.data?.securities_data) {
        const rates: Record<string, number> = {}
        
        result.data.securities_data.forEach((sec: any) => {
          if (sec.success && sec.fields?.PX_LAST) {
            // Extract pair name from ticker (e.g., "EURUSD Curncy" -> "EURUSD")
            const pair = sec.security.replace(' Curncy', '')
            rates[pair] = sec.fields.PX_LAST
          }
        })
        
        console.log('Fetched spot rates:', rates)
        setSpotRates(rates)
      }
    } catch (error) {
      console.error('Error fetching spot rates:', error)
      // Don't fail the whole component if spot rates fail
    }
  }, [])
  
  const fetchData = useCallback(async () => {
    console.log('fetchData called for', selectedPair)
    setLoading(true)
    setError(null)
    setSurfaceData([])
    setLoadingProgress('Fetching all tenor data...')
    
    try {
      // FIXED: Use the optimized batch fetching - pass ALL tenors at once
      // The getVolatilitySurface function already handles batching internally
      console.log('Fetching all tenors in one batched call...', TENORS)
      const data = await bloombergAPI.getVolatilitySurface(selectedPair, TENORS)
      
      if (data && data.length > 0) {
        console.log(`Received ${data.length} volatility data points`)
        console.log('Tenors received:', data.map(d => d.tenor))
        
        // Calculate overall data quality
        const totalScore = data.reduce((sum, d) => sum + (d.quality?.completeness || 0), 0)
        const avgScore = Math.round(totalScore / data.length)
        setDataQualityScore(avgScore)
        
        // Set last update time
        setLastUpdate(new Date())
        
        setSurfaceData(data)
        setError(null) // Clear any previous errors
      } else {
        console.warn('No data received from Bloomberg API')
        setSurfaceData([])
        setError(`No volatility data available for ${selectedPair}`)
        setDataQualityScore(0)
      }
    } catch (err) {
      console.error('Bloomberg API failed:', err)
      console.error('Full error:', err)
      
      // Show real error - no error recovery
      const userMessage = err instanceof Error ? err.message : String(err)
      
      setError(userMessage)
      setSurfaceData([])
      setDataQualityScore(0)
    } finally {
      console.log('fetchData completed, setting loading to false')
      setLoading(false)
      setLoadingProgress('')
    }
  }, [selectedPair, fetchSpotRates])

  useEffect(() => {
    console.log('useEffect triggered, calling fetchData')
    fetchSpotRates() // Fetch spot rates on component mount
    fetchData()
  }, [fetchData, fetchSpotRates])

  // D3.js Term Structure Visualization - Simplified version from VolatilityAnalysisTabNew
  const drawTermStructureChart = useCallback(() => {
    if (!termChartRef.current || !surfaceData.length) return
    
    console.log('📊 Drawing term structure chart')
    const container = termChartRef.current
    d3.select(container).selectAll('*').remove()
    
    const margin = { top: 20, right: 20, bottom: 40, left: 50 }
    const width = container.clientWidth - margin.left - margin.right
    const height = container.clientHeight - margin.top - margin.bottom
    
    const svg = d3.select(container)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    
    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)
    
    // Convert tenor to days for x-axis
    const tenorToDays = (tenor: string): number => {
      const map: Record<string, number> = {
        'ON': 1, '1W': 7, '2W': 14, '1M': 30, '2M': 60, '3M': 90,
        '6M': 180, '9M': 270, '1Y': 365, '18M': 547, '2Y': 730
      }
      return map[tenor] || 30
    }
    
    // Prepare data
    const termData = surfaceData
      .filter(d => d.atm_mid && d.atm_mid > 0)
      .map(d => ({
        tenor: d.tenor,
        days: tenorToDays(d.tenor),
        volatility: d.atm_mid || 0
      }))
      .sort((a, b) => a.days - b.days)
    
    console.log('📈 Term structure data:', termData)
    
    if (termData.length === 0) {
      g.append('text')
        .attr('x', width/2)
        .attr('y', height/2)
        .attr('text-anchor', 'middle')
        .style('fill', currentTheme.textSecondary)
        .text('No term structure data available')
      return
    }
    
    // Scales
    const xScale = d3.scaleLinear()
      .domain(d3.extent(termData, d => d.days) as [number, number])
      .range([0, width])
    
    const yScale = d3.scaleLinear()
      .domain(d3.extent(termData, d => d.volatility) as [number, number])
      .range([height, 0])
    
    // Line generator
    const line = d3.line<typeof termData[0]>()
      .x(d => xScale(d.days))
      .y(d => yScale(d.volatility))
      .curve(d3.curveMonotoneX)
    
    // Draw line
    g.append('path')
      .datum(termData)
      .attr('fill', 'none')
      .attr('stroke', currentTheme.primary)
      .attr('stroke-width', 2)
      .attr('d', line)
    
    // Draw points
    g.selectAll('.point')
      .data(termData)
      .enter().append('circle')
      .attr('class', 'point')
      .attr('cx', d => xScale(d.days))
      .attr('cy', d => yScale(d.volatility))
      .attr('r', 3)
      .attr('fill', currentTheme.primary)
    
    // X-axis
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale))
      .selectAll('text')
      .style('fill', currentTheme.text)
    
    // Y-axis
    g.append('g')
      .call(d3.axisLeft(yScale))
      .selectAll('text')
      .style('fill', currentTheme.text)
    
    // Axis labels
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 0 - margin.left)
      .attr('x', 0 - (height / 2))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('fill', currentTheme.text)
      .text('Volatility (%)')
    
    g.append('text')
      .attr('transform', `translate(${width / 2}, ${height + margin.bottom - 5})`)
      .style('text-anchor', 'middle')
      .style('fill', currentTheme.text)
      .text('Days to Expiry')
  }, [surfaceData, currentTheme])

  // D3.js Volatility Smile Visualization - Multiple Tenor Curves
  const drawSmileChart = useCallback(() => {
    if (!smileChartRef.current) return
    
    // Clear previous chart
    d3.select(smileChartRef.current).selectAll("*").remove()
    
    if (!surfaceData.length) return

    // Get all smile curves for selected tenors
    const allSmileCurves: Array<{tenor: string, points: Array<{delta: number, vol: number, label: string, tenor: string}>}> = []
    
    console.log('Drawing smile curves for visible tenors:', Array.from(visibleTenorsForSmile))
    
    visibleTenorsForSmile.forEach(tenor => {
      // Find data by matching tenor name, not by index
      const data = surfaceData.find(d => d.tenor === tenor)
      if (!data) {
        console.warn(`No data found for tenor ${tenor}`)
        return
      }

      const atmMid = data.raw?.atm_bid && data.raw?.atm_ask ? (data.raw.atm_bid + data.raw.atm_ask) / 2 : null
      if (!atmMid) return

      const smilePoints = []
      
      // All available delta points from Bloomberg data
      const deltaData = [
        { delta: 5, rrBid: data.raw?.rr_5d_bid, rrAsk: data.raw?.rr_5d_ask, bfBid: data.raw?.bf_5d_bid, bfAsk: data.raw?.bf_5d_ask },
        { delta: 10, rrBid: data.raw?.rr_10d_bid, rrAsk: data.raw?.rr_10d_ask, bfBid: data.raw?.bf_10d_bid, bfAsk: data.raw?.bf_10d_ask },
        { delta: 15, rrBid: data.raw?.rr_15d_bid, rrAsk: data.raw?.rr_15d_ask, bfBid: data.raw?.bf_15d_bid, bfAsk: data.raw?.bf_15d_ask },
        { delta: 25, rrBid: data.raw?.rr_25d_bid, rrAsk: data.raw?.rr_25d_ask, bfBid: data.raw?.bf_25d_bid, bfAsk: data.raw?.bf_25d_ask },
        { delta: 35, rrBid: data.raw?.rr_35d_bid, rrAsk: data.raw?.rr_35d_ask, bfBid: data.raw?.bf_35d_bid, bfAsk: data.raw?.bf_35d_ask }
      ]

      deltaData.forEach(({ delta, rrBid, rrAsk, bfBid, bfAsk }) => {
        if (rrBid !== null && rrAsk !== null && bfBid !== null && bfAsk !== null) {
          const rrMid = (rrBid + rrAsk) / 2
          const bfMid = (bfBid + bfAsk) / 2
          
          // FX smile construction: Put Vol = ATM - RR/2 + BF, Call Vol = ATM + RR/2 + BF
          const putVol = atmMid - rrMid/2 + bfMid
          const callVol = atmMid + rrMid/2 + bfMid
          
          // Add put and call points
          smilePoints.push(
            { delta: delta, vol: putVol, label: `${delta}ΔP`, tenor },
            { delta: 100 - delta, vol: callVol, label: `${delta}ΔC`, tenor }
          )
        }
      })
      
      // ATM point
      smilePoints.push({ delta: 50, vol: atmMid, label: 'ATM', tenor })
      
      if (smilePoints.length > 0) {
        allSmileCurves.push({
          tenor,
          points: smilePoints.sort((a, b) => a.delta - b.delta)
        })
      }
    })

    if (allSmileCurves.length === 0) return

    // Clear previous chart
    d3.select(smileChartRef.current).selectAll("*").remove()

    const margin = { top: 20, right: 30, bottom: 40, left: 50 }
    const width = smileChartRef.current.clientWidth - margin.left - margin.right
    const height = smileChartRef.current.clientHeight - margin.top - margin.bottom

    const svg = d3.select(smileChartRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`)

    // Scales - fix overlapping by using proper delta range and fixed volatility range
    const xScale = d3.scaleLinear()
      .domain([5, 95]) // Full delta range from 5 to 95
      .range([0, width])

    // Fixed Y-axis range for better comparison across smiles
    const allSmilePoints = allSmileCurves.flatMap(curve => curve.points)
    const volExtent = d3.extent(allSmilePoints, d => d.vol) as [number, number]
    const yScale = d3.scaleLinear()
      .domain([Math.max(0, volExtent[0] - 0.5), volExtent[1] + 0.5]) // Add padding but start reasonable
      .range([height, 0])

    // Color scale for different tenors
    const colorScale = d3.scaleOrdinal()
      .domain(allSmileCurves.map(c => c.tenor))
      .range([currentTheme.primary, currentTheme.secondary || '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#F7DC6F'])

    // Minimal grid lines - only Y-axis
    g.selectAll(".grid-line-y")
      .data(yScale.ticks(3))
      .enter()
      .append("line")
      .attr("class", "grid-line-y")
      .attr("x1", 0)
      .attr("x2", width)
      .attr("y1", d => yScale(d))
      .attr("y2", d => yScale(d))
      .attr("stroke", currentTheme.border)
      .attr("stroke-width", 0.5)
      .attr("opacity", 0.2)

    // X-axis (no labels, we'll add custom ones below)
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale).tickSize(0).tickFormat(() => ""))
      .style("color", currentTheme.textSecondary)

    g.append("g")
      .call(d3.axisLeft(yScale).tickFormat(d => `${d}%`))
      .style("color", currentTheme.textSecondary)

    // Line generator
    const line = d3.line<any>()
      .x(d => xScale(d.delta))
      .y(d => yScale(d.vol))
      .curve(d3.curveCatmullRom.alpha(0.5))

    // Draw each tenor curve
    allSmileCurves.forEach((curve) => {
      const curveColor = colorScale(curve.tenor) as string
      const sortedPoints = curve.points.sort((a: any, b: any) => a.delta - b.delta)
      
      // Enhanced glow effect
      g.append("path")
        .datum(sortedPoints)
        .attr("fill", "none")
        .attr("stroke", curveColor)
        .attr("stroke-width", 1)
        .attr("stroke-opacity", 0.2)
        .attr("stroke-linejoin", "round")
        .attr("stroke-linecap", "round")
        .style("filter", "blur(3px)")
        .attr("d", line)

      // Main line with stronger presence
      g.append("path")
        .datum(sortedPoints)
        .attr("fill", "none")
        .attr("stroke", curveColor)
        .attr("stroke-width", 1.2)
        .attr("stroke-linejoin", "round")
        .attr("stroke-linecap", "round")
        .attr("d", line)
        .style("filter", "drop-shadow(0 1px 2px rgba(0,0,0,0.15))")

      // Enhanced tooltip on hover - no visible points for smile chart
      let smileTooltipDiv = d3.select("body").select(".smile-tooltip")
      if (smileTooltipDiv.empty()) {
        smileTooltipDiv = d3.select("body").append("div")
          .attr("class", "smile-tooltip")
          .style("opacity", 0)
          .style("position", "absolute")
          .style("background", currentTheme.surface)
          .style("border", `1px solid ${currentTheme.border}`)
          .style("border-radius", "6px")
          .style("padding", "10px")
          .style("font-size", "11px")
          .style("color", currentTheme.text)
          .style("pointer-events", "none")
          .style("box-shadow", "0 2px 8px rgba(0,0,0,0.15)")
          .style("backdrop-filter", "blur(10px)")
      }

      // Invisible overlay for mouse interaction on smile curve
      g.append("path")
        .datum(sortedPoints)
        .attr("fill", "none")
        .attr("stroke", "transparent")
        .attr("stroke-width", 20)
        .attr("d", line)
        .style("cursor", "crosshair")
        .on("mousemove", function(event) {
          const [mouseX] = d3.pointer(event)
          const deltaValue = xScale.invert(mouseX)
          
          // Find closest data point
          let closestPoint = sortedPoints[0]
          let minDist = Math.abs(closestPoint.delta - deltaValue)
          
          sortedPoints.forEach((p: any) => {
            const dist = Math.abs(p.delta - deltaValue)
            if (dist < minDist) {
              minDist = dist
              closestPoint = p
            }
          })
          
          smileTooltipDiv.transition()
            .duration(50)
            .style("opacity", .95)
          
          smileTooltipDiv.html(`
            <div style="font-weight: 600; margin-bottom: 6px; color: ${curveColor}">
              ${curve.tenor} Smile
            </div>
            <div style="display: flex; justify-content: space-between; gap: 20px;">
              <span style="color: ${currentTheme.textSecondary}">Strike:</span>
              <span style="font-weight: 500">${closestPoint.label}</span>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 20px;">
              <span style="color: ${currentTheme.textSecondary}">Volatility:</span>
              <span style="font-weight: 500">${closestPoint.vol.toFixed(3)}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 20px; margin-top: 4px; padding-top: 4px; border-top: 1px solid ${currentTheme.border}">
              <span style="color: ${currentTheme.textSecondary}; font-size: 10px">Delta:</span>
              <span style="font-size: 10px">${closestPoint.delta}Δ</span>
            </div>
          `)
            .style("left", (event.pageX + 15) + "px")
            .style("top", (event.pageY - 40) + "px")
        })
        .on("mouseout", function() {
          smileTooltipDiv.transition()
            .duration(200)
            .style("opacity", 0)
        })
    })

    // Legend for tenors
    const legend = g.append("g")
      .attr("class", "legend")
      .attr("transform", `translate(10, 10)`)

    allSmileCurves.forEach((curve, index) => {
      const legendItem = legend.append("g")
        .attr("transform", `translate(0, ${index * 15})`)

      legendItem.append("line")
        .attr("x1", 0)
        .attr("x2", 15)
        .attr("y1", 0)
        .attr("y2", 0)
        .attr("stroke", colorScale(curve.tenor) as string)
        .attr("stroke-width", 1.2)

      legendItem.append("text")
        .attr("x", 20)
        .attr("y", 0)
        .attr("dy", "0.35em")
        .style("font-size", "9px")
        .style("fill", currentTheme.textSecondary)
        .text(curve.tenor)
    })

    // Show all available delta points
    const availableDeltas = [...new Set(allSmilePoints.map(p => p.delta))].sort((a, b) => a - b)
    
    // Use real spot rates from Bloomberg or show warning
    const getSpotRate = (pair: string) => {
      // First check if we have real Bloomberg spot rates
      if (spotRates[pair]) {
        return spotRates[pair]
      }
      
      // If no real rate available, return null to indicate missing data
      console.warn(`No Bloomberg spot rate available for ${pair}`)
      return null
    }
    const spotRate = getSpotRate(selectedPair)
    
    // Calculate strikes using simplified Black-Scholes delta-to-strike conversion
    const calculateStrike = (delta: number, vol: number) => {
      // If no spot rate available, return null
      if (!spotRate) return null
      
      // Convert tenor to time in years
      const tenorToYears = (tenor: string): number => {
        const map: Record<string, number> = {
          'ON': 1/365, '1W': 7/365, '2W': 14/365, '1M': 30/365, '2M': 60/365, '3M': 90/365,
          '6M': 180/365, '9M': 270/365, '1Y': 1.0, '18M': 1.5, '2Y': 2.0
        }
        return map[tenor] || 0
      }
      
      const timeToExpiry = tenorToYears(selectedTenor)
      
      // Simplified strike calculation: K = F * exp(-N^(-1)(delta) * vol * sqrt(T))
      // Where N^(-1) is inverse normal CDF
      if (delta === 50) return spotRate // ATM
      
      // Rough approximation of inverse normal CDF for common deltas
      const invNorm = delta < 50 
        ? (delta === 5 ? -1.645 : delta === 10 ? -1.282 : delta === 15 ? -1.036 : delta === 25 ? -0.674 : delta === 35 ? -0.385 : -0.674)
        : (delta === 65 ? 0.385 : delta === 75 ? 0.674 : delta === 85 ? 1.036 : delta === 90 ? 1.282 : delta === 95 ? 1.645 : 0.674)
      
      return spotRate * Math.exp(-invNorm * (vol/100) * Math.sqrt(timeToExpiry))
    }
    
    const deltaLabels = availableDeltas.map(delta => {
      const point = allSmilePoints.find(p => p.delta === delta)
      const strike = point ? calculateStrike(delta, point.vol) : spotRate
      
      return {
        delta,
        strike,
        label: delta === 50 ? 'ATM' : delta < 50 ? `${delta}ΔP` : `${100-delta}ΔC`,
        strikeLabel: strike ? strike.toFixed(4) : 'N/A',
        color: delta === 50 ? currentTheme.primary : currentTheme.textSecondary
      }
    })

    const deltaLabelGroups = g.selectAll(".delta-label-group")
      .data(deltaLabels)
      .enter()
      .append("g")
      .attr("class", "delta-label-group")
      .attr("transform", (d: any) => `translate(${xScale(d.delta)}, 0)`)
    
    // Delta labels (top line)
    deltaLabelGroups
      .append("text")
      .attr("class", "delta-label")
      .attr("x", 0)
      .attr("y", height + 15)
      .attr("text-anchor", "middle")
      .style("font-size", "10px")
      .style("font-weight", (d: any) => d.delta === 50 ? "700" : "500")
      .style("fill", (d: any) => d.color)
      .text((d: any) => d.label)
    
    // Strike labels (bottom line)
    deltaLabelGroups
      .append("text")
      .attr("class", "strike-label")
      .attr("x", 0)
      .attr("y", height + 28)
      .attr("text-anchor", "middle")
      .style("font-size", "9px")
      .style("font-weight", "400")
      .style("fill", currentTheme.textSecondary)
      .style("opacity", 0.8)
      .text((d: any) => d.strikeLabel)

    // Axis labels
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - (height / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .style("fill", currentTheme.textSecondary)
      .text("Implied Volatility (%)")

    g.append("text")
      .attr("transform", `translate(${width/2}, ${height + margin.bottom})`)
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .style("fill", currentTheme.textSecondary)
      .text("Delta")

    // Add status about strike prices
    if (!spotRate) {
      g.append("text")
        .attr("transform", `translate(${width - 10}, 10)`)
        .style("text-anchor", "end")
        .style("font-size", "10px")
        .style("fill", currentTheme.danger || '#f44336')
        .style("font-style", "italic")
        .text("⚠️ No Bloomberg spot rate available")
    }

  }, [surfaceData, selectedTenor, currentTheme, visibleTenorsForSmile, selectedPair, spotRates])


  useEffect(() => {
    console.log('🎯 Chart render useEffect triggered:', { 
      surfaceDataLength: surfaceData.length, 
      loading,
      shouldRender: surfaceData.length > 0 && !loading 
    })
    if (surfaceData.length > 0 && !loading) {
      // Add a small delay to ensure DOM is ready
      const timer = setTimeout(() => {
        console.log('⏰ Drawing charts after 100ms delay')
        drawSmileChart()
        drawTermStructureChart()
      }, 100)
      
      return () => clearTimeout(timer)
    }
  }, [surfaceData, loading, drawSmileChart, drawTermStructureChart])

  return (
    <div style={{
      backgroundColor: currentTheme.surface,
      borderRadius: '8px',
      border: `1px solid ${currentTheme.border}`,
      overflow: 'hidden',
      height: '100%'
    }}>
      {/* Header */}
      <div style={{
        padding: '16px',
        borderBottom: `1px solid ${currentTheme.border}`,
        display: 'flex',
        gap: '16px',
        alignItems: 'center'
      }}>
        <div>
          <label style={{ fontSize: '12px', color: currentTheme.textSecondary, marginRight: '8px' }}>
            Currency Pair:
          </label>
          <select
            value={selectedPair}
            onChange={(e) => {
              setSelectedPair(e.target.value)
              fetchSpotRates() // Refresh spot rates when pair changes
            }}
            style={{
              backgroundColor: currentTheme.background,
              color: currentTheme.text,
              border: `1px solid ${currentTheme.border}`,
              borderRadius: '4px',
              padding: '4px 8px',
              fontSize: '12px'
            }}
          >
            {currencyPairs.map(pair => (
              <option key={pair} value={pair}>{pair}</option>
            ))}
          </select>
        </div>
        
        <button
          onClick={fetchData}
          disabled={loading}
          style={{
            backgroundColor: currentTheme.primary,
            color: currentTheme.background,
            border: 'none',
            borderRadius: '4px',
            padding: '6px 12px',
            fontSize: '12px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1
          }}
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>
        
        
        <div style={{ 
          marginLeft: 'auto',
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          fontSize: '11px',
          color: currentTheme.textSecondary 
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <span>Data Quality:</span>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '2px 8px',
              borderRadius: '12px',
              backgroundColor: getQualityColor(dataQualityScore) + '20',
              border: `1px solid ${getQualityColor(dataQualityScore)}40`
            }}>
              <div style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                backgroundColor: getQualityColor(dataQualityScore)
              }} />
              <span style={{ 
                color: getQualityColor(dataQualityScore),
                fontWeight: '600'
              }}>
                {dataQualityScore}%
              </span>
            </div>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}>
            <span>Updated:</span>
            <span style={{ fontWeight: '500' }}>
              {lastUpdate ? lastUpdate.toLocaleTimeString() : 'Never'}
            </span>
          </div>
        </div>
      </div>

      {error && (
        <ErrorRetryBanner 
          error={error}
          onRetry={fetchData}
          retrying={loading}
        />
      )}

      {/* Layout with full right side for 3D surface */}
      <div style={{
        display: 'flex',
        gap: '2px',
        backgroundColor: currentTheme.border,
        height: 'calc(100% - 80px)'
      }}>
        
        {/* Left Column: Smile and Term Structure */}
        <div style={{
          flex: '0 0 50%',
          display: 'flex',
          flexDirection: 'column',
          gap: '2px'
        }}>
        
          {/* Volatility Smile Section */}
          <div style={{
            flex: '1',
            backgroundColor: currentTheme.background,
            padding: '12px',
            display: 'flex',
            flexDirection: 'column'
          }}>
          <h3 style={{ 
            fontSize: '13px', 
            fontWeight: '600', 
            margin: '0 0 8px 0',
            color: currentTheme.text,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span>Volatility Smile - {selectedPair}</span>
          </h3>
          
          {/* Tenor selection buttons */}
          <div style={{
            display: 'flex',
            gap: '2px',
            marginBottom: '8px',
            flexWrap: 'wrap'
          }}>
            {TENORS.slice(0, 6).map(tenor => (
              <button
                key={tenor}
                onClick={() => {
                  const newVisibleTenors = new Set(visibleTenorsForSmile)
                  if (newVisibleTenors.has(tenor)) {
                    newVisibleTenors.delete(tenor)
                  } else {
                    newVisibleTenors.add(tenor)
                  }
                  setVisibleTenorsForSmile(newVisibleTenors)
                }}
                style={{
                  fontSize: '9px',
                  padding: '2px 6px',
                  backgroundColor: visibleTenorsForSmile.has(tenor) ? currentTheme.primary : currentTheme.surface,
                  color: visibleTenorsForSmile.has(tenor) ? currentTheme.background : currentTheme.textSecondary,
                  border: `1px solid ${currentTheme.border}`,
                  borderRadius: '3px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                {tenor}
              </button>
            ))}
          </div>
          
          <div style={{ 
            flex: 1,
            minHeight: '0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: `1px solid ${currentTheme.border}20`,
            borderRadius: '4px',
            backgroundColor: currentTheme.surface + '30'
          }}>
            <div ref={smileChartRef} style={{ width: '100%', height: '100%' }}>
              {(loading || surfaceData.length === 0) && (
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  height: '100%',
                  color: currentTheme.textSecondary,
                  fontSize: '11px'
                }}>
                  Loading smile data...
                </div>
              )}
            </div>
          </div>
          </div>
          
          {/* Term Structure Section */}
          <div style={{
            flex: '1',
            backgroundColor: currentTheme.background,
            padding: '12px',
            display: 'flex',
            flexDirection: 'column'
          }}>
          <h3 style={{ 
            fontSize: '13px', 
            fontWeight: '600', 
            margin: '0 0 8px 0',
            color: currentTheme.text 
          }}>
            Term Structure - {selectedPair}
          </h3>
          
          <div style={{ 
            flex: 1,
            minHeight: '0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: `1px solid ${currentTheme.border}20`,
            borderRadius: '4px',
            backgroundColor: currentTheme.surface + '30'
          }}>
            <div ref={termChartRef} style={{ width: '100%', height: '100%' }}>
              {(loading || surfaceData.length === 0) && (
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  height: '100%',
                  color: currentTheme.textSecondary,
                  fontSize: '11px'
                }}>
                  Loading term structure...
                </div>
              )}
            </div>
          </div>
          </div>
        </div>
        
        {/* Right Column: Full height 3D Surface */}
        <div style={{
          flex: '1',
          backgroundColor: currentTheme.background,
          padding: '12px',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <h3 style={{ 
            fontSize: '13px', 
            fontWeight: '600', 
            margin: '0 0 8px 0',
            color: currentTheme.text 
          }}>
            3D Volatility Surface - {selectedPair}
          </h3>
          
          <div style={{ 
            flex: 1,
            minHeight: '0',
            border: `1px solid ${currentTheme.border}20`,
            borderRadius: '4px',
            backgroundColor: currentTheme.surface + '30',
            display: 'flex',
            alignItems: (loading || surfaceData.length === 0) ? 'center' : 'stretch',
            justifyContent: (loading || surfaceData.length === 0) ? 'center' : 'stretch',
            color: currentTheme.textSecondary,
            fontSize: '12px',
            overflow: 'hidden'
          }}>
            {loading ? (
              <div style={{ textAlign: 'center' }}>
                <span style={{ fontSize: '11px', display: 'block' }}>Loading 3D surface...</span>
                {loadingProgress && (
                  <span style={{ fontSize: '10px', display: 'block', marginTop: '4px', color: currentTheme.primary }}>
                    {loadingProgress}
                  </span>
                )}
              </div>
            ) : surfaceData.length === 0 ? (
              <div style={{ textAlign: 'center' }}>
                <span style={{ fontSize: '11px', display: 'block' }}>No data available</span>
              </div>
            ) : (
              <PlotlyVolatilitySurface surfaceData={surfaceData} selectedPair={selectedPair} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}