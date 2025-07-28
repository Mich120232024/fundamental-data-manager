// Portfolio Service - Bloomberg Integration and Portfolio Management

import { bloombergAPI } from '../api/bloomberg'
import type { 
  Portfolio, 
  FXOptionPosition, 
  NewPositionForm, 
  PortfolioValuation, 
  PositionValuationSummary,
  TickerValidationResult 
} from '../types/portfolio'

class PortfolioService {
  private portfolios: Map<string, Portfolio> = new Map()
  
  // Portfolio Management
  createPortfolio(name: string, description?: string, baseCurrency: string = 'USD', type: 'active' | 'virtual' = 'active'): Portfolio {
    const portfolio: Portfolio = {
      id: `portfolio_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name,
      description,
      baseCurrency,
      positions: [],
      createdAt: new Date(),
      updatedAt: new Date(),
      type
    }
    
    this.portfolios.set(portfolio.id, portfolio)
    console.log(`✅ Created ${type} portfolio: ${name} (${portfolio.id})`)
    return portfolio
  }
  
  getPortfolio(portfolioId: string): Portfolio | null {
    return this.portfolios.get(portfolioId) || null
  }
  
  getAllPortfolios(): Portfolio[] {
    return Array.from(this.portfolios.values())
  }
  
  deletePortfolio(portfolioId: string): boolean {
    const success = this.portfolios.delete(portfolioId)
    if (success) {
      console.log(`🗑️ Deleted portfolio: ${portfolioId}`)
    }
    return success
  }
  
  // Position Management
  async addPosition(portfolioId: string, positionForm: NewPositionForm): Promise<FXOptionPosition | null> {
    const portfolio = this.portfolios.get(portfolioId)
    if (!portfolio) {
      console.error(`Portfolio not found: ${portfolioId}`)
      return null
    }
    
    // Validate ticker format
    const validation = this.validateTicker(positionForm.ticker)
    if (!validation.isValid) {
      console.error(`Invalid ticker: ${positionForm.ticker} - ${validation.error}`)
      throw new Error(`Invalid ticker: ${validation.error}`)
    }
    
    const position: FXOptionPosition = {
      id: `pos_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      ticker: validation.normalizedTicker || positionForm.ticker,
      description: positionForm.description,
      quantity: positionForm.quantity,
      entryPrice: positionForm.entryPrice,
      currency: portfolio.baseCurrency,
      portfolioId: portfolioId,
      lastUpdated: new Date()
    }
    
    // Try to get current price from Bloomberg
    try {
      const currentPrice = await this.fetchTickerPrice(position.ticker)
      position.currentPrice = currentPrice || undefined
      console.log(`📈 Fetched price for ${position.ticker}: ${currentPrice}`)
    } catch (error) {
      console.warn(`⚠️ Could not fetch price for ${position.ticker}:`, error)
    }
    
    portfolio.positions.push(position)
    portfolio.updatedAt = new Date()
    
    console.log(`✅ Added position: ${position.ticker} (qty: ${position.quantity})`)
    return position
  }
  
  updatePosition(positionId: string, updates: Partial<FXOptionPosition>): void {
    for (const portfolio of this.portfolios.values()) {
      const positionIndex = portfolio.positions.findIndex(p => p.id === positionId)
      if (positionIndex !== -1) {
        portfolio.positions[positionIndex] = {
          ...portfolio.positions[positionIndex],
          ...updates,
          lastUpdated: new Date()
        }
        portfolio.updatedAt = new Date()
        console.log(`✅ Updated position: ${positionId}`)
        return
      }
    }
    console.error(`Position not found: ${positionId}`)
  }
  
  removePosition(positionId: string): void {
    for (const portfolio of this.portfolios.values()) {
      const positionIndex = portfolio.positions.findIndex(p => p.id === positionId)
      if (positionIndex !== -1) {
        const removedPosition = portfolio.positions.splice(positionIndex, 1)[0]
        portfolio.updatedAt = new Date()
        console.log(`🗑️ Removed position: ${removedPosition.ticker}`)
        return
      }
    }
    console.error(`Position not found: ${positionId}`)
  }
  
  // Bloomberg Integration
  validateTicker(ticker: string): TickerValidationResult {
    // Basic ticker validation for FX options
    const trimmedTicker = ticker.trim().toUpperCase()
    
    // Bloomberg FX option patterns
    const patterns = [
      // ATM: EURUSDV1M BGN Curncy, EURUSDVON Curncy
      /^([A-Z]{6})V(ON|\d+[DWMY])\s*(BGN\s*)?CURNCY?$/i,
      // Risk Reversal: EURUSD25R1M BGN Curncy
      /^([A-Z]{6})(\d+)R(\d+[DWMY])\s*(BGN\s*)?CURNCY?$/i,
      // Butterfly: EURUSD25B1M BGN Curncy  
      /^([A-Z]{6})(\d+)B(\d+[DWMY])\s*(BGN\s*)?CURNCY?$/i,
      // Spot rates: EURUSD Curncy
      /^([A-Z]{6})\s*CURNCY?$/i
    ]
    
    for (const pattern of patterns) {
      if (pattern.test(trimmedTicker)) {
        // Normalize the ticker format
        let normalized = trimmedTicker
        if (!normalized.endsWith(' CURNCY')) {
          normalized = normalized.replace(/CURNCY?$/i, ' CURNCY')
        }
        
        return {
          isValid: true,
          ticker: ticker,
          normalizedTicker: normalized,
          tickerType: this.classifyTicker(normalized)
        }
      }
    }
    
    return {
      isValid: false,
      ticker: ticker,
      error: 'Invalid Bloomberg FX option ticker format. Expected formats: EURUSDV1M BGN CURNCY, EURUSD25R1M BGN CURNCY, EURUSD25B1M BGN CURNCY'
    }
  }
  
