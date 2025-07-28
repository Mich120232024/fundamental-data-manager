export interface AgentState {
  lastAnalysis: {
    timestamp: Date
    regime: MarketRegime
    observations: string[]
    confidence: number
  } | null
  marketRegime: MarketRegime
  positions: Position[]
  performance: PerformanceRecord[]
  learnings: Learning[]
}

export type MarketRegime = 'COMPRESSED' | 'LOW_VOL' | 'NORMAL' | 'STRESSED' | 'CRISIS' | 'UNKNOWN'

export interface Position {
  id: string
  currencyPair: string
  strategy: string
  entryDate: Date
  entryVol: number
  targetVol: number
  stopVol: number
  status: 'OPEN' | 'CLOSED'
  pnl?: number
}

export interface PerformanceRecord {
  date: Date
  action: string
  outcome: 'SUCCESS' | 'FAILURE' | 'PARTIAL'
  details: string
}

export interface Learning {
  timestamp: Date
  observation: string
  actionTaken: string
  result: string
  lessonLearned: string
}

export interface AgentDecision {
  action: 'FETCH_VOLATILITY' | 'ANALYZE_REGIME' | 'RECOMMEND_POSITION' | 'UPDATE_POSITIONS' | 'WAIT'
  reasoning: string
  confidence: number
  params: Record<string, any>
}

export interface VolatilityData {
  currencyPair: string
  tenor: string
  atmVol: number
  rr25d: number
  bf25d: number
  timestamp: Date
}

export interface MarketContext {
  currentTime: Date
  tradingSession: 'ASIA' | 'EUROPE' | 'US' | 'CLOSED'
  recentEvents: string[]
  volatilityTrend: 'RISING' | 'FALLING' | 'STABLE'
}