import { useState, useEffect, useRef, useCallback } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import * as d3 from 'd3'
import { Currency, FXPair } from '../constants/currencies'
import { YIELD_CURVE_CONFIGS, getYieldCurveConfig } from '../data/yieldCurveConfigs'

type CurveType = 'yield' | 'forward'
type ForwardDisplayMode = 'outright' | 'points'
type CurrencyPair = FXPair

interface CurvePoint {
  tenor: number // Days to maturity
  rate: number  // Rate in %
  label: string // Display label
  ticker?: string // Bloomberg ticker
  years: number // Years to maturity for proper scaling
}

interface CurveInstrument {
  ticker: string
  tenor: number
  label: string
  years: number
  instrumentType: 'money_market' | 'swap' | 'bond'
  order?: number
}

interface YieldCurveConfig {
  title: string
  instruments: CurveInstrument[]
}

export function RateCurvesTab() {
  const { currentTheme } = useTheme()
  const chartContainerRef = useRef<HTMLDivElement>(null)
  
  // Controls
  const [curveType, setCurveType] = useState<CurveType>('yield')
  const [selectedCurrencies, setSelectedCurrencies] = useState<Set<Currency>>(new Set(['USD']))
  const [selectedCurrencyPairs, setSelectedCurrencyPairs] = useState<Set<CurrencyPair>>(new Set(['EURUSD']))
  const [selectedDate, setSelectedDate] = useState<string>('2025-07-24')
  
  // Data
  const [curvePointsByCurrency, setCurvePointsByCurrency] = useState<Map<Currency | CurrencyPair, CurvePoint[]>>(new Map())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Store configurations fetched from database
  const [yieldCurveConfigs, setYieldCurveConfigs] = useState<Map<Currency, YieldCurveConfig>>(new Map())
  const [configsLoading, setConfigsLoading] = useState(true)

  // Modern color scheme for different currencies and pairs
  const currencyColors: { [key in Currency | CurrencyPair]?: string } = {
    // Single currencies for yield curves
    USD: currentTheme.primary || '#7A9E65',  // Green
    EUR: '#4ECDC4',  // Teal
    GBP: '#F39C12',  // Orange
    JPY: '#E74C3C',  // Red
    CHF: '#9B59B6',  // Purple
    AUD: '#3498DB',  // Blue
    CAD: '#E91E63',  // Pink
    NZD: '#00BCD4',   // Cyan
    // Currency pairs for forward curves
    EURUSD: '#4ECDC4',  // Teal
    GBPUSD: '#F39C12',  // Orange
    USDJPY: '#E74C3C',  // Red
    USDCHF: '#9B59B6',  // Purple
    AUDUSD: '#3498DB',  // Blue
    USDCAD: '#E91E63',  // Pink
    NZDUSD: '#00BCD4',  // Cyan
    EURGBP: '#2ECC71',  // Green
    EURJPY: '#1ABC9C',  // Turquoise
    GBPJPY: '#D35400'   // Dark Orange
  }

  // Fetch yield curve configurations from database
  const fetchYieldCurveConfigs = async () => {
    setConfigsLoading(true)
    try {
      // Get unique currencies to fetch
      const currenciesToFetch = Array.from(selectedCurrencies)
      if (currenciesToFetch.length === 0) return
      
      const response = await fetch('http://localhost:8000/api/yield-curves/batch-config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(currenciesToFetch)
      })
      
      if (!response.ok) {
        throw new Error(`Failed to fetch curve configs: ${response.status}`)
      }
      
      const data = await response.json()
      const newConfigs = new Map<Currency, YieldCurveConfig>()
      
      if (data.success && data.curves) {
        Object.entries(data.curves).forEach(([currency, curveData]: [string, any]) => {
          if (curveData.success && curveData.instruments?.length > 0) {
            newConfigs.set(currency as Currency, {
              title: curveData.title,
              instruments: curveData.instruments
            })
          }
        })
      }
      
      setYieldCurveConfigs(newConfigs)
    } catch (error) {
      console.error('Failed to fetch yield curve configs:', error)
      // Don't set error - we'll use fallback configs
      // setError('Failed to load curve configurations')
    } finally {
      setConfigsLoading(false)
    }
  }
  
  // Fetch configs when currencies change
  useEffect(() => {
    if (curveType === 'yield' && selectedCurrencies.size > 0) {
      fetchYieldCurveConfigs()
    }
  }, [selectedCurrencies, curveType])

  // Curve configuration based on type and currency/pair
  const getCurveConfig = (currencyOrPair: Currency | CurrencyPair) => {
    if (curveType === 'yield') {
      const currency = currencyOrPair as Currency
      
      // First check if we have a database configuration
      const dbConfig = yieldCurveConfigs.get(currency)
      if (dbConfig && dbConfig.instruments.length > 0) {
        return dbConfig
      }
      
      // NO FALLBACK - if database fails, show error
      console.error(`No database data available for ${currency}`)
      return null
    } else {
      // FX Forward curves (OTC) - NOT futures! Using forward points to calculate outright rates
      // TODO: Review FX forward curve implementation:
      // 1. Verify all Bloomberg tickers are correct for each currency pair
      // 2. Consider fetching outright forward rates directly if available
      // 3. Add error handling for missing data points
      // 4. Verify pip divisor calculations for all pairs
      const pair = currencyOrPair as CurrencyPair
      const configs: { [key in CurrencyPair]?: any } = {
        EURUSD: {
          title: 'EURUSD OTC Forward Rates',
          instruments: [
            { ticker: 'EURUSD Curncy', tenor: 0, label: 'Spot', years: 0 },
            { ticker: 'EURUSD1W Curncy', tenor: 7, label: '1W', years: 7/365 },
            { ticker: 'EUR1M Curncy', tenor: 30, label: '1M', years: 30/365 },
            { ticker: 'EUR2M Curncy', tenor: 60, label: '2M', years: 60/365 },
            { ticker: 'EUR3M Curncy', tenor: 90, label: '3M', years: 90/365 },
            { ticker: 'EUR6M Curncy', tenor: 180, label: '6M', years: 180/365 },
            { ticker: 'EUR9M Curncy', tenor: 270, label: '9M', years: 270/365 },
            { ticker: 'EURUSD12M Curncy', tenor: 365, label: '1Y', years: 1 },
            { ticker: 'EURUSD18M Curncy', tenor: 540, label: '18M', years: 540/365 },
            { ticker: 'EURUSD2Y Curncy', tenor: 730, label: '2Y', years: 2 }
          ],
          pipDivisor: 10000
        },
        GBPUSD: {
          title: 'GBPUSD OTC Forward Rates',
          instruments: [
            { ticker: 'GBPUSD Curncy', tenor: 0, label: 'Spot', years: 0 },
            { ticker: 'GBP1W Curncy', tenor: 7, label: '1W', years: 7/365 },
            { ticker: 'GBP1M Curncy', tenor: 30, label: '1M', years: 30/365 },
            { ticker: 'GBP3M Curncy', tenor: 90, label: '3M', years: 90/365 },
            { ticker: 'GBP6M Curncy', tenor: 180, label: '6M', years: 180/365 },
            { ticker: 'GBP12M Curncy', tenor: 365, label: '1Y', years: 1 },
            { ticker: 'GBP2Y Curncy', tenor: 730, label: '2Y', years: 2 }
          ],
          pipDivisor: 10000
        },
        USDJPY: {
          title: 'USDJPY OTC Forward Rates',
          instruments: [
            { ticker: 'USDJPY Curncy', tenor: 0, label: 'Spot', years: 0 },
            { ticker: 'JPY1W Curncy', tenor: 7, label: '1W', years: 7/365 },
            { ticker: 'JPY1M Curncy', tenor: 30, label: '1M', years: 30/365 },
            { ticker: 'JPY3M Curncy', tenor: 90, label: '3M', years: 90/365 },
            { ticker: 'JPY6M Curncy', tenor: 180, label: '6M', years: 180/365 },
            { ticker: 'JPY12M Curncy', tenor: 365, label: '1Y', years: 1 },
            { ticker: 'JPY2Y Curncy', tenor: 730, label: '2Y', years: 2 }
          ],
          pipDivisor: 100
        },
        USDCHF: {
          title: 'USDCHF OTC Forward Rates',
          instruments: [
            { ticker: 'USDCHF Curncy', tenor: 0, label: 'Spot', years: 0 },
            { ticker: 'CHF1W Curncy', tenor: 7, label: '1W', years: 7/365 },
            { ticker: 'CHF1M Curncy', tenor: 30, label: '1M', years: 30/365 },
            { ticker: 'CHF3M Curncy', tenor: 90, label: '3M', years: 90/365 },
            { ticker: 'CHF6M Curncy', tenor: 180, label: '6M', years: 180/365 },
            { ticker: 'CHF12M Curncy', tenor: 365, label: '1Y', years: 1 },
            { ticker: 'CHF2Y Curncy', tenor: 730, label: '2Y', years: 2 }
          ],
          pipDivisor: 10000
        },
        AUDUSD: {
          title: 'AUDUSD OTC Forward Rates',
          instruments: [
            { ticker: 'AUDUSD Curncy', tenor: 0, label: 'Spot', years: 0 },
            { ticker: 'AUD1W Curncy', tenor: 7, label: '1W', years: 7/365 },
            { ticker: 'AUD1M Curncy', tenor: 30, label: '1M', years: 30/365 },
            { ticker: 'AUD3M Curncy', tenor: 90, label: '3M', years: 90/365 },
            { ticker: 'AUD6M Curncy', tenor: 180, label: '6M', years: 180/365 },
            { ticker: 'AUD12M Curncy', tenor: 365, label: '1Y', years: 1 },
            { ticker: 'AUD2Y Curncy', tenor: 730, label: '2Y', years: 2 }
          ],
          pipDivisor: 10000
        },
        USDCAD: {
          title: 'USDCAD OTC Forward Rates',
          instruments: [
            { ticker: 'USDCAD Curncy', tenor: 0, label: 'Spot', years: 0 },
            { ticker: 'CAD1W Curncy', tenor: 7, label: '1W', years: 7/365 },
            { ticker: 'CAD1M Curncy', tenor: 30, label: '1M', years: 30/365 },
            { ticker: 'CAD3M Curncy', tenor: 90, label: '3M', years: 90/365 },
            { ticker: 'CAD6M Curncy', tenor: 180, label: '6M', years: 180/365 },
            { ticker: 'CAD12M Curncy', tenor: 365, label: '1Y', years: 1 },
            { ticker: 'CAD2Y Curncy', tenor: 730, label: '2Y', years: 2 }
          ],
          pipDivisor: 10000
        },
        NZDUSD: {
          title: 'NZDUSD OTC Forward Rates',
          instruments: [
            { ticker: 'NZDUSD Curncy', tenor: 0, label: 'Spot', years: 0 },
            { ticker: 'NZD1W Curncy', tenor: 7, label: '1W', years: 7/365 },
            { ticker: 'NZD1M Curncy', tenor: 30, label: '1M', years: 30/365 },
            { ticker: 'NZD3M Curncy', tenor: 90, label: '3M', years: 90/365 },
            { ticker: 'NZD6M Curncy', tenor: 180, label: '6M', years: 180/365 },
            { ticker: 'NZD12M Curncy', tenor: 365, label: '1Y', years: 1 },
            { ticker: 'NZD2Y Curncy', tenor: 730, label: '2Y', years: 2 }
          ],
          pipDivisor: 10000
        },
        EURGBP: {
          title: 'EURGBP OTC Forward Rates',
          instruments: [
            { ticker: 'EURGBP Curncy', tenor: 0, label: 'Spot', years: 0 },
            { ticker: 'EURGBP1M Curncy', tenor: 30, label: '1M', years: 30/365 },
            { ticker: 'EURGBP3M Curncy', tenor: 90, label: '3M', years: 90/365 },
            { ticker: 'EURGBP6M Curncy', tenor: 180, label: '6M', years: 180/365 },
            { ticker: 'EURGBP12M Curncy', tenor: 365, label: '1Y', years: 1 },
            { ticker: 'EURGBP2Y Curncy', tenor: 730, label: '2Y', years: 2 }
          ],
          pipDivisor: 10000
        },
        EURJPY: {
          title: 'EURJPY OTC Forward Rates',
          instruments: [
            { ticker: 'EURJPY Curncy', tenor: 0, label: 'Spot', years: 0 },
            { ticker: 'EURJPY1M Curncy', tenor: 30, label: '1M', years: 30/365 },
            { ticker: 'EURJPY3M Curncy', tenor: 90, label: '3M', years: 90/365 },
            { ticker: 'EURJPY6M Curncy', tenor: 180, label: '6M', years: 180/365 },
            { ticker: 'EURJPY12M Curncy', tenor: 365, label: '1Y', years: 1 },
            { ticker: 'EURJPY2Y Curncy', tenor: 730, label: '2Y', years: 2 }
          ],
          pipDivisor: 100
        },
        GBPJPY: {
          title: 'GBPJPY OTC Forward Rates',
          instruments: [
            { ticker: 'GBPJPY Curncy', tenor: 0, label: 'Spot', years: 0 },
            { ticker: 'GBPJPY1M Curncy', tenor: 30, label: '1M', years: 30/365 },
            { ticker: 'GBPJPY3M Curncy', tenor: 90, label: '3M', years: 90/365 },
            { ticker: 'GBPJPY6M Curncy', tenor: 180, label: '6M', years: 180/365 },
            { ticker: 'GBPJPY12M Curncy', tenor: 365, label: '1Y', years: 1 },
            { ticker: 'GBPJPY2Y Curncy', tenor: 730, label: '2Y', years: 2 }
          ],
          pipDivisor: 100
        }
      }
      return configs[pair] || configs.EURUSD
    }
  }

  // Fetch curve data from Bloomberg API
  const fetchCurveData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const newCurveData = new Map<Currency | CurrencyPair, CurvePoint[]>()
      
      // Handle yield curves
      if (curveType === 'yield') {
        for (const currency of selectedCurrencies) {
          const config = getCurveConfig(currency)
        const tickers = config.instruments.map(inst => inst.ticker)
        
        const response = await fetch('http://localhost:8000/api/bloomberg/reference', {
          method: 'POST',
          headers: {
            'Authorization': 'Bearer test',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            securities: tickers,
            fields: ['PX_LAST', 'PX_BID', 'PX_ASK']
          })
        })
        
        if (!response.ok) {
          throw new Error(`Bloomberg API error: ${response.status}`)
        }
        
        const data = await response.json()
        
        if (data.success && data.data) {
          const points: CurvePoint[] = []
          const securities = data.data.securities_data
          
          securities?.forEach((item: any, index: number) => {
            const instrument = config.instruments[index]
            if (!instrument) return
            
            if (item.success && item.fields?.PX_LAST) {
              const value = item.fields.PX_LAST
              
              // Yield curve - use values as-is and include years for proper scaling
              points.push({
                tenor: instrument.tenor,
                rate: value,
                label: instrument.label,
                ticker: instrument.ticker,
                years: instrument.years
              })
            }
          })
          
          points.sort((a, b) => a.tenor - b.tenor)
          newCurveData.set(currency, points)
        }
      }
      } else {
        // Handle forward curves
        for (const pair of selectedCurrencyPairs) {
          const config = getCurveConfig(pair)
          const tickers = config.instruments.map(inst => inst.ticker)
          
          const response = await fetch('http://localhost:8000/api/bloomberg/reference', {
            method: 'POST',
            headers: {
              'Authorization': 'Bearer test',
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              securities: tickers,
              fields: ['PX_LAST', 'PX_BID', 'PX_ASK']
            })
          })
          
          if (!response.ok) {
            throw new Error(`Bloomberg API error: ${response.status}`)
          }
          
          const data = await response.json()
          
          if (data.success && data.data) {
            const points: CurvePoint[] = []
            const securities = data.data.securities_data
            
            // For FX forwards, we need to calculate outright rates from spot + forward points
            let spotRate: number | null = null
            
            securities?.forEach((item: any, index: number) => {
              const instrument = config.instruments[index]
              if (!instrument) return
              
              if (item.success && item.fields?.PX_LAST) {
                const value = item.fields.PX_LAST
                
                if (instrument.tenor === 0) {
                  // This is the spot rate
                  spotRate = value
                  points.push({
                    tenor: instrument.tenor,
                    rate: value,
                    label: instrument.label,
                    ticker: instrument.ticker,
                    years: instrument.years
                  })
                } else if (spotRate !== null) {
                  // Calculate outright forward rate from spot + forward points
                  const forwardRate = spotRate + (value / config.pipDivisor)
                  points.push({
                    tenor: instrument.tenor,
                    rate: forwardRate,
                    label: instrument.label,
                    ticker: instrument.ticker,
                    years: instrument.years
                  })
                }
              }
            })
            
            points.sort((a, b) => a.tenor - b.tenor)
            newCurveData.set(pair, points)
          }
        }
      }
      
      setCurvePointsByCurrency(newCurveData)
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to fetch curve data')
    } finally {
      setLoading(false)
    }
  }

  // D3.js chart rendering
  const drawChart = useCallback(() => {
    if (!chartContainerRef.current || curvePointsByCurrency.size === 0) return

    // Clear previous chart
    d3.select(chartContainerRef.current).selectAll("*").remove()

    const margin = { top: 20, right: 80, bottom: 50, left: 60 }
    const width = chartContainerRef.current.clientWidth - margin.left - margin.right
    const height = chartContainerRef.current.clientHeight - margin.top - margin.bottom

    if (width <= 0 || height <= 0) return

    const svg = d3.select(chartContainerRef.current)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`)

    // Get all unique tenors and rates for scales
    const allTenors = new Set<number>()
    const allRates: number[] = []
    const tenorToLabel = new Map<number, string>()

    curvePointsByCurrency.forEach(points => {
      points.forEach(point => {
        allTenors.add(point.tenor)
        allRates.push(point.rate)
        tenorToLabel.set(point.tenor, point.label)
      })
    })

    const sortedTenors = Array.from(allTenors).sort((a, b) => a - b)

    // Convert tenor days to years for realistic time scale
    const tenorToYears = (days: number): number => days / 365

    // Create a linear scale based on years for realistic time spacing
    const xScale = d3.scaleLinear()
      .domain([0, tenorToYears(sortedTenors[sortedTenors.length - 1])])
      .range([0, width])

    // Y scale for rates
    const yScale = d3.scaleLinear()
      .domain([
        Math.min(...allRates) - 0.2,
        Math.max(...allRates) + 0.2
      ])
      .range([height, 0])

    // Grid lines
    g.selectAll(".grid-line-y")
      .data(yScale.ticks(5))
      .enter()
      .append("line")
      .attr("class", "grid-line-y")
      .attr("x1", 0)
      .attr("x2", width)
      .attr("y1", d => yScale(d))
      .attr("y2", d => yScale(d))
      .attr("stroke", currentTheme.border)
      .attr("stroke-width", 0.5)
      .attr("stroke-dasharray", "3,3")
      .attr("opacity", 0.3)

    // X-axis with custom tick formatter
    // Set specific tick values at actual tenor positions
    const tickValues = sortedTenors.map(tenor => tenorToYears(tenor))
    
    const xAxis = d3.axisBottom(xScale)
      .tickValues(tickValues)
      .tickFormat((d, i) => {
        const tenor = sortedTenors[i]
        return tenorToLabel.get(tenor) || ''
      })

    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(xAxis)
      .style("color", currentTheme.textSecondary)

    // Y-axis
    g.append("g")
      .call(d3.axisLeft(yScale).tickFormat(d => curveType === 'yield' ? `${d}%` : d.toFixed(4)))
      .style("color", currentTheme.textSecondary)

    // Line generator
    const line = d3.line<CurvePoint>()
      .x(d => xScale(tenorToYears(d.tenor)))
      .y(d => yScale(d.rate))
      .curve(d3.curveCatmullRom.alpha(0.5))

    // Enhanced tooltip
    let tooltipDiv = d3.select("body").select(".rate-tooltip")
    if (tooltipDiv.empty()) {
      tooltipDiv = d3.select("body").append("div")
        .attr("class", "rate-tooltip")
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

    // Draw curves
    curvePointsByCurrency.forEach((points, currencyOrPair) => {
      const color = currencyColors[currencyOrPair] || currentTheme.primary

      // Line
      g.append("path")
        .datum(points)
        .attr("fill", "none")
        .attr("stroke", color)
        .attr("stroke-width", 1.5)
        .attr("stroke-linejoin", "round")
        .attr("stroke-linecap", "round")
        .attr("d", line)
        .style("filter", "drop-shadow(0 1px 2px rgba(0,0,0,0.15))")

      // Invisible overlay for mouse interaction
      g.append("path")
        .datum(points)
        .attr("fill", "none")
        .attr("stroke", "transparent")
        .attr("stroke-width", 20)
        .attr("d", line)
        .style("cursor", "crosshair")
        .on("mousemove", function(event) {
          const [mouseX] = d3.pointer(event)
          const yearValue = xScale.invert(mouseX)
          
          // Find closest point by year value
          let closestPoint = points[0]
          let minDist = Math.abs(tenorToYears(closestPoint.tenor) - yearValue)
          
          points.forEach(p => {
            const dist = Math.abs(tenorToYears(p.tenor) - yearValue)
            if (dist < minDist) {
              minDist = dist
              closestPoint = p
            }
          })
          
          tooltipDiv.transition()
            .duration(50)
            .style("opacity", .95)
          
          const formatValue = curveType === 'yield' 
            ? `${closestPoint.rate.toFixed(3)}%`
            : closestPoint.rate.toFixed(5)
          
          const labelText = curveType === 'yield' ? 'Rate:' : 'FX Rate:'
          
          tooltipDiv.html(`
            <div style="font-weight: 600; margin-bottom: 6px; color: ${color}">
              ${currencyOrPair} - ${closestPoint.label}
            </div>
            <div style="display: flex; justify-content: space-between; gap: 20px;">
              <span style="color: ${currentTheme.textSecondary}">${labelText}</span>
              <span style="font-weight: 500">${formatValue}</span>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 20px; margin-top: 4px; padding-top: 4px; border-top: 1px solid ${currentTheme.border}">
              <span style="color: ${currentTheme.textSecondary}; font-size: 10px">Ticker:</span>
              <span style="font-size: 10px; font-family: monospace; color: ${currentTheme.primary}">${closestPoint.ticker || 'N/A'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; gap: 20px; margin-top: 2px;">
              <span style="color: ${currentTheme.textSecondary}; font-size: 10px">Maturity:</span>
              <span style="font-size: 10px">${closestPoint.tenor} days</span>
            </div>
          `)
            .style("left", (event.pageX + 15) + "px")
            .style("top", (event.pageY - 40) + "px")
        })
        .on("mouseout", function() {
          tooltipDiv.transition()
            .duration(200)
            .style("opacity", 0)
        })
    })

    // Axis labels
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - (height / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .style("fill", currentTheme.textSecondary)
      .text(curveType === 'yield' ? 'Yield (%)' : 'FX Forward Rate')

  }, [curvePointsByCurrency, currentTheme, currencyColors, curveType])

  // Initial data fetch
  useEffect(() => {
    fetchCurveData()
  }, [curveType, selectedCurrencies, selectedCurrencyPairs])

  // Redraw chart when data or theme changes
  useEffect(() => {
    drawChart()
  }, [drawChart])

  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      drawChart()
    }
    
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [drawChart])

  return (
    <div style={{ 
      backgroundColor: currentTheme.surface,
      borderRadius: '8px',
      border: `1px solid ${currentTheme.border}`,
      height: '100%',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header */}
      <div style={{
        padding: '16px',
        borderBottom: `1px solid ${currentTheme.border}`,
        backgroundColor: currentTheme.surface
      }}>
        <h3 style={{ 
          margin: 0, 
          fontSize: '16px', 
          fontWeight: '600',
          color: currentTheme.text 
        }}>
          {curveType === 'yield' ? 'Yield Curves' : 'Forward Rate Curves'}
        </h3>
      </div>

      {/* Main Content Area */}
      <div style={{ 
        flex: 1, 
        display: 'flex', 
        gap: '16px',
        padding: '16px',
        overflow: 'hidden'
      }}>
        {/* Chart Container */}
        <div style={{ 
          flex: 1, 
          position: 'relative',
          minHeight: '400px'
        }}>
          <div 
            ref={chartContainerRef}
            style={{
              width: '100%',
              height: '100%',
              backgroundColor: currentTheme.background,
              borderRadius: '6px',
              border: `1px solid ${currentTheme.border}`
            }}
          />
          {loading && (
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: currentTheme.background + 'dd',
              borderRadius: '6px'
            }}>
              <div style={{ color: currentTheme.textSecondary }}>
                Loading rate curves...
              </div>
            </div>
          )}
          {configsLoading && (
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: currentTheme.background + 'dd',
              borderRadius: '6px'
            }}>
              <div style={{ color: currentTheme.textSecondary }}>
                Loading curve configurations...
              </div>
            </div>
          )}
          {error && (
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              color: '#e74c3c',
              textAlign: 'center'
            }}>
              {error}
            </div>
          )}
        </div>

        {/* Controls Panel - Right Side */}
        <div style={{
          width: '280px',
          backgroundColor: currentTheme.background,
          padding: '16px',
          borderRadius: '6px',
          border: `1px solid ${currentTheme.border}`,
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          overflowY: 'auto'
        }}>
          {/* Curve Type Selector */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '12px', fontWeight: '600', color: currentTheme.textSecondary }}>
              Curve Type
            </label>
            <select
              value={curveType}
              onChange={(e) => setCurveType(e.target.value as CurveType)}
              style={{
                backgroundColor: currentTheme.background,
                color: currentTheme.text,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '4px',
                padding: '8px 12px',
                fontSize: '12px'
              }}
            >
              <option value="yield">Yield Curve</option>
              <option value="forward">FX Forwards (OTC)</option>
            </select>
          </div>

          {/* Currency/Pair Multi-Selector */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '12px', fontWeight: '600', color: currentTheme.textSecondary }}>
              {curveType === 'yield' ? `Currencies (${selectedCurrencies.size} selected)` : `Currency Pairs (${selectedCurrencyPairs.size} selected)`}
            </label>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '4px'
            }}>
              {curveType === 'yield' ? (
                // Show currencies for yield curves
                (['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD'] as Currency[]).map(curr => (
                <label key={curr} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 10px',
                  cursor: 'pointer',
                  fontSize: '12px',
                  backgroundColor: selectedCurrencies.has(curr) ? currentTheme.primary + '20' : currentTheme.surface,
                  border: `1px solid ${selectedCurrencies.has(curr) ? currentTheme.primary : currentTheme.border}`,
                  borderRadius: '6px',
                  transition: 'all 0.2s ease'
                }}>
                  <input
                    type="checkbox"
                    checked={selectedCurrencies.has(curr)}
                    onChange={(e) => {
                      const newCurrencies = new Set(selectedCurrencies)
                      if (e.target.checked) {
                        newCurrencies.add(curr)
                      } else {
                        newCurrencies.delete(curr)
                      }
                      if (newCurrencies.size > 0) {
                        setSelectedCurrencies(newCurrencies)
                      }
                    }}
                    style={{ display: 'none' }}
                  />
                  <div style={{
                    width: '12px',
                    height: '2px',
                    backgroundColor: selectedCurrencies.has(curr) ? currencyColors[curr] : currentTheme.border,
                    transition: 'all 0.2s ease'
                  }} />
                  <span style={{ 
                    color: selectedCurrencies.has(curr) ? currentTheme.primary : currentTheme.text,
                    fontWeight: selectedCurrencies.has(curr) ? '600' : '400'
                  }}>
                    {curr}
                  </span>
                </label>
              ))
              ) : (
                // Show currency pairs for forward curves
                (['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD', 'EURGBP', 'EURJPY', 'GBPJPY'] as CurrencyPair[]).map(pair => (
                  <label key={pair} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px 10px',
                    cursor: 'pointer',
                    fontSize: '11px',
                    backgroundColor: selectedCurrencyPairs.has(pair) ? currentTheme.primary + '20' : currentTheme.surface,
                    border: `1px solid ${selectedCurrencyPairs.has(pair) ? currentTheme.primary : currentTheme.border}`,
                    borderRadius: '6px',
                    transition: 'all 0.2s ease'
                  }}>
                    <input
                      type="checkbox"
                      checked={selectedCurrencyPairs.has(pair)}
                      onChange={(e) => {
                        const newPairs = new Set(selectedCurrencyPairs)
                        if (e.target.checked) {
                          newPairs.add(pair)
                        } else {
                          newPairs.delete(pair)
                        }
                        if (newPairs.size > 0) {
                          setSelectedCurrencyPairs(newPairs)
                        }
                      }}
                      style={{ display: 'none' }}
                    />
                    <div style={{
                      width: '12px',
                      height: '2px',
                      backgroundColor: selectedCurrencyPairs.has(pair) ? currencyColors[pair] : currentTheme.border,
                      transition: 'all 0.2s ease'
                    }} />
                    <span style={{ 
                      color: selectedCurrencyPairs.has(pair) ? currentTheme.primary : currentTheme.text,
                      fontWeight: selectedCurrencyPairs.has(pair) ? '600' : '400'
                    }}>
                      {pair}
                    </span>
                  </label>
                ))
              )}
            </div>
          </div>

          {/* Currency/Pair Legend */}
          {((curveType === 'yield' && selectedCurrencies.size > 0) || (curveType === 'forward' && selectedCurrencyPairs.size > 0)) && (
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              gap: '4px',
              marginTop: 'auto'
            }}>
              <label style={{ fontSize: '11px', fontWeight: '600', color: currentTheme.textSecondary }}>
                Active Curves
              </label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                {curveType === 'yield' ? (
                  Array.from(selectedCurrencies).map(currency => (
                    <div key={currency} style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '8px',
                      fontSize: '11px'
                    }}>
                      <div style={{
                        width: '12px',
                        height: '2px',
                        backgroundColor: currencyColors[currency],
                        borderRadius: '1px'
                      }} />
                      <span style={{ color: currentTheme.text }}>{currency}</span>
                    </div>
                  ))
                ) : (
                  Array.from(selectedCurrencyPairs).map(pair => (
                    <div key={pair} style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '8px',
                      fontSize: '11px'
                    }}>
                      <div style={{
                        width: '12px',
                        height: '2px',
                        backgroundColor: currencyColors[pair],
                        borderRadius: '1px'
                      }} />
                      <span style={{ color: currentTheme.text }}>{pair}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}