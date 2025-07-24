import { useState, useEffect, useCallback, useRef } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import { bloombergAPI } from '../api/bloomberg'
import { ValidatedVolatilityData, getQualityColor } from '../utils/dataValidation'
import * as d3 from 'd3'
import { PlotlyVolatilitySurface } from './PlotlyVolatilitySurface'
import { ErrorRetryBanner } from './ErrorRetryBanner'

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
  const [visibleDeltasForTerm, setVisibleDeltasForTerm] = useState<Set<number>>(new Set([10, 25]))
  const [dataQualityScore, setDataQualityScore] = useState<number>(0)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  
  const smileChartRef = useRef<HTMLDivElement>(null)
  const termChartRef = useRef<HTMLDivElement>(null)
  
  // Major FX pairs for volatility trading
  const currencyPairs = [
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
        const totalScore = data.reduce((sum, d) => sum + d.quality.completenessScore, 0)
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
      
      // Use the error recovery utility to get user-friendly message
      const { BloombergErrorRecovery } = await import('../utils/errorRecovery')
      const userMessage = BloombergErrorRecovery.getErrorMessage(err)
      
      setError(userMessage)
      setSurfaceData([])
      setDataQualityScore(0)
    } finally {
      console.log('fetchData completed, setting loading to false')
      setLoading(false)
      setLoadingProgress('')
    }
  }, [selectedPair])

  useEffect(() => {
    console.log('useEffect triggered, calling fetchData')
    fetchData()
  }, [fetchData])

  // D3.js Term Structure Visualization
  const drawTermStructureChart = useCallback(() => {
    if (!termChartRef.current) return
    
    // Clear previous chart
    d3.select(termChartRef.current).selectAll("*").remove()
    
    if (!surfaceData.length) return

    // Get all term structure curves for selected deltas
    const allTermCurves: Array<{delta: number, points: Array<{tenor: string, vol: number, sortKey: number, delta: number}>}> = []
    
    console.log('Drawing term structure for visible deltas:', Array.from(visibleDeltasForTerm))
    
    visibleDeltasForTerm.forEach(delta => {
      const termPoints: Array<{tenor: string, vol: number, sortKey: number, delta: number}> = []
      
      surfaceData.forEach(data => {
        if (!data.atm_bid || !data.atm_ask) return
        
        const atmMid = (data.atm_bid + data.atm_ask) / 2
        let deltaVol = atmMid // Default to ATM
        
        // Calculate volatility for this delta
        if (delta !== 50) {
          let rr = 0, bf = 0
          
          switch(delta) {
            case 5:
              rr = data.rr_5d_bid && data.rr_5d_ask ? (data.rr_5d_bid + data.rr_5d_ask) / 2 : 0
              bf = data.bf_5d_bid && data.bf_5d_ask ? (data.bf_5d_bid + data.bf_5d_ask) / 2 : 0
              break
            case 10:
              rr = data.rr_10d_bid && data.rr_10d_ask ? (data.rr_10d_bid + data.rr_10d_ask) / 2 : 0
              bf = data.bf_10d_bid && data.bf_10d_ask ? (data.bf_10d_bid + data.bf_10d_ask) / 2 : 0
              break
            case 15:
              rr = data.rr_15d_bid && data.rr_15d_ask ? (data.rr_15d_bid + data.rr_15d_ask) / 2 : 0
              bf = data.bf_15d_bid && data.bf_15d_ask ? (data.bf_15d_bid + data.bf_15d_ask) / 2 : 0
              break
            case 25:
              rr = data.rr_25d_bid && data.rr_25d_ask ? (data.rr_25d_bid + data.rr_25d_ask) / 2 : 0
              bf = data.bf_25d_bid && data.bf_25d_ask ? (data.bf_25d_bid + data.bf_25d_ask) / 2 : 0
              break
            case 35:
              rr = data.rr_35d_bid && data.rr_35d_ask ? (data.rr_35d_bid + data.rr_35d_ask) / 2 : 0
              bf = data.bf_35d_bid && data.bf_35d_ask ? (data.bf_35d_bid + data.bf_35d_ask) / 2 : 0
              break
          }
          
          // Calculate put vol: ATM - RR/2 + BF
          deltaVol = atmMid - rr/2 + bf
        }
        
        termPoints.push({
          tenor: data.tenor,
          vol: deltaVol,
          sortKey: TENORS.indexOf(data.tenor),
          delta
        })
      })
      
      if (termPoints.length > 0) {
        allTermCurves.push({
          delta,
          points: termPoints.sort((a, b) => a.sortKey - b.sortKey)
        })
      }
    })

    if (allTermCurves.length === 0) return

    // Clear previous chart
    d3.select(termChartRef.current).selectAll("*").remove()

    const margin = { top: 20, right: 30, bottom: 40, left: 50 }
    const width = termChartRef.current.clientWidth - margin.left - margin.right
    const height = termChartRef.current.clientHeight - margin.top - margin.bottom

    const svg = d3.select(termChartRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`)

    // Get all data points for scale calculations
    const allPoints = allTermCurves.flatMap(curve => curve.points)
    const allTenors = [...new Set(allPoints.map(p => p.tenor))].sort((a, b) => TENORS.indexOf(a) - TENORS.indexOf(b))
    const volExtent = d3.extent(allPoints, d => d.vol) as [number, number]

    // Scales
    const xScale = d3.scaleBand()
      .domain(allTenors)
      .range([0, width])
      .padding(0.3)

    if (!xScale.bandwidth) return

    const yScale = d3.scaleLinear()
      .domain([Math.max(0, volExtent[0] - 0.5), volExtent[1] + 0.5])
      .range([height, 0])

    // Color scale for different deltas
    const colorScale = d3.scaleOrdinal()
      .domain(allTermCurves.map(c => c.delta.toString()))
      .range([currentTheme.primary, currentTheme.secondary || '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])

    // Grid lines - Y-axis only
    g.selectAll(".grid-line-y")
      .data(yScale.ticks(4))
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

    // Axes
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale))
      .style("color", currentTheme.textSecondary)

    g.append("g")
      .call(d3.axisLeft(yScale).tickFormat(d => `${d}%`))
      .style("color", currentTheme.textSecondary)

    // Line generator
    const line = d3.line<any>()
      .x(d => (xScale(d.tenor) || 0) + (xScale.bandwidth() || 0) / 2)
      .y(d => yScale(d.vol))
      .curve(d3.curveCatmullRom)

    // Draw each delta curve
    allTermCurves.forEach((curve) => {
      const curveColor = colorScale(curve.delta.toString()) as string
      
      // Glow effect
      g.append("path")
        .datum(curve.points)
        .attr("fill", "none")
        .attr("stroke", curveColor)
        .attr("stroke-width", 4)
        .attr("stroke-opacity", 0.3)
        .attr("stroke-linejoin", "round")
        .attr("stroke-linecap", "round")
        .style("filter", "blur(2px)")
        .attr("d", line)

      // Main line
      g.append("path")
        .datum(curve.points)
        .attr("fill", "none")
        .attr("stroke", curveColor)
        .attr("stroke-width", 2.5)
        .attr("stroke-linejoin", "round")
        .attr("stroke-linecap", "round")
        .attr("d", line)
        .style("filter", "drop-shadow(0 2px 4px rgba(0,0,0,0.2))")

      // Points with hover
      const pointGroup = g.selectAll(`.term-point-group-${curve.delta}`)
        .data(curve.points)
        .enter()
        .append("g")
        .attr("class", `term-point-group-${curve.delta}`)
        .attr("transform", (d: any) => `translate(${(xScale(d.tenor) || 0) + (xScale.bandwidth() || 0) / 2}, ${yScale(d.vol)})`)
        .style("cursor", "pointer")

      // Outer circle
      pointGroup.append("circle")
        .attr("r", 5)
        .attr("fill", curveColor)
        .attr("fill-opacity", 0.3)

      // Inner circle
      pointGroup.append("circle")
        .attr("r", 3)
        .attr("fill", currentTheme.background)
        .attr("stroke", curveColor)
        .attr("stroke-width", 2)

      // Hover tooltip
      const tooltip = pointGroup.append("g")
        .attr("class", "tooltip")
        .attr("transform", "translate(0, -25)")
        .style("opacity", 0)

      tooltip.append("rect")
        .attr("x", -25)
        .attr("y", -12)
        .attr("width", 50)
        .attr("height", 20)
        .attr("rx", 3)
        .attr("fill", currentTheme.surface)
        .attr("stroke", curveColor)
        .attr("stroke-width", 1)
        .style("filter", "drop-shadow(0 2px 4px rgba(0,0,0,0.3))")

      tooltip.append("text")
        .attr("text-anchor", "middle")
        .attr("y", -2)
        .style("font-size", "9px")
        .style("font-weight", "600")
        .style("fill", currentTheme.text)
        .text((d: any) => `${curve.delta}Δ: ${d.vol.toFixed(2)}%`)

      pointGroup
        .on("mouseenter", function() {
          d3.select(this).select(".tooltip")
            .transition()
            .duration(200)
            .style("opacity", 1)
        })
        .on("mouseleave", function() {
          d3.select(this).select(".tooltip")
            .transition()
            .duration(200)
            .style("opacity", 0)
        })
    })

    // Legend
    const legend = g.append("g")
      .attr("class", "legend")
      .attr("transform", `translate(${width - 80}, 10)`)

    allTermCurves.forEach((curve, index) => {
      const legendItem = legend.append("g")
        .attr("transform", `translate(0, ${index * 15})`)

      legendItem.append("line")
        .attr("x1", 0)
        .attr("x2", 15)
        .attr("y1", 0)
        .attr("y2", 0)
        .attr("stroke", colorScale(curve.delta.toString()) as string)
        .attr("stroke-width", 2)

      legendItem.append("text")
        .attr("x", 20)
        .attr("y", 0)
        .attr("dy", "0.35em")
        .style("font-size", "9px")
        .style("fill", currentTheme.textSecondary)
        .text(`${curve.delta}Δ`)
    })

    // Axis labels
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - (height / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font-size", "11px")
      .style("fill", currentTheme.textSecondary)
      .text("ATM Volatility (%)")

    g.append("text")
      .attr("transform", `translate(${width/2}, ${height + margin.bottom - 5})`)
      .style("text-anchor", "middle")
      .style("font-size", "11px")
      .style("fill", currentTheme.textSecondary)
      .text("Tenor")

  }, [surfaceData, currentTheme, visibleDeltasForTerm])

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

      const atmMid = data.atm_bid && data.atm_ask ? (data.atm_bid + data.atm_ask) / 2 : null
      if (!atmMid) return

      const smilePoints = []
      
      // All available delta points from Bloomberg data
      const deltaData = [
        { delta: 5, rrBid: data.rr_5d_bid, rrAsk: data.rr_5d_ask, bfBid: data.bf_5d_bid, bfAsk: data.bf_5d_ask },
        { delta: 10, rrBid: data.rr_10d_bid, rrAsk: data.rr_10d_ask, bfBid: data.bf_10d_bid, bfAsk: data.bf_10d_ask },
        { delta: 15, rrBid: data.rr_15d_bid, rrAsk: data.rr_15d_ask, bfBid: data.bf_15d_bid, bfAsk: data.bf_15d_ask },
        { delta: 25, rrBid: data.rr_25d_bid, rrAsk: data.rr_25d_ask, bfBid: data.bf_25d_bid, bfAsk: data.bf_25d_ask },
        { delta: 35, rrBid: data.rr_35d_bid, rrAsk: data.rr_35d_ask, bfBid: data.bf_35d_bid, bfAsk: data.bf_35d_ask }
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
        .attr("stroke-width", 6)
        .attr("stroke-opacity", 0.3)
        .attr("stroke-linejoin", "round")
        .attr("stroke-linecap", "round")
        .style("filter", "blur(3px)")
        .attr("d", line)

      // Main line with stronger presence
      g.append("path")
        .datum(sortedPoints)
        .attr("fill", "none")
        .attr("stroke", curveColor)
        .attr("stroke-width", 2.5)
        .attr("stroke-linejoin", "round")
        .attr("stroke-linecap", "round")
        .attr("d", line)
        .style("filter", "drop-shadow(0 2px 4px rgba(0,0,0,0.2))")

      // Modern hover points - only show on hover
      const pointGroup = g.selectAll(`.point-group-${curve.tenor}`)
        .data(sortedPoints)
        .enter()
        .append("g")
        .attr("class", `point-group-${curve.tenor}`)
        .attr("transform", (d: any) => `translate(${xScale(d.delta)}, ${yScale(d.vol)})`)
        .style("opacity", 0)
        .style("cursor", "pointer")

      // Outer glow circle
      pointGroup.append("circle")
        .attr("r", 6)
        .attr("fill", curveColor)
        .attr("fill-opacity", 0.2)
        .attr("stroke", "none")

      // Inner circle
      pointGroup.append("circle")
        .attr("r", 3)
        .attr("fill", currentTheme.background)
        .attr("stroke", curveColor)
        .attr("stroke-width", 2)

      // Modern tooltip box
      const tooltip = pointGroup.append("g")
        .attr("class", "tooltip")
        .attr("transform", "translate(0, -25)")

      tooltip.append("rect")
        .attr("x", -25)
        .attr("y", -12)
        .attr("width", 50)
        .attr("height", 20)
        .attr("rx", 4)
        .attr("fill", currentTheme.surface)
        .attr("stroke", curveColor)
        .attr("stroke-width", 1)
        .style("filter", "drop-shadow(0 2px 4px rgba(0,0,0,0.3))")

      tooltip.append("text")
        .attr("text-anchor", "middle")
        .attr("y", -2)
        .style("font-size", "9px")
        .style("font-weight", "600")
        .style("fill", currentTheme.text)
        .text((d: any) => `${curve.tenor}: ${d.vol.toFixed(2)}%`)

      // Hover interactions
      pointGroup
        .on("mouseenter", function() {
          d3.select(this)
            .transition()
            .duration(200)
            .style("opacity", 1)
        })
        .on("mouseleave", function() {
          d3.select(this)
            .transition()
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
        .attr("stroke-width", 2.5)

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
    
    // Estimate forward price based on currency pair
    // In production, fetch actual spot rates from Bloomberg
    const getEstimatedSpot = (pair: string) => {
      const spotRates: Record<string, number> = {
        // Major USD pairs
        'EURUSD': 1.08,
        'GBPUSD': 1.26,
        'USDJPY': 148.50,
        'USDCHF': 0.89,
        'AUDUSD': 0.65,
        'USDCAD': 1.35,
        'NZDUSD': 0.61,
        // EUR crosses
        'EURGBP': 0.857,
        'EURJPY': 160.38,
        'EURCHF': 0.961,
        'EURAUD': 1.662,
        'EURCAD': 1.458,
        'EURNZD': 1.770,
        // GBP crosses
        'GBPJPY': 187.11,
        'GBPCHF': 1.121,
        'GBPAUD': 1.938,
        'GBPCAD': 1.701,
        'GBPNZD': 2.066,
        // JPY crosses
        'AUDJPY': 96.53,
        'CADJPY': 110.00,
        'NZDJPY': 90.60,
        'CHFJPY': 166.85,
        // Other crosses
        'AUDCAD': 0.878,
        'AUDCHF': 0.578,
        'AUDNZD': 1.066,
        'CADCHF': 0.659,
        'NZDCAD': 0.823,
        'NZDCHF': 0.542
      }
      return spotRates[pair] || 1.0
    }
    const estimatedForward = getEstimatedSpot(selectedPair)
    
    // Calculate strikes using simplified Black-Scholes delta-to-strike conversion
    const calculateStrike = (delta: number, vol: number) => {
      // Convert tenor to years (rough approximation)
      const tenorToYears: Record<string, number> = {
        'ON': 1/365, '1W': 7/365, '2W': 14/365, '1M': 30/365, 
        '2M': 60/365, '3M': 90/365, '6M': 180/365, '9M': 270/365, 
        '1Y': 1, '18M': 1.5
      }
      const timeToExpiry = tenorToYears[selectedTenor] || 30/365
      
      // Simplified strike calculation: K = F * exp(-N^(-1)(delta) * vol * sqrt(T))
      // Where N^(-1) is inverse normal CDF
      if (delta === 50) return estimatedForward // ATM
      
      // Rough approximation of inverse normal CDF for common deltas
      const invNorm = delta < 50 
        ? (delta === 5 ? -1.645 : delta === 10 ? -1.282 : delta === 15 ? -1.036 : delta === 25 ? -0.674 : delta === 35 ? -0.385 : -0.674)
        : (delta === 65 ? 0.385 : delta === 75 ? 0.674 : delta === 85 ? 1.036 : delta === 90 ? 1.282 : delta === 95 ? 1.645 : 0.674)
      
      return estimatedForward * Math.exp(-invNorm * (vol/100) * Math.sqrt(timeToExpiry))
    }
    
    const deltaLabels = availableDeltas.map(delta => {
      const point = allSmilePoints.find(p => p.delta === delta)
      const strike = point ? calculateStrike(delta, point.vol) : estimatedForward
      
      return {
        delta,
        strike,
        label: delta === 50 ? 'ATM' : delta < 50 ? `${delta}ΔP` : `${100-delta}ΔC`,
        strikeLabel: strike.toFixed(4),
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

  }, [surfaceData, selectedTenor, currentTheme, visibleTenorsForSmile, visibleDeltasForTerm, selectedPair])


  useEffect(() => {
    if (surfaceData.length > 0 && !loading) {
      // Add a small delay to ensure DOM is ready
      const timer = setTimeout(() => {
        drawSmileChart()
        drawTermStructureChart()
      }, 100)
      
      return () => clearTimeout(timer)
    }
  }, [surfaceData, selectedTenor, currentTheme, visibleTenorsForSmile, visibleDeltasForTerm, drawSmileChart, drawTermStructureChart, selectedPair, loading])

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
            onChange={(e) => setSelectedPair(e.target.value)}
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
          
          {/* Delta selection buttons */}
          <div style={{
            display: 'flex',
            gap: '2px',
            marginBottom: '8px',
            flexWrap: 'wrap'
          }}>
            {[5, 10, 15, 25, 35, 50].map(delta => (
              <button
                key={delta}
                onClick={() => {
                  const newVisibleDeltas = new Set(visibleDeltasForTerm)
                  if (newVisibleDeltas.has(delta)) {
                    newVisibleDeltas.delete(delta)
                  } else {
                    newVisibleDeltas.add(delta)
                  }
                  setVisibleDeltasForTerm(newVisibleDeltas)
                }}
                style={{
                  fontSize: '9px',
                  padding: '2px 6px',
                  backgroundColor: visibleDeltasForTerm.has(delta) ? currentTheme.primary : currentTheme.surface,
                  color: visibleDeltasForTerm.has(delta) ? currentTheme.background : currentTheme.textSecondary,
                  border: `1px solid ${currentTheme.border}`,
                  borderRadius: '3px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                {delta === 50 ? 'ATM' : `${delta}Δ`}
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