  private classifyTicker(ticker: string): 'atm' | 'risk_reversal' | 'butterfly' | 'spot' | 'unknown' {
    if (ticker.includes('V') && (ticker.includes('BGN') || ticker.includes('VON'))) return 'atm'
    if (ticker.includes('R') && ticker.includes('BGN')) return 'risk_reversal'
    if (ticker.includes('B') && ticker.includes('BGN')) return 'butterfly'
    if (ticker.match(/^[A-Z]{6}\s+CURNCY$/)) return 'spot'
    return 'unknown'
  }
  
  async fetchTickerPrice(ticker: string): Promise<number | null> {
    try {
      console.log(`🔍 Fetching price for ticker: ${ticker}`)
      const response = await bloombergAPI.getReferenceData([ticker], ['PX_LAST', 'PX_BID', 'PX_ASK'])
      
      if (response.success && response.securities_data && response.securities_data.length > 0) {
        const securityData = response.securities_data[0]
        if (securityData.success && securityData.fields) {
          // Prefer PX_LAST, fallback to mid of bid/ask
          const price = securityData.fields.PX_LAST || 
                       (securityData.fields.PX_BID && securityData.fields.PX_ASK 
                        ? (securityData.fields.PX_BID + securityData.fields.PX_ASK) / 2 
                        : null)
          
          console.log(`📊 Price fetched for ${ticker}: ${price}`)
          return price
        }
      }
      
      console.warn(`⚠️ No price data returned for ${ticker}`)
      return null
    } catch (error) {
      console.error(`❌ Error fetching price for ${ticker}:`, error)
      throw error
    }
  }
  
  async updateAllPrices(portfolioId: string): Promise<void> {
    const portfolio = this.portfolios.get(portfolioId)
    if (!portfolio) {
      throw new Error(`Portfolio not found: ${portfolioId}`)
    }
    
    console.log(`🔄 Updating prices for portfolio: ${portfolio.name}`)
    const updatePromises = portfolio.positions.map(async (position) => {
      try {
        const newPrice = await this.fetchTickerPrice(position.ticker)
        if (newPrice !== null) {
          position.currentPrice = newPrice
          position.lastUpdated = new Date()
        }
        return { ticker: position.ticker, success: true, price: newPrice }
      } catch (error) {
        console.error(`Failed to update price for ${position.ticker}:`, error)
        return { ticker: position.ticker, success: false, error }
      }
    })
    
    const results = await Promise.all(updatePromises)
    const successful = results.filter(r => r.success).length
    const failed = results.filter(r => !r.success).length
    
    portfolio.updatedAt = new Date()
    console.log(`✅ Price update complete: ${successful} successful, ${failed} failed`)
  }
  
  // Portfolio Valuation
  calculateValuation(portfolioId: string): PortfolioValuation {
    const portfolio = this.portfolios.get(portfolioId)
    if (!portfolio) {
      throw new Error(`Portfolio not found: ${portfolioId}`)
    }
    
    const positionSummaries: PositionValuationSummary[] = portfolio.positions.map(position => {
      const marketValue = position.currentPrice !== null && position.currentPrice !== undefined
        ? position.quantity * position.currentPrice
        : null
      
      const unrealizedPnL = position.entryPrice !== null && position.entryPrice !== undefined && 
                           position.currentPrice !== null && position.currentPrice !== undefined
        ? position.quantity * (position.currentPrice - position.entryPrice)
        : null
      
      const pnlPercent = position.entryPrice !== null && position.entryPrice !== undefined && 
                        position.currentPrice !== null && position.currentPrice !== undefined && 
                        position.entryPrice !== 0
        ? ((position.currentPrice - position.entryPrice) / position.entryPrice) * 100
        : null
      
      return {
        positionId: position.id,
        ticker: position.ticker,
        quantity: position.quantity,
        entryPrice: position.entryPrice || null,
        currentPrice: position.currentPrice || null,
        marketValue,
        unrealizedPnL,
        pnlPercent
      }
    })
    
    const totalMarketValue = positionSummaries
      .filter(p => p.marketValue !== null)
      .reduce((sum, p) => sum + (p.marketValue || 0), 0)
    
    const totalUnrealizedPnL = positionSummaries
      .filter(p => p.unrealizedPnL !== null)
      .reduce((sum, p) => sum + (p.unrealizedPnL || 0), 0)
    
    return {
      portfolioId: portfolio.id,
      portfolioName: portfolio.name,
      baseCurrency: portfolio.baseCurrency,
      totalPositions: portfolio.positions.length,
      totalMarketValue,
      totalUnrealizedPnL,
      lastUpdated: new Date(),
      positionValueSummary: positionSummaries
    }
  }
}

// Export singleton instance
export const portfolioService = new PortfolioService()