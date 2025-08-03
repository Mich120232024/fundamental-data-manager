import { useState, useEffect, useRef } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import * as d3 from 'd3'
import { Currency, ALL_CURRENCIES } from '../constants/currencies'
import { getCurveNameForCurrency, getCurveTickers, type DatabaseTicker } from '../api/database'
// import { YIELD_CURVE_CONFIGS } from '../data/yieldCurveConfigs'

// Empty configs - no hardcoded data
const YIELD_CURVE_CONFIGS: Record<Currency, CurveConfig> = {} as any

interface CurvePoint {
  tenor: number     // Days to maturity
  years: number     // Years to maturity for proper scaling
  rate: number      // Rate in %
  label: string     // Display label
  ticker: string    // Bloomberg ticker
  instrumentType: 'money_market' | 'swap' | 'bond'
  isInterpolated?: boolean
}

interface CurveConfig {
  title: string
  instruments: Array<{
    ticker: string
    tenor: number
    label: string
    years: number
    instrumentType: 'money_market' | 'swap' | 'bond'
  }>
}

export function YieldCurvesTab() {
  const { currentTheme } = useTheme()
  const chartContainerRef = useRef<HTMLDivElement>(null)
  
  // Controls
  const [selectedCurrencies, setSelectedCurrencies] = useState<Set<Currency>>(new Set(['USD']))
  const [showGrid, setShowGrid] = useState(true)
  const [showLegend, setShowLegend] = useState(true)
  const [showInterpolated, setShowInterpolated] = useState(true)
  
  // Data
  const [curveData, setCurveData] = useState<Map<Currency, CurvePoint[]>>(new Map())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [zoomRange, setZoomRange] = useState(30) // Default to full 0-30Y view
  const [useLogScale, setUseLogScale] = useState(false) // Toggle log scale for x-axis
  const [viewMode, setViewMode] = useState<'2Y' | '10Y' | 'full'>('full') // View mode selection

  // Professional color palette
  const currencyColors: Record<Currency, string> = {
    USD: '#2E7D32',  // Forest green
    EUR: '#1976D2',  // Royal blue
    GBP: '#D32F2F',  // Deep red
    JPY: '#7B1FA2',  // Purple
    CHF: '#F57C00',  // Orange
    AUD: '#00897B',  // Teal
    CAD: '#E91E63',  // Pink
    NZD: '#00ACC1',  // Cyan
    SEK: '#FDD835',  // Yellow
    NOK: '#6A4C93',  // Indigo
    DKK: '#8E24AA',  // Deep purple
    ISK: '#E53935',  // Light red
    // Emerging Markets
    ZAR: '#F44336',  // Red
    PLN: '#E91E63',  // Pink
    CZK: '#9C27B0',  // Purple
    HUF: '#673AB7',  // Deep Purple
    HKD: '#3F51B5',  // Indigo
    TRY: '#2196F3',  // Blue
    MXN: '#03A9F4',  // Light Blue
    CNH: '#00BCD4',  // Cyan
    KRW: '#009688',  // Teal
    THB: '#4CAF50',  // Green
    TWD: '#8BC34A',  // Light Green
    SGD: '#CDDC39',  // Lime
    INR: '#FFEB3B',  // Yellow
    PHP: '#FFC107',  // Amber
    RUB: '#FF9800',  // Orange
    BRL: '#FF5722',  // Deep Orange
    ILS: '#795548'   // Brown
  }
  
  // Available curves - All G10 currencies are setup in database
  const availableCurves: Currency[] = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD', 'SEK', 'NOK']

  // Yield curve configurations using real Bloomberg tickers
  const getCurveConfig = (currency: Currency): CurveConfig => {
    // Use centralized yield curve configurations
    return YIELD_CURVE_CONFIGS[currency] || {
      title: `${currency} Yield Curve`,
      instruments: []
    }
  }

  // Removed old hardcoded configs - now using YIELD_CURVE_CONFIGS

  // Fetch curve data from database endpoint
  const fetchCurveData = async () => {
    console.log('🚀 fetchCurveData called, selectedCurrencies:', selectedCurrencies)
    setLoading(true)
    setError(null)
    
    try {
      const apiUrl = import.meta.env.DEV ? 'http://localhost:8000' : 'http://20.172.249.92:8080'
      const newCurveData = new Map<Currency, CurvePoint[]>()
      
      // Fetch data for each selected currency using curves endpoint
      for (const currency of selectedCurrencies) {
        const response = await fetch(`${apiUrl}/api/curves/${currency}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test'
          }
        })
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        
        const result = await response.json()
        console.log('📊 Curve response for', currency, ':', result)
        
        if (result.success && result.points) {
          console.log(`Raw points for ${currency}:`, result.points.length)
          
          const points: CurvePoint[] = result.points.map((point: any) => ({
            tenor: point.tenor_days,
            years: point.tenor_days / 365.0, // All tenor_days are now in days
            rate: point.rate,
            label: point.tenor,
            ticker: point.ticker,
            instrumentType: 'swap' as const
          })).filter((point: CurvePoint) => point.rate !== null && point.rate !== undefined)
          
          console.log(`Filtered points for ${currency}:`, points.length)
          console.log(`${currency} points:`, points.map(p => `${p.ticker}(${p.label}): ${p.rate}%`))
          
          // Sort by years
          points.sort((a, b) => a.years - b.years)
          newCurveData.set(currency, showInterpolated ? interpolateCurve(points) : points)
        }
      }
      
      console.log('✅ Final curve data:', newCurveData)
      setCurveData(newCurveData)
      setLastUpdate(new Date())
    } catch (err) {
      console.error('❌ Curve data fetch error:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch curve data')
    } finally {
      setLoading(false)
    }
  }

  // Interpolate curve for smooth display
  const interpolateCurve = (points: CurvePoint[]): CurvePoint[] => {
    if (points.length < 2) return points
    
    // Just return the actual points - no interpolation to avoid spikes
    return points
  }

  // Format tenor label
  const formatTenorLabel = (years: number): string => {
    if (years < 0.08) return 'O/N'
    if (years < 0.17) return `${Math.round(years * 12)}M`
    if (years < 1) return `${Math.round(years * 12)}M`
    if (years === Math.floor(years)) return `${years}Y`
    return `${years.toFixed(1)}Y`
  }

  // Draw chart using D3
  const drawChart = () => {
    if (!chartContainerRef.current || curveData.size === 0) return

    // Clear previous chart
    d3.select(chartContainerRef.current).select('svg').remove()

    // Dimensions
    const margin = { top: 30, right: 150, bottom: 60, left: 70 }
    const width = chartContainerRef.current.clientWidth - margin.left - margin.right
    const height = 500 - margin.top - margin.bottom

    // Create SVG
    const svg = d3.select(chartContainerRef.current)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .style('background', currentTheme.background)

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Scales - use custom scale points for realistic yield curve display
    // Map years to x-position with proper compression
    const tenorPositions = [
      { years: 0.003, pos: 0 },     // O/N at start
      { years: 0.083, pos: 0.08 },  // 1M
      { years: 0.25, pos: 0.15 },   // 3M
      { years: 0.5, pos: 0.22 },    // 6M
      { years: 1, pos: 0.3 },       // 1Y
      { years: 2, pos: 0.4 },       // 2Y
      { years: 3, pos: 0.48 },      // 3Y
      { years: 5, pos: 0.58 },      // 5Y
      { years: 10, pos: 0.75 },     // 10Y
      { years: 20, pos: 0.9 },      // 20Y
      { years: 30, pos: 1 }         // 30Y
    ]
    
    // Create appropriate scale based on settings
    const xScale = (() => {
      if (useLogScale) {
        return d3.scaleLog()
          .domain([0.08, zoomRange]) // Start from 1M (0.083Y) for log scale
          .range([0, width])
          .clamp(true)
      } else {
        // Always use linear scale - no more segments
        return d3.scaleLinear()
          .domain([0, zoomRange])
          .range([0, width])
      }
    })()
    
    // Dynamic tick values based on zoom range
    const getTickValues = () => {
      if (useLogScale) {
        // Logarithmic ticks for better short-end visibility
        const ticks = [0.083, 0.25, 0.5, 1, 2, 3, 5, 10]
        if (zoomRange >= 20) ticks.push(20)
        if (zoomRange >= 30) ticks.push(30)
        return ticks.filter(t => t <= zoomRange)
      } else {
        // Linear ticks
        if (zoomRange <= 2) {
          return [0.083, 0.25, 0.5, 1, 1.5, 2].filter(t => t <= zoomRange)
        } else if (zoomRange <= 5) {
          return [0.083, 0.25, 0.5, 1, 2, 3, 4, 5].filter(t => t <= zoomRange)
        } else if (zoomRange <= 10) {
          return [0.25, 0.5, 1, 2, 3, 5, 7, 10].filter(t => t <= zoomRange)
        } else {
          return [0.083, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30].filter(t => t <= zoomRange)
        }
      }
    }

    // Fixed y-scale for proper comparison across currencies
    // Start from -1% to accommodate negative rates (EUR, CHF, JPY)
    const yScale = d3.scaleLinear()
      .domain([-1, 6])  // -1% to 6% covers most yield curves
      .range([height, 0])

    // Add clip path to prevent drawing outside chart area
    svg.append('defs')
      .append('clipPath')
      .attr('id', 'chart-clip')
      .append('rect')
      .attr('x', 0)
      .attr('y', 0)
      .attr('width', width)
      .attr('height', height)
    
    // Background segments removed for cleaner view
    if (false) {
      const segment1 = width / 3
      const segment2 = width / 3
      
      // 0-1Y segment (light blue)
      g.append('rect')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', segment1)
        .attr('height', height)
        .attr('fill', currentTheme.primary)
        .attr('opacity', 0.03)
      
      // 1-5Y segment (medium blue)
      g.append('rect')
        .attr('x', segment1)
        .attr('y', 0)
        .attr('width', segment2)
        .attr('height', height)
        .attr('fill', currentTheme.primary)
        .attr('opacity', 0.06)
      
      // 5-30Y segment (dark blue)
      g.append('rect')
        .attr('x', segment1 + segment2)
        .attr('y', 0)
        .attr('width', width - segment1 - segment2)
        .attr('height', height)
        .attr('fill', currentTheme.primary)
        .attr('opacity', 0.09)
    }
    
    // Add zero line for reference
    g.append('line')
      .attr('x1', 0)
      .attr('x2', width)
      .attr('y1', yScale(0))
      .attr('y2', yScale(0))
      .attr('stroke', currentTheme.border)
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '3,3')
      .style('opacity', 0.5)
    
    // Grid lines
    if (showGrid) {
      // X-axis grid
      const xGridLines = g.append('g')
        .attr('class', 'grid')
        .attr('transform', `translate(0,${height})`)
      
      // Create custom axis generator for three-segment scale
      const gridTickValues = [0.083, 0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30].filter(t => t <= zoomRange)
      
      if (false) {
        // Manual grid lines removed - using standard grid
        gridTickValues.forEach(value => {
          xGridLines.append('line')
            .attr('x1', xScale(value))
            .attr('x2', xScale(value))
            .attr('y1', 0)
            .attr('y2', -height)
            .style('stroke', currentTheme.border)
            .style('stroke-dasharray', '2,2')
            .style('opacity', 0.3)
        })
      } else {
        xGridLines.call(d3.axisBottom(xScale)
          .tickValues(gridTickValues)
          .tickSize(-height)
          .tickFormat(() => '')
        )
      }
      
      xGridLines.selectAll('line')
        .style('stroke', currentTheme.border)
        .style('stroke-dasharray', '2,2')
        .style('opacity', 0.3)
      
      xGridLines.select('.domain').remove()

      // Y-axis grid
      const yGridLines = g.append('g')
        .attr('class', 'grid')
        
      yGridLines.call(d3.axisLeft(yScale)
        .tickSize(-width)
        .tickFormat(() => '')
      )
      
      yGridLines.selectAll('line')
        .style('stroke', currentTheme.border)
        .style('stroke-dasharray', '2,2')
        .style('opacity', 0.3)
        
      yGridLines.select('.domain').remove()
    }

    // X-axis
    const xAxis = g.append('g')
      .attr('transform', `translate(0,${height})`)
    
    if (false) {
      // Manual ticks removed - using standard axis
      const tickValues = getTickValues()
      tickValues.forEach(value => {
        const x = xScale(value)
        xAxis.append('line')
          .attr('x1', x)
          .attr('x2', x)
          .attr('y1', 0)
          .attr('y2', 6)
          .style('stroke', currentTheme.border)
        
        xAxis.append('text')
          .attr('x', x)
          .attr('y', 9)
          .attr('dy', '0.71em')
          .style('text-anchor', 'middle')
          .style('fill', currentTheme.text)
          .style('font-size', '12px')
          .text(formatTenorLabel(value))
      })
      
      // Add axis line
      xAxis.append('line')
        .attr('x1', 0)
        .attr('x2', width)
        .attr('y1', 0)
        .attr('y2', 0)
        .style('stroke', currentTheme.border)
    } else {
      xAxis.call(d3.axisBottom(xScale)
        .tickValues(getTickValues())
        .tickFormat(d => formatTenorLabel(d as number))
      )
    }

    xAxis.selectAll('text')
      .style('fill', currentTheme.text)
      .style('font-size', '12px')

    xAxis.select('.domain')
      .style('stroke', currentTheme.border)

    xAxis.selectAll('.tick line')
      .style('stroke', currentTheme.border)

    // Y-axis
    const yAxis = g.append('g')
      .call(d3.axisLeft(yScale)
        .tickFormat(d => `${(d as number).toFixed(2)}%`)
      )

    yAxis.selectAll('text')
      .style('fill', currentTheme.text)
      .style('font-size', '12px')

    yAxis.select('.domain')
      .style('stroke', currentTheme.border)

    yAxis.selectAll('.tick line')
      .style('stroke', currentTheme.border)

    // Line generator with smooth curve
    const line = d3.line<CurvePoint>()
      .x(d => xScale(d.years))
      .y(d => yScale(d.rate))
      .curve(d3.curveCatmullRom.alpha(0.5))  // Catmull-Rom spline for smooth professional curves

    // Create a group for all chart elements with clipping
    const chartGroup = g.append('g')
      .attr('clip-path', 'url(#chart-clip)')
    
    // Draw lines for each currency
    curveData.forEach((points, currency) => {
      const color = currencyColors[currency]
      
      // Add subtle gradient for professional depth
      const gradientId = `gradient-${currency}-${Date.now()}`
      const gradient = svg.append('defs')
        .append('linearGradient')
        .attr('id', gradientId)
        .attr('x1', '0%')
        .attr('y1', '0%')
        .attr('x2', '0%')
        .attr('y2', '100%')
      
      gradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', color)
        .attr('stop-opacity', 0.15)
      
      gradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', color)
        .attr('stop-opacity', 0)
      
      // Area fill for professional look
      const area = d3.area<CurvePoint>()
        .x(d => xScale(d.years))
        .y0(height)
        .y1(d => yScale(d.rate))
        .curve(d3.curveCatmullRom.alpha(0.5))
      
      chartGroup.append('path')
        .datum(points)
        .attr('fill', `url(#${gradientId})`)
        .attr('d', area)
      
      // Draw the line with enhanced styling
      const path = chartGroup.append('path')
        .datum(points)
        .attr('fill', 'none')
        .attr('stroke', color)
        .attr('stroke-width', 2)
        .attr('d', line)
        .style('filter', 'drop-shadow(0 1px 3px rgba(0,0,0,0.3))')

      // Animate the line drawing
      const totalLength = path.node()?.getTotalLength() || 0
      path
        .attr('stroke-dasharray', totalLength + ' ' + totalLength)
        .attr('stroke-dashoffset', totalLength)
        .transition()
        .duration(1000)
        .ease(d3.easeLinear)
        .attr('stroke-dashoffset', 0)

      // Add points for all actual data
      const dataPoints = points
      console.log(`Rendering ${dataPoints.length} points for ${currency}`)
      
      // Add circles for actual data points - render directly in chartGroup for clipping
      chartGroup.selectAll(`.point-${currency}`)
        .data(dataPoints)
        .enter().append('circle')
        .attr('class', `point-${currency}`)
        .attr('cx', d => xScale(d.years))
        .attr('cy', d => yScale(d.rate))
        .attr('r', 4) // Start with visible radius
        .attr('fill', color)
        .attr('stroke', currentTheme.background)
        .attr('stroke-width', 1)
        .style('cursor', 'pointer')

      // Add hover interactions
      chartGroup.selectAll(`.point-${currency}`)
        .on('mouseover', function(event, d) {
          // Highlight the point
          d3.select(this)
            .transition()
            .duration(100)
            .attr('r', 6)

          // Tooltip
          const tooltip = d3.select('body').append('div')
            .attr('class', 'tooltip')
            .style('position', 'absolute')
            .style('background', currentTheme.surface)
            .style('border', `1px solid ${currentTheme.border}`)
            .style('padding', '10px')
            .style('border-radius', '4px')
            .style('font-size', '12px')
            .style('pointer-events', 'none')
            .style('opacity', 0)
            .style('box-shadow', '0 2px 4px rgba(0,0,0,0.1)')

          tooltip.transition()
            .duration(200)
            .style('opacity', 0.95)

          tooltip.html(`
            <div style="color: ${currentTheme.text}">
              <div style="font-weight: 600; margin-bottom: 4px; color: ${color}">${currency} ${d.label}</div>
              <div>Rate: <strong>${d.rate.toFixed(3)}%</strong></div>
              <div style="font-size: 11px; color: ${currentTheme.textSecondary}; margin-top: 4px">
                ${d.ticker}
              </div>
            </div>
          `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px')
        })
        .on('mouseout', function(event, d) {
          // Reset point size
          d3.select(this)
            .transition()
            .duration(100)
            .attr('r', 4)
            
          // Remove tooltip
          d3.selectAll('.tooltip').remove()
        })
    })

    // Legend
    if (showLegend) {
      const legend = svg.append('g')
        .attr('transform', `translate(${width + margin.left + 20}, ${margin.top})`)

      let yOffset = 0
      curveData.forEach((points, currency) => {
        const color = currencyColors[currency]
        
        const legendItem = legend.append('g')
          .attr('transform', `translate(0, ${yOffset})`)
          .style('cursor', 'pointer')

        // Color rect
        legendItem.append('rect')
          .attr('x', 0)
          .attr('y', 0)
          .attr('width', 14)
          .attr('height', 14)
          .attr('fill', color)
          .attr('rx', 2)

        // Label
        legendItem.append('text')
          .attr('x', 20)
          .attr('y', 11)
          .text(`${currency} OIS Curve`)
          .style('font-size', '13px')
          .style('fill', currentTheme.text)

        // Latest rate
        const latestPoint = points[points.length - 1]
        if (latestPoint && !latestPoint.isInterpolated) {
          legendItem.append('text')
            .attr('x', 20)
            .attr('y', 26)
            .text(`${latestPoint.label}: ${latestPoint.rate.toFixed(2)}%`)
            .style('font-size', '11px')
            .style('fill', currentTheme.textSecondary)
        }

        yOffset += 35
      })
    }

    // Title
    svg.append('text')
      .attr('x', margin.left + width / 2)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', '600')
      .style('fill', currentTheme.text)
      .text('OIS Yield Curves')

    // Axis labels
    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 15)
      .attr('x', 0 - (height / 2 + margin.top))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('fill', currentTheme.text)
      .style('font-size', '14px')
      .text('Yield (%)')

    svg.append('text')
      .attr('transform', `translate(${width / 2 + margin.left}, ${height + margin.top + 45})`)
      .style('text-anchor', 'middle')
      .style('fill', currentTheme.text)
      .style('font-size', '14px')
      .text('Maturity')
  }

  // Effects
  useEffect(() => {
    if (selectedCurrencies.size > 0) {
      fetchCurveData()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCurrencies])

  useEffect(() => {
    drawChart()
  }, [curveData, currentTheme, showGrid, showLegend, zoomRange, useLogScale])

  useEffect(() => {
    const handleResize = () => {
      drawChart()
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [curveData])

  const toggleCurrency = (currency: Currency) => {
    const newSet = new Set(selectedCurrencies)
    if (newSet.has(currency)) {
      newSet.delete(currency)
    } else {
      newSet.add(currency)
    }
    setSelectedCurrencies(newSet)
  }

  return (
    <div style={{
      backgroundColor: currentTheme.surface,
      borderRadius: '8px',
      border: `1px solid ${currentTheme.border}`,
      overflow: 'hidden',
      height: '100%',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header Controls */}
      <div style={{
        borderBottom: `1px solid ${currentTheme.border}`,
        backgroundColor: currentTheme.background,
        padding: '12px 16px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        {/* Currency Selector */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxWidth: '80%' }}>
          {/* G10 Currencies */}
          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '10px', color: currentTheme.textSecondary, marginRight: '8px' }}>G10:</span>
            {availableCurves.filter(c => ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NOK', 'SEK', 'NZD'].includes(c)).map(currency => (
            <button
              key={currency}
              onClick={() => toggleCurrency(currency)}
              style={{
                padding: '2px 6px',
                backgroundColor: selectedCurrencies.has(currency) ? currentTheme.primary : currentTheme.surface,
                color: selectedCurrencies.has(currency) ? currentTheme.background : currentTheme.textSecondary,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '3px',
                cursor: 'pointer',
                fontSize: '9px',
                transition: 'all 0.2s ease',
                marginRight: '4px',
                marginBottom: '4px'
              }}
            >
              {currency}
            </button>
          ))}
          </div>
          
          {/* EM Currencies */}
          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '10px', color: currentTheme.textSecondary, marginRight: '8px' }}>EM:</span>
            {availableCurves.filter(c => !['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NOK', 'SEK', 'NZD'].includes(c)).map(currency => (
            <button
              key={currency}
              onClick={() => toggleCurrency(currency)}
              style={{
                padding: '2px 6px',
                backgroundColor: selectedCurrencies.has(currency) ? currentTheme.primary : currentTheme.surface,
                color: selectedCurrencies.has(currency) ? currentTheme.background : currentTheme.textSecondary,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '3px',
                cursor: 'pointer',
                fontSize: '9px',
                transition: 'all 0.2s ease',
                marginRight: '4px',
                marginBottom: '4px'
              }}
            >
              {currency}
            </button>
          ))}
          </div>
        </div>

        {/* Display Options */}
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showGrid}
              onChange={(e) => setShowGrid(e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            Grid
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showLegend}
              onChange={(e) => setShowLegend(e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            Legend
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showInterpolated}
              onChange={(e) => setShowInterpolated(e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            Smooth
          </label>

          {/* View Mode Controls */}
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ fontSize: '10px', color: currentTheme.textSecondary }}>View:</span>
              {(['2Y', '10Y', 'full'] as const).map(mode => (
                <button
                  key={mode}
                  onClick={() => {
                    setViewMode(mode)
                    setZoomRange(mode === '2Y' ? 2 : mode === '10Y' ? 10 : 30)
                  }}
                  style={{
                    padding: '2px 8px',
                    fontSize: '10px',
                    border: `1px solid ${viewMode === mode ? currentTheme.primary : currentTheme.border}`,
                    borderRadius: '4px',
                    background: viewMode === mode ? currentTheme.primary : 'transparent',
                    color: viewMode === mode ? '#fff' : currentTheme.text,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  {mode === 'full' ? 'Full' : `0-${mode}`}
                </button>
              ))}
            </div>
            
            <label style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={useLogScale}
                onChange={(e) => setUseLogScale(e.target.checked)}
                style={{ cursor: 'pointer' }}
              />
              Log
            </label>
          </div>
          
          <button
            onClick={fetchCurveData}
            disabled={loading || selectedCurrencies.size === 0}
            style={{
              padding: '2px 6px',
              backgroundColor: currentTheme.primary,
              color: currentTheme.background,
              border: `1px solid ${currentTheme.border}`,
              borderRadius: '3px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '9px',
              opacity: loading ? 0.5 : 1
            }}
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Chart Container */}
      <div style={{ flex: 1, padding: '16px' }}>
        <div style={{
          backgroundColor: currentTheme.background,
          padding: '12px',
          borderRadius: '6px',
          border: `1px solid ${currentTheme.border}`,
          height: 'calc(100% - 24px)',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative'
        }}>
          <h3 style={{ 
            fontSize: '13px', 
            fontWeight: '600', 
            margin: '0 0 12px 0',
            color: currentTheme.text
          }}>
            OIS Yield Curves
          </h3>
          
          {loading && (
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              fontSize: '14px',
              color: currentTheme.textSecondary
            }}>
              Loading yield curve data...
            </div>
          )}
          
          {error && (
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              fontSize: '14px',
              color: '#ef4444',
              textAlign: 'center'
            }}>
              Error: {error}
            </div>
          )}
          
          {!loading && !error && selectedCurrencies.size === 0 && (
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              fontSize: '14px',
              color: currentTheme.textSecondary,
              textAlign: 'center'
            }}>
              Select one or more currencies to display yield curves
            </div>
          )}
          
          <div ref={chartContainerRef} style={{ width: '100%', flex: 1 }} />
        </div>
      </div>

      {/* Status Bar */}
      <div style={{
        borderTop: `1px solid ${currentTheme.border}`,
        padding: '8px 16px',
        fontSize: '12px',
        color: currentTheme.textSecondary,
        display: 'flex',
        justifyContent: 'space-between'
      }}>
        <span>
          {curveData.size > 0 && `Showing ${Array.from(curveData.values()).flat().filter(p => !p.isInterpolated).length} market points across ${curveData.size} curves`}
        </span>
        <span>
          {lastUpdate && `Last update: ${lastUpdate.toLocaleTimeString()}`}
        </span>
      </div>
    </div>
  )
}