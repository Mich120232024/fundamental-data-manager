import { useState, useEffect, useRef } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import * as d3 from 'd3'
import { FXPair } from '../constants/currencies'

type CurrencyPair = FXPair
type DisplayMode = 'outright' | 'points' | 'implied_yield'

interface ForwardPoint {
  tenor: number     // Days to maturity
  years: number     // Years to maturity for proper scaling
  spot: number      // Spot rate
  forward: number   // Forward rate
  points: number    // Forward points (pips)
  impliedYield: number // Implied yield differential
  label: string     // Display label
  ticker: string    // Bloomberg ticker
  isInterpolated?: boolean
}

interface ForwardCurveConfig {
  title: string
  spotTicker: string
  forwardTickers: Array<{
    ticker: string
    tenor: number
    label: string
    years: number
  }>
}

export function FXForwardCurvesTab() {
  const { currentTheme } = useTheme()
  const chartContainerRef = useRef<HTMLDivElement>(null)
  
  // Controls
  const [selectedPairs, setSelectedPairs] = useState<Set<CurrencyPair>>(new Set(['EURUSD', 'GBPUSD']))
  const [displayMode, setDisplayMode] = useState<DisplayMode>('points')
  const [showGrid, setShowGrid] = useState(true)
  const [showLegend, setShowLegend] = useState(true)
  const [expandedSelector, setExpandedSelector] = useState(false)
  
  // Data
  const [forwardData, setForwardData] = useState<Map<CurrencyPair, ForwardPoint[]>>(new Map())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  // Professional color palette for currency pairs
  const getPairColor = (pair: CurrencyPair): string => {
    const colors: Partial<Record<CurrencyPair, string>> = {
      // Major G10 pairs
      EURUSD: '#1976D2',  // Blue
      GBPUSD: '#D32F2F',  // Red
      USDJPY: '#7B1FA2',  // Purple
      USDCHF: '#F57C00',  // Orange
      AUDUSD: '#388E3C',  // Green
      USDCAD: '#E91E63',  // Pink
      NZDUSD: '#00ACC1',  // Cyan
      USDSEK: '#FDD835',  // Yellow
      USDNOK: '#6A4C93',  // Indigo
      // Major EM pairs
      USDMXN: '#8D6E63',  // Brown
      USDZAR: '#546E7A',  // Blue Grey
      USDTRY: '#B71C1C',  // Dark Red
      USDBRL: '#1B5E20',  // Dark Green
      USDCNH: '#FF6F00',  // Amber
      USDINR: '#4527A0',  // Deep Purple
      USDKRW: '#0277BD',  // Light Blue
      USDTWD: '#00695C',  // Teal
      USDSGD: '#AD1457',  // Deep Pink
      USDHKD: '#BF360C',  // Deep Orange
      USDTHB: '#1A237E',  // Indigo
      // Middle East
      USDILS: '#006064',  // Dark Cyan
      // Asia
      USDPHP: '#F57F17',  // Yellow
      // Europe
      USDPLN: '#311B92',  // Deep Purple
      USDCZK: '#880E4F',  // Pink
      USDHUF: '#01579B',  // Blue
      USDDKK: '#BF360C',  // Orange
      USDRUB: '#B71C1C',  // Red
      // Precious Metals
      XAUUSD: '#FFD700',  // Gold
      XAGUSD: '#C0C0C0',  // Silver
      // EUR crosses
      EURGBP: '#5D4037',  // Brown
      EURJPY: '#FBC02D',  // Yellow
      EURCHF: '#0277BD',  // Light Blue
      EURAUD: '#2E7D32',  // Forest Green
      EURCAD: '#AD1457',  // Deep Pink
      EURNZD: '#00838F',  // Dark Cyan
      EURSEK: '#FF6F00',  // Amber
      EURNOK: '#4527A0',  // Purple
      // GBP crosses
      GBPJPY: '#455A64',  // Blue Grey
      GBPCHF: '#6A1B9A',  // Purple
      GBPAUD: '#43A047',  // Light Green
      GBPCAD: '#E91E63',  // Pink
      GBPNZD: '#00ACC1',  // Cyan
      GBPSEK: '#FDD835',  // Yellow
      GBPNOK: '#6A4C93',  // Indigo
      // JPY crosses
      AUDJPY: '#EF6C00',  // Amber
      CADJPY: '#C62828',  // Dark Red
      NZDJPY: '#00695C',  // Teal
      CHFJPY: '#5E35B1',  // Deep Purple
      // Other crosses
      AUDCAD: '#388E3C',  // Green
      AUDCHF: '#F57C00',  // Orange
      AUDNZD: '#00897B',  // Teal
      NZDCAD: '#E91E63',  // Pink
      NZDCHF: '#F57C00',  // Orange
      CADCHF: '#7B1FA2',  // Purple
      NOKJPY: '#6A4C93',  // Indigo
      SEKJPY: '#FDD835',  // Yellow
      ZARJPY: '#546E7A',  // Blue Grey
      MXNJPY: '#8D6E63',  // Brown
      TRYJPY: '#B71C1C'   // Dark Red
    }
    
    return colors[pair] || '#757575'  // Default grey if not defined
  }

  // Forward curve configurations
  const getForwardConfig = (pair: CurrencyPair): ForwardCurveConfig => {
    const configs: Partial<Record<CurrencyPair, ForwardCurveConfig>> = {
      EURUSD: {
        title: 'EUR/USD Forward Curve',
        spotTicker: 'EURUSD Curncy',
        forwardTickers: [
          { ticker: 'EURUSD1W Curncy', tenor: 7, label: '1W', years: 0.019 },
          { ticker: 'EURUSD2W Curncy', tenor: 14, label: '2W', years: 0.038 },
          { ticker: 'EURUSD1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'EURUSD2M Curncy', tenor: 60, label: '2M', years: 0.167 },
          { ticker: 'EURUSD3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'EURUSD6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'EURUSD9M Curncy', tenor: 270, label: '9M', years: 0.75 },
          { ticker: 'EURUSD1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'EURUSD18M Curncy', tenor: 548, label: '18M', years: 1.5 },
          { ticker: 'EURUSD2Y Curncy', tenor: 730, label: '2Y', years: 2 },
          { ticker: 'EURUSD3Y Curncy', tenor: 1095, label: '3Y', years: 3 },
          { ticker: 'EURUSD4Y Curncy', tenor: 1460, label: '4Y', years: 4 },
          { ticker: 'EURUSD5Y Curncy', tenor: 1825, label: '5Y', years: 5 }
        ]
      },
      GBPUSD: {
        title: 'GBP/USD Forward Curve',
        spotTicker: 'GBPUSD Curncy',
        forwardTickers: [
          { ticker: 'GBPUSD1W Curncy', tenor: 7, label: '1W', years: 0.019 },
          { ticker: 'GBPUSD2W Curncy', tenor: 14, label: '2W', years: 0.038 },
          { ticker: 'GBPUSD1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'GBPUSD2M Curncy', tenor: 60, label: '2M', years: 0.167 },
          { ticker: 'GBPUSD3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'GBPUSD6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'GBPUSD9M Curncy', tenor: 270, label: '9M', years: 0.75 },
          { ticker: 'GBPUSD1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'GBPUSD18M Curncy', tenor: 548, label: '18M', years: 1.5 },
          { ticker: 'GBPUSD2Y Curncy', tenor: 730, label: '2Y', years: 2 },
          { ticker: 'GBPUSD3Y Curncy', tenor: 1095, label: '3Y', years: 3 },
          { ticker: 'GBPUSD5Y Curncy', tenor: 1825, label: '5Y', years: 5 }
        ]
      },
      USDJPY: {
        title: 'USD/JPY Forward Curve',
        spotTicker: 'USDJPY Curncy',
        forwardTickers: [
          { ticker: 'USDJPY1W Curncy', tenor: 7, label: '1W', years: 0.019 },
          { ticker: 'USDJPY2W Curncy', tenor: 14, label: '2W', years: 0.038 },
          { ticker: 'USDJPY1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'USDJPY2M Curncy', tenor: 60, label: '2M', years: 0.167 },
          { ticker: 'USDJPY3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'USDJPY6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'USDJPY9M Curncy', tenor: 270, label: '9M', years: 0.75 },
          { ticker: 'USDJPY1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'USDJPY18M Curncy', tenor: 548, label: '18M', years: 1.5 },
          { ticker: 'USDJPY2Y Curncy', tenor: 730, label: '2Y', years: 2 },
          { ticker: 'USDJPY3Y Curncy', tenor: 1095, label: '3Y', years: 3 },
          { ticker: 'USDJPY5Y Curncy', tenor: 1825, label: '5Y', years: 5 }
        ]
      },
      USDCHF: {
        title: 'USD/CHF Forward Curve',
        spotTicker: 'USDCHF Curncy',
        forwardTickers: [
          { ticker: 'USDCHF1W Curncy', tenor: 7, label: '1W', years: 0.019 },
          { ticker: 'USDCHF1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'USDCHF2M Curncy', tenor: 60, label: '2M', years: 0.167 },
          { ticker: 'USDCHF3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'USDCHF6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'USDCHF9M Curncy', tenor: 270, label: '9M', years: 0.75 },
          { ticker: 'USDCHF1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'USDCHF2Y Curncy', tenor: 730, label: '2Y', years: 2 },
          { ticker: 'USDCHF3Y Curncy', tenor: 1095, label: '3Y', years: 3 },
          { ticker: 'USDCHF5Y Curncy', tenor: 1825, label: '5Y', years: 5 }
        ]
      },
      AUDUSD: {
        title: 'AUD/USD Forward Curve',
        spotTicker: 'AUDUSD Curncy',
        forwardTickers: [
          { ticker: 'AUDUSD1W Curncy', tenor: 7, label: '1W', years: 0.019 },
          { ticker: 'AUDUSD1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'AUDUSD2M Curncy', tenor: 60, label: '2M', years: 0.167 },
          { ticker: 'AUDUSD3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'AUDUSD6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'AUDUSD9M Curncy', tenor: 270, label: '9M', years: 0.75 },
          { ticker: 'AUDUSD1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'AUDUSD2Y Curncy', tenor: 730, label: '2Y', years: 2 },
          { ticker: 'AUDUSD3Y Curncy', tenor: 1095, label: '3Y', years: 3 },
          { ticker: 'AUDUSD5Y Curncy', tenor: 1825, label: '5Y', years: 5 }
        ]
      },
      USDCAD: {
        title: 'USD/CAD Forward Curve',
        spotTicker: 'USDCAD Curncy',
        forwardTickers: [
          { ticker: 'USDCAD1W Curncy', tenor: 7, label: '1W', years: 0.019 },
          { ticker: 'USDCAD1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'USDCAD2M Curncy', tenor: 60, label: '2M', years: 0.167 },
          { ticker: 'USDCAD3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'USDCAD6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'USDCAD9M Curncy', tenor: 270, label: '9M', years: 0.75 },
          { ticker: 'USDCAD1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'USDCAD2Y Curncy', tenor: 730, label: '2Y', years: 2 },
          { ticker: 'USDCAD3Y Curncy', tenor: 1095, label: '3Y', years: 3 },
          { ticker: 'USDCAD5Y Curncy', tenor: 1825, label: '5Y', years: 5 }
        ]
      },
      NZDUSD: {
        title: 'NZD/USD Forward Curve',
        spotTicker: 'NZDUSD Curncy',
        forwardTickers: [
          { ticker: 'NZDUSD1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'NZDUSD3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'NZDUSD6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'NZDUSD1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'NZDUSD2Y Curncy', tenor: 730, label: '2Y', years: 2 }
        ]
      },
      EURGBP: {
        title: 'EUR/GBP Forward Curve',
        spotTicker: 'EURGBP Curncy',
        forwardTickers: [
          { ticker: 'EURGBP1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'EURGBP3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'EURGBP6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'EURGBP1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'EURGBP2Y Curncy', tenor: 730, label: '2Y', years: 2 }
        ]
      },
      EURJPY: {
        title: 'EUR/JPY Forward Curve',
        spotTicker: 'EURJPY Curncy',
        forwardTickers: [
          { ticker: 'EURJPY1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'EURJPY3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'EURJPY6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'EURJPY1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'EURJPY2Y Curncy', tenor: 730, label: '2Y', years: 2 }
        ]
      },
      GBPJPY: {
        title: 'GBP/JPY Forward Curve',
        spotTicker: 'GBPJPY Curncy',
        forwardTickers: [
          { ticker: 'GBPJPY1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'GBPJPY3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'GBPJPY6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'GBPJPY1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'GBPJPY2Y Curncy', tenor: 730, label: '2Y', years: 2 }
        ]
      },
      // Emerging Market pairs
      USDMXN: {
        title: 'USD/MXN Forward Curve',
        spotTicker: 'USDMXN Curncy',
        forwardTickers: [
          { ticker: 'USDMXN1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'USDMXN3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'USDMXN6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'USDMXN1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'USDMXN2Y Curncy', tenor: 730, label: '2Y', years: 2 }
        ]
      },
      USDZAR: {
        title: 'USD/ZAR Forward Curve',
        spotTicker: 'USDZAR Curncy',
        forwardTickers: [
          { ticker: 'USDZAR1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'USDZAR3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'USDZAR6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'USDZAR1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'USDZAR2Y Curncy', tenor: 730, label: '2Y', years: 2 }
        ]
      },
      USDTRY: {
        title: 'USD/TRY Forward Curve',
        spotTicker: 'USDTRY Curncy',
        forwardTickers: [
          { ticker: 'USDTRY1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'USDTRY3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'USDTRY6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'USDTRY1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'USDTRY2Y Curncy', tenor: 730, label: '2Y', years: 2 }
        ]
      },
      USDBRL: {
        title: 'USD/BRL Forward Curve',
        spotTicker: 'USDBRL Curncy',
        forwardTickers: [
          { ticker: 'USDBRL1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'USDBRL3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'USDBRL6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'USDBRL1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'USDBRL2Y Curncy', tenor: 730, label: '2Y', years: 2 }
        ]
      },
      // EUR crosses
      EURCHF: {
        title: 'EUR/CHF Forward Curve',
        spotTicker: 'EURCHF Curncy',
        forwardTickers: [
          { ticker: 'EURCHF1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'EURCHF3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'EURCHF6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'EURCHF1Y Curncy', tenor: 365, label: '1Y', years: 1 },
          { ticker: 'EURCHF2Y Curncy', tenor: 730, label: '2Y', years: 2 }
        ]
      },
      EURAUD: {
        title: 'EUR/AUD Forward Curve',
        spotTicker: 'EURAUD Curncy',
        forwardTickers: [
          { ticker: 'EURAUD1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'EURAUD3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'EURAUD6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'EURAUD1Y Curncy', tenor: 365, label: '1Y', years: 1 }
        ]
      },
      EURCAD: {
        title: 'EUR/CAD Forward Curve',
        spotTicker: 'EURCAD Curncy',
        forwardTickers: [
          { ticker: 'EURCAD1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'EURCAD3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'EURCAD6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'EURCAD1Y Curncy', tenor: 365, label: '1Y', years: 1 }
        ]
      },
      EURNZD: {
        title: 'EUR/NZD Forward Curve',
        spotTicker: 'EURNZD Curncy',
        forwardTickers: [
          { ticker: 'EURNZD1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'EURNZD3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'EURNZD6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'EURNZD1Y Curncy', tenor: 365, label: '1Y', years: 1 }
        ]
      },
      // GBP crosses
      GBPCHF: {
        title: 'GBP/CHF Forward Curve',
        spotTicker: 'GBPCHF Curncy',
        forwardTickers: [
          { ticker: 'GBPCHF1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'GBPCHF3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'GBPCHF6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'GBPCHF1Y Curncy', tenor: 365, label: '1Y', years: 1 }
        ]
      },
      GBPAUD: {
        title: 'GBP/AUD Forward Curve',
        spotTicker: 'GBPAUD Curncy',
        forwardTickers: [
          { ticker: 'GBPAUD1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'GBPAUD3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'GBPAUD6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'GBPAUD1Y Curncy', tenor: 365, label: '1Y', years: 1 }
        ]
      },
      // JPY crosses
      AUDJPY: {
        title: 'AUD/JPY Forward Curve',
        spotTicker: 'AUDJPY Curncy',
        forwardTickers: [
          { ticker: 'AUDJPY1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'AUDJPY3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'AUDJPY6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'AUDJPY1Y Curncy', tenor: 365, label: '1Y', years: 1 }
        ]
      },
      CADJPY: {
        title: 'CAD/JPY Forward Curve',
        spotTicker: 'CADJPY Curncy',
        forwardTickers: [
          { ticker: 'CADJPY1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'CADJPY3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'CADJPY6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'CADJPY1Y Curncy', tenor: 365, label: '1Y', years: 1 }
        ]
      },
      NZDJPY: {
        title: 'NZD/JPY Forward Curve',
        spotTicker: 'NZDJPY Curncy',
        forwardTickers: [
          { ticker: 'NZDJPY1M Curncy', tenor: 30, label: '1M', years: 0.083 },
          { ticker: 'NZDJPY3M Curncy', tenor: 90, label: '3M', years: 0.25 },
          { ticker: 'NZDJPY6M Curncy', tenor: 180, label: '6M', years: 0.5 },
          { ticker: 'NZDJPY1Y Curncy', tenor: 365, label: '1Y', years: 1 }
        ]
      }
    }
    
    // For pairs not explicitly configured, generate standard config
    if (!configs[pair]) {
      const standardTenors = [
        { ticker: `${pair}1M Curncy`, tenor: 30, label: '1M', years: 0.083 },
        { ticker: `${pair}3M Curncy`, tenor: 90, label: '3M', years: 0.25 },
        { ticker: `${pair}6M Curncy`, tenor: 180, label: '6M', years: 0.5 },
        { ticker: `${pair}1Y Curncy`, tenor: 365, label: '1Y', years: 1 }
      ]
      
      return {
        title: `${pair} Forward Curve`,
        spotTicker: `${pair} Curncy`,
        forwardTickers: standardTenors
      }
    }
    
    return configs[pair]
  }

  // Fetch forward data from Bloomberg
  const fetchForwardData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const apiUrl = import.meta.env.DEV ? 'http://localhost:8000' : 'http://20.172.249.92:8080'
      const newForwardData = new Map<CurrencyPair, ForwardPoint[]>()
      
      // Fetch data for each selected pair
      for (const pair of selectedPairs) {
        const config = getForwardConfig(pair)
        const allTickers = [config.spotTicker, ...config.forwardTickers.map(f => f.ticker)]
        
        const response = await fetch(`${apiUrl}/api/bloomberg/reference`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test'
          },
          body: JSON.stringify({
            securities: allTickers,
            fields: ['PX_LAST', 'PX_BID', 'PX_ASK']
          })
        })
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        
        const result = await response.json()
        
        if (result.data?.securities_data) {
          const points: ForwardPoint[] = []
          let spotRate = 0
          
          // Get spot rate first
          if (result.data.securities_data[0]?.success) {
            spotRate = result.data.securities_data[0].fields?.PX_LAST || 0
          }
          
          // Process forward points
          config.forwardTickers.forEach((fwdConfig, index) => {
            const dataIndex = index + 1 // Skip spot at index 0
            if (dataIndex < result.data.securities_data.length && 
                result.data.securities_data[dataIndex]?.success) {
              const forward = result.data.securities_data[dataIndex].fields?.PX_LAST
              
              if (forward !== null && forward !== undefined && spotRate > 0) {
                // Bloomberg forward tickers return forward POINTS directly, not outright rates
                const forwardPoints = forward // This IS the forward points value
                
                // Calculate outright forward rate from spot + points
                const forwardRate = pair.includes('JPY') 
                  ? spotRate + (forwardPoints / 100)    // JPY pairs: points are in hundredths
                  : spotRate + (forwardPoints / 10000)  // Major pairs: points are in ten-thousandths
                
                // Calculate implied yield differential
                const impliedYield = ((forwardRate / spotRate) - 1) * (365 / fwdConfig.tenor) * 100
                
                points.push({
                  tenor: fwdConfig.tenor,
                  years: fwdConfig.years,
                  spot: spotRate,
                  forward: forwardRate,     // Use calculated outright rate
                  points: forwardPoints,    // Use direct points from Bloomberg
                  impliedYield: impliedYield,
                  label: fwdConfig.label,
                  ticker: fwdConfig.ticker
                })
              }
            }
          })
          
          // Sort by years
          points.sort((a, b) => a.years - b.years)
          
          // Add spot point at the beginning
          if (spotRate > 0) {
            points.unshift({
              tenor: 0,
              years: 0,
              spot: spotRate,
              forward: spotRate,
              points: 0,
              impliedYield: 0,
              label: 'Spot',
              ticker: config.spotTicker
            })
          }
          
          newForwardData.set(pair, points)
        }
      }
      
      setForwardData(newForwardData)
      setLastUpdate(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch forward data')
      console.error('Forward data fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  // Draw chart using D3
  const drawChart = () => {
    if (!chartContainerRef.current || forwardData.size === 0) return

    // Clear previous chart
    d3.select(chartContainerRef.current).select('svg').remove()

    // Dimensions
    const margin = { top: 30, right: 150, bottom: 60, left: 80 }
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

    // Scales
    const xScale = d3.scaleLinear()
      .domain([0, 5])  // 0 to 5 years
      .range([0, width])
      .nice()

    // Y scale depends on display mode
    let yScale: d3.ScaleLinear<number, number>
    let yAxisLabel: string
    let yFormat: (d: number) => string
    
    if (displayMode === 'outright') {
      // Forward rates
      const allForwards = Array.from(forwardData.values()).flat().map(d => d.forward)
      const yMin = Math.min(...allForwards) * 0.995
      const yMax = Math.max(...allForwards) * 1.005
      
      yScale = d3.scaleLinear()
        .domain([yMin, yMax])
        .range([height, 0])
        .nice()
      
      yAxisLabel = 'Forward Rate'
      yFormat = (d: number) => d.toFixed(4)
    } else if (displayMode === 'points') {
      // Forward points
      const allPoints = Array.from(forwardData.values()).flat().map(d => d.points)
      const yMin = Math.min(...allPoints, -50)
      const yMax = Math.max(...allPoints, 50)
      
      yScale = d3.scaleLinear()
        .domain([yMin, yMax])
        .range([height, 0])
        .nice()
      
      yAxisLabel = 'Forward Points (pips)'
      yFormat = (d: number) => d.toFixed(0)
    } else {
      // Implied yield differential
      const allYields = Array.from(forwardData.values()).flat().map(d => d.impliedYield)
      const yMin = Math.min(...allYields) - 0.5
      const yMax = Math.max(...allYields) + 0.5
      
      yScale = d3.scaleLinear()
        .domain([yMin, yMax])
        .range([height, 0])
        .nice()
      
      yAxisLabel = 'Implied Yield Differential (%)'
      yFormat = (d: number) => `${d.toFixed(2)}%`
    }

    // Grid lines
    if (showGrid) {
      // X-axis grid
      const xGridLines = g.append('g')
        .attr('class', 'grid')
        .attr('transform', `translate(0,${height})`)
        
      xGridLines.call(d3.axisBottom(xScale)
        .tickSize(-height)
        .tickFormat(() => '')
      )
      
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

    // Add zero line for points/yield modes
    if (displayMode !== 'outright') {
      g.append('line')
        .attr('x1', 0)
        .attr('x2', width)
        .attr('y1', yScale(0))
        .attr('y2', yScale(0))
        .style('stroke', currentTheme.textSecondary)
        .style('stroke-width', 1)
        .style('opacity', 0.5)
    }

    // X-axis
    const xAxis = g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale)
        .tickFormat(d => d === 0 ? 'Spot' : `${d}Y`)
      )

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
        .tickFormat(d => yFormat(d as number))
      )

    yAxis.selectAll('text')
      .style('fill', currentTheme.text)
      .style('font-size', '12px')

    yAxis.select('.domain')
      .style('stroke', currentTheme.border)

    yAxis.selectAll('.tick line')
      .style('stroke', currentTheme.border)

    // Line generator
    const line = d3.line<ForwardPoint>()
      .x(d => xScale(d.years))
      .y(d => {
        if (displayMode === 'outright') return yScale(d.forward)
        if (displayMode === 'points') return yScale(d.points)
        return yScale(d.impliedYield)
      })
      .curve(d3.curveMonotoneX)

    // Draw lines for each currency pair
    forwardData.forEach((points, pair) => {
      const color = getPairColor(pair)
      
      // Draw the line
      const path = g.append('path')
        .datum(points)
        .attr('fill', 'none')
        .attr('stroke', color)
        .attr('stroke-width', 2.5)
        .attr('d', line)
        .style('opacity', 0.9)

      // Animate the line drawing
      const totalLength = path.node()?.getTotalLength() || 0
      path
        .attr('stroke-dasharray', totalLength + ' ' + totalLength)
        .attr('stroke-dashoffset', totalLength)
        .transition()
        .duration(1000)
        .ease(d3.easeLinear)
        .attr('stroke-dashoffset', 0)

      // Add points for actual data
      g.selectAll(`.point-${pair.replace('/', '')}`)
        .data(points)
        .enter().append('circle')
        .attr('class', `point-${pair.replace('/', '')}`)
        .attr('cx', d => xScale(d.years))
        .attr('cy', d => {
          if (displayMode === 'outright') return yScale(d.forward)
          if (displayMode === 'points') return yScale(d.points)
          return yScale(d.impliedYield)
        })
        .attr('r', 0)
        .attr('fill', color)
        .style('cursor', 'pointer')
        .transition()
        .delay((_d, i) => 1000 + i * 50)
        .duration(200)
        .attr('r', 4)

      // Add hover interactions
      g.selectAll<SVGCircleElement, ForwardPoint>(`.point-${pair.replace('/', '')}`)
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

          const tooltipContent = `
            <div style="color: ${currentTheme.text}">
              <div style="font-weight: 600; margin-bottom: 6px; color: ${color}">${pair} ${d.label}</div>
              <div>Spot: <strong>${d.spot.toFixed(4)}</strong></div>
              <div>Forward: <strong>${d.forward.toFixed(4)}</strong></div>
              <div>Points: <strong>${d.points.toFixed(1)} pips</strong></div>
              <div>Implied Yield Diff: <strong>${d.impliedYield.toFixed(2)}%</strong></div>
              <div style="font-size: 11px; color: ${currentTheme.textSecondary}; margin-top: 4px">
                ${d.ticker}
              </div>
            </div>
          `

          tooltip.html(tooltipContent)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px')
        })
        .on('mouseout', function() {
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
      forwardData.forEach((points, pair) => {
        const color = getPairColor(pair)
        
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
          .text(pair)
          .style('font-size', '13px')
          .style('fill', currentTheme.text)
          .style('font-weight', '600')

        // Latest value
        const latestPoint = points[points.length - 1]
        if (latestPoint) {
          let valueText = ''
          if (displayMode === 'outright') {
            valueText = `${latestPoint.label}: ${latestPoint.forward.toFixed(4)}`
          } else if (displayMode === 'points') {
            valueText = `${latestPoint.label}: ${latestPoint.points.toFixed(0)} pips`
          } else {
            valueText = `${latestPoint.label}: ${latestPoint.impliedYield.toFixed(2)}%`
          }
          
          legendItem.append('text')
            .attr('x', 20)
            .attr('y', 26)
            .text(valueText)
            .style('font-size', '11px')
            .style('fill', currentTheme.textSecondary)
        }

        yOffset += 35
      })
    }

    // Title
    const titleText = displayMode === 'outright' ? 'FX Forward Rates' 
                    : displayMode === 'points' ? 'FX Forward Points'
                    : 'Implied Yield Differentials'
    
    svg.append('text')
      .attr('x', margin.left + width / 2)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', '600')
      .style('fill', currentTheme.text)
      .text(titleText)

    // Axis labels
    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 20)
      .attr('x', 0 - (height / 2 + margin.top))
      .attr('dy', '1em')
      .style('text-anchor', 'middle')
      .style('fill', currentTheme.text)
      .style('font-size', '14px')
      .text(yAxisLabel)

    svg.append('text')
      .attr('transform', `translate(${width / 2 + margin.left}, ${height + margin.top + 45})`)
      .style('text-anchor', 'middle')
      .style('fill', currentTheme.text)
      .style('font-size', '14px')
      .text('Maturity')
  }

  // Effects
  useEffect(() => {
    if (selectedPairs.size > 0) {
      fetchForwardData()
    }
  }, [selectedPairs])

  useEffect(() => {
    drawChart()
  }, [forwardData, currentTheme, showGrid, showLegend, displayMode])

  useEffect(() => {
    const handleResize = () => {
      drawChart()
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [forwardData, displayMode])

  const togglePair = (pair: CurrencyPair) => {
    const newSet = new Set(selectedPairs)
    if (newSet.has(pair)) {
      newSet.delete(pair)
    } else {
      newSet.add(pair)
    }
    setSelectedPairs(newSet)
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
        {/* Display Mode Selector */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {(['points', 'outright', 'implied_yield'] as DisplayMode[]).map(mode => (
            <button
              key={mode}
              onClick={() => setDisplayMode(mode)}
              style={{
                padding: '2px 6px',
                backgroundColor: displayMode === mode ? currentTheme.primary : currentTheme.surface,
                color: displayMode === mode ? currentTheme.background : currentTheme.textSecondary,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '3px',
                cursor: 'pointer',
                fontSize: '9px',
                transition: 'all 0.2s ease'
              }}
            >
              {mode === 'points' ? 'Points' : mode === 'outright' ? 'Outright' : 'Implied Yield'}
            </button>
          ))}
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
          
          <button
            onClick={fetchForwardData}
            disabled={loading || selectedPairs.size === 0}
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

      {/* Currency Pair Selector - Collapsible */}
      <div style={{
        borderBottom: `1px solid ${currentTheme.border}`,
        backgroundColor: currentTheme.background,
      }}>
        {/* Header with selected pairs and toggle */}
        <div style={{
          padding: '12px 16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
          userSelect: 'none'
        }}
        onClick={() => setExpandedSelector(!expandedSelector)}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '13px', fontWeight: '600', color: currentTheme.text }}>Currency Pairs</span>
            <span style={{ fontSize: '11px', color: currentTheme.textSecondary }}>
              ({selectedPairs.size} selected)
            </span>
            {/* Show selected pairs when collapsed */}
            {!expandedSelector && selectedPairs.size > 0 && (
              <div style={{ display: 'flex', gap: '4px', marginLeft: '8px' }}>
                {Array.from(selectedPairs).slice(0, 5).map(pair => (
                  <span key={pair} style={{
                    padding: '1px 4px',
                    backgroundColor: currentTheme.primary,
                    color: currentTheme.background,
                    borderRadius: '3px',
                    fontSize: '9px'
                  }}>
                    {pair}
                  </span>
                ))}
                {selectedPairs.size > 5 && (
                  <span style={{ fontSize: '9px', color: currentTheme.textSecondary }}>+{selectedPairs.size - 5} more</span>
                )}
              </div>
            )}
          </div>
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            style={{
              transform: expandedSelector ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: 'transform 0.2s ease',
              fill: currentTheme.textSecondary
            }}
          >
            <path d="M8 10.5l-4-4h8l-4 4z"/>
          </svg>
        </div>
        
        {/* Expandable content */}
        <div style={{
          maxHeight: expandedSelector ? '400px' : '0',
          overflow: 'hidden',
          transition: 'max-height 0.3s ease',
          padding: expandedSelector ? '0 16px 16px' : '0 16px',
        }}>
          {/* Quick selection buttons */}
          <div style={{ marginBottom: '8px', display: 'flex', gap: '6px' }}>
            <button
              onClick={() => {
                const majors = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD'] as CurrencyPair[]
                setSelectedPairs(new Set(majors))
              }}
              style={{
                padding: '2px 8px',
                backgroundColor: currentTheme.surface,
                color: currentTheme.text,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '3px',
                cursor: 'pointer',
                fontSize: '10px'
              }}
            >
              Select G10 Majors
            </button>
            <button
              onClick={() => {
                const em = ['USDMXN', 'USDZAR', 'USDTRY', 'USDBRL', 'USDCNH'] as CurrencyPair[]
                setSelectedPairs(new Set(em))
              }}
              style={{
                padding: '2px 8px',
                backgroundColor: currentTheme.surface,
                color: currentTheme.text,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '3px',
                cursor: 'pointer',
                fontSize: '10px'
              }}
            >
              Select Major EM
            </button>
            <button
              onClick={() => setSelectedPairs(new Set())}
              style={{
                padding: '2px 8px',
                backgroundColor: currentTheme.surface,
                color: currentTheme.text,
                border: `1px solid ${currentTheme.border}`,
                borderRadius: '3px',
                cursor: 'pointer',
                fontSize: '10px'
              }}
            >
              Clear All
            </button>
          </div>
          
          <div style={{ marginBottom: '8px' }}>
            <span style={{ fontSize: '11px', fontWeight: '600', color: currentTheme.text }}>G10 USD Pairs:</span>
            <div style={{ display: 'flex', gap: '6px', marginTop: '4px', flexWrap: 'wrap' }}>
              {(['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD', 'USDSEK', 'USDNOK'] as CurrencyPair[]).map(pair => (
              <button
                key={pair}
                onClick={() => togglePair(pair)}
                style={{
                  padding: '2px 6px',
                  backgroundColor: selectedPairs.has(pair) ? currentTheme.primary : currentTheme.surface,
                  color: selectedPairs.has(pair) ? currentTheme.background : currentTheme.textSecondary,
                  border: `1px solid ${currentTheme.border}`,
                  borderRadius: '3px',
                  cursor: 'pointer',
                  fontSize: '9px',
                  transition: 'all 0.2s ease'
                }}
              >
                {pair}
              </button>
            ))}
          </div>
        </div>
        
        <div style={{ marginBottom: '8px' }}>
          <span style={{ fontSize: '11px', fontWeight: '600', color: currentTheme.text }}>EM USD Pairs - Major:</span>
          <div style={{ display: 'flex', gap: '6px', marginTop: '4px', flexWrap: 'wrap' }}>
            {(['USDMXN', 'USDZAR', 'USDTRY', 'USDBRL', 'USDCNH', 'USDINR', 'USDKRW', 'USDTWD'] as CurrencyPair[]).map(pair => (
              <button
                key={pair}
                onClick={() => togglePair(pair)}
                style={{
                  padding: '2px 6px',
                  backgroundColor: selectedPairs.has(pair) ? currentTheme.primary : currentTheme.surface,
                  color: selectedPairs.has(pair) ? currentTheme.background : currentTheme.textSecondary,
                  border: `1px solid ${currentTheme.border}`,
                  borderRadius: '3px',
                  cursor: 'pointer',
                  fontSize: '9px',
                  transition: 'all 0.2s ease'
                }}
              >
                {pair}
              </button>
            ))}
          </div>
        </div>
        
        <div style={{ marginBottom: '8px' }}>
          <span style={{ fontSize: '11px', fontWeight: '600', color: currentTheme.text }}>EUR Crosses:</span>
          <div style={{ display: 'flex', gap: '6px', marginTop: '4px', flexWrap: 'wrap' }}>
            {(['EURGBP', 'EURJPY', 'EURCHF', 'EURAUD', 'EURCAD', 'EURNZD'] as CurrencyPair[]).map(pair => (
              <button
                key={pair}
                onClick={() => togglePair(pair)}
                style={{
                  padding: '2px 6px',
                  backgroundColor: selectedPairs.has(pair) ? currentTheme.primary : currentTheme.surface,
                  color: selectedPairs.has(pair) ? currentTheme.background : currentTheme.textSecondary,
                  border: `1px solid ${currentTheme.border}`,
                  borderRadius: '3px',
                  cursor: 'pointer',
                  fontSize: '9px',
                  transition: 'all 0.2s ease'
                }}
              >
                {pair}
              </button>
            ))}
          </div>
        </div>
        
        <div style={{ marginBottom: '8px' }}>
          <span style={{ fontSize: '11px', fontWeight: '600', color: currentTheme.text }}>EM USD Pairs - Other:</span>
          <div style={{ display: 'flex', gap: '6px', marginTop: '4px', flexWrap: 'wrap' }}>
            {(['USDSGD', 'USDHKD', 'USDTHB', 'USDILS', 'USDPLN', 'USDCZK', 'USDHUF', 
               'USDRUB', 'USDPHP', 'USDDKK'] as CurrencyPair[]).map(pair => (
              <button
                key={pair}
                onClick={() => togglePair(pair)}
                style={{
                  padding: '2px 6px',
                  backgroundColor: selectedPairs.has(pair) ? currentTheme.primary : currentTheme.surface,
                  color: selectedPairs.has(pair) ? currentTheme.background : currentTheme.textSecondary,
                  border: `1px solid ${currentTheme.border}`,
                  borderRadius: '3px',
                  cursor: 'pointer',
                  fontSize: '9px',
                  transition: 'all 0.2s ease'
                }}
              >
                {pair}
              </button>
            ))}
          </div>
        </div>
        
        <div style={{ marginBottom: '8px' }}>
          <span style={{ fontSize: '11px', fontWeight: '600', color: currentTheme.text }}>Precious Metals:</span>
          <div style={{ display: 'flex', gap: '6px', marginTop: '4px', flexWrap: 'wrap' }}>
            {(['XAUUSD', 'XAGUSD'] as CurrencyPair[]).map(pair => (
              <button
                key={pair}
                onClick={() => togglePair(pair)}
                style={{
                  padding: '2px 6px',
                  backgroundColor: selectedPairs.has(pair) ? currentTheme.primary : currentTheme.surface,
                  color: selectedPairs.has(pair) ? currentTheme.background : currentTheme.textSecondary,
                  border: `1px solid ${currentTheme.border}`,
                  borderRadius: '3px',
                  cursor: 'pointer',
                  fontSize: '9px',
                  transition: 'all 0.2s ease'
                }}
              >
                {pair === 'XAUUSD' ? 'XAUUSD (Gold)' : 'XAGUSD (Silver)'}
              </button>
            ))}
          </div>
        </div>
        
          <div>
            <span style={{ fontSize: '11px', fontWeight: '600', color: currentTheme.text }}>Other Crosses:</span>
            <div style={{ display: 'flex', gap: '6px', marginTop: '4px', flexWrap: 'wrap' }}>
              {(['GBPJPY', 'GBPCHF', 'GBPAUD', 'GBPCAD', 'GBPNZD', 'AUDJPY', 'CADJPY', 'NZDJPY', 'CHFJPY'] as CurrencyPair[]).map(pair => (
                <button
                  key={pair}
                  onClick={() => togglePair(pair)}
                  style={{
                    padding: '2px 6px',
                    backgroundColor: selectedPairs.has(pair) ? currentTheme.primary : currentTheme.surface,
                    color: selectedPairs.has(pair) ? currentTheme.background : currentTheme.textSecondary,
                    border: `1px solid ${currentTheme.border}`,
                    borderRadius: '3px',
                    cursor: 'pointer',
                    fontSize: '9px',
                    transition: 'all 0.2s ease'
                  }}
                >
                  {pair}
                </button>
              ))}
            </div>
          </div>
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
            FX Forward Curves - {displayMode === 'points' ? 'Forward Points' : displayMode === 'outright' ? 'Outright Rates' : 'Implied Yield Differential'}
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
              Loading forward curve data...
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
          
          {!loading && !error && selectedPairs.size === 0 && (
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              fontSize: '14px',
              color: currentTheme.textSecondary,
              textAlign: 'center'
            }}>
              Select one or more currency pairs to display forward curves
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
          {forwardData.size > 0 && `Showing ${Array.from(forwardData.values()).flat().length} forward points across ${forwardData.size} pairs`}
        </span>
        <span>
          {lastUpdate && `Last update: ${lastUpdate.toLocaleTimeString()}`}
        </span>
      </div>
    </div>
  )
}