import Anthropic from '@anthropic-ai/sdk'
import axios from 'axios'
import * as fs from 'fs/promises'
import * as path from 'path'
import dotenv from 'dotenv'
import { fileURLToPath } from 'url'
import { dirname } from 'path'
import type { AgentState, AgentDecision, MarketContext, VolatilityData } from './types.js'

// Load environment variables
const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
dotenv.config({ path: path.join(__dirname, '..', '.env') })

const AGENT_SYSTEM_PROMPT = `You are an autonomous FX volatility trading agent with deep market expertise.

Your capabilities:
- Access to Bloomberg Terminal data via API
- Analysis of volatility surfaces, term structures, and skew
- Detection of market regime changes
- Generation of trading recommendations
- Learning from market outcomes

Your mandate:
- Monitor FX volatility markets continuously
- Identify mispricing and regime shifts
- Recommend high-Sharpe ratio volatility trades
- Maintain disciplined risk management
- Learn and adapt from market feedback

Current Bloomberg API endpoint: ${process.env.BLOOMBERG_API_URL}

When making decisions:
1. Analyze the current state and market context
2. Reason step-by-step about what action to take
3. Consider risk/reward and market conditions
4. Learn from past successes and failures

Always output your decision in this JSON format:
{
  "action": "FETCH_VOLATILITY|ANALYZE_REGIME|RECOMMEND_POSITION|UPDATE_POSITIONS|WAIT",
  "reasoning": "Step-by-step explanation of your thinking",
  "confidence": 0.0-1.0,
  "params": {
    // Action-specific parameters
  }
}`

export class AutonomousVolatilityAgent {
  private anthropic: Anthropic
  private state: AgentState
  private stateFile: string
  private running: boolean = false

  constructor() {
    if (!process.env.ANTHROPIC_API_KEY) {
      throw new Error('ANTHROPIC_API_KEY not found in environment')
    }
    
    this.anthropic = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    })
    
    this.stateFile = process.env.AGENT_STATE_FILE || './state/agent_state.json'
    this.state = this.loadState()
  }

  private loadState(): AgentState {
    try {
      const stateData = fs.readFileSync(this.stateFile, 'utf-8')
      return JSON.parse(stateData)
    } catch (error) {
      console.log('No previous state found, initializing new state')
      return {
        lastAnalysis: null,
        marketRegime: 'UNKNOWN',
        positions: [],
        performance: [],
        learnings: []
      }
    }
  }

  private async saveState(): Promise<void> {
    const dir = path.dirname(this.stateFile)
    await fs.mkdir(dir, { recursive: true })
    await fs.writeFile(this.stateFile, JSON.stringify(this.state, null, 2))
  }

  async start(): Promise<void> {
    console.log('🤖 Autonomous Volatility Agent Starting...')
    console.log(`📊 Current state: ${this.state.marketRegime} regime`)
    console.log(`💼 Open positions: ${this.state.positions.filter(p => p.status === 'OPEN').length}`)
    
    this.running = true
    
    while (this.running) {
      try {
        await this.runCycle()
        
        // Wait before next cycle
        const interval = parseInt(process.env.AGENT_RUN_INTERVAL || '60000')
        console.log(`⏳ Waiting ${interval/1000} seconds until next cycle...`)
        await this.sleep(interval)
        
      } catch (error) {
        console.error('❌ Agent cycle error:', error)
        await this.handleError(error)
      }
    }
  }

  private async runCycle(): Promise<void> {
    console.log('\n🔄 Starting new agent cycle...')
    
    // Get market context
    const context = await this.getMarketContext()
    
    // Let Claude reason about next action
    const decision = await this.getClaudeDecision(context)
    
    // Execute the decision
    await this.executeDecision(decision)
    
    // Save updated state
    await this.saveState()
  }

  private async getMarketContext(): Promise<MarketContext> {
    const now = new Date()
    const hour = now.getUTCHours()
    
    let session: MarketContext['tradingSession']
    if (hour >= 0 && hour < 6) session = 'ASIA'
    else if (hour >= 6 && hour < 13) session = 'EUROPE'
    else if (hour >= 13 && hour < 21) session = 'US'
    else session = 'CLOSED'
    
    // Analyze recent performance to determine trend
    const recentPerf = this.state.performance.slice(-5)
    const successRate = recentPerf.filter(p => p.outcome === 'SUCCESS').length / recentPerf.length
    
    return {
      currentTime: now,
      tradingSession: session,
      recentEvents: this.state.learnings.slice(-3).map(l => l.observation),
      volatilityTrend: successRate > 0.6 ? 'RISING' : successRate < 0.4 ? 'FALLING' : 'STABLE'
    }
  }

  private async getClaudeDecision(context: MarketContext): Promise<AgentDecision> {
    console.log('🧠 Asking Claude for decision...')
    
    const message = await this.anthropic.messages.create({
      model: 'claude-3-sonnet-20240229',
      max_tokens: 1500,
      temperature: 0.7,
      system: AGENT_SYSTEM_PROMPT,
      messages: [{
        role: 'user',
        content: `Current market context:
${JSON.stringify(context, null, 2)}

Current agent state:
${JSON.stringify(this.state, null, 2)}

What should I do next? Reason step-by-step and provide your decision.`
      }]
    })
    
    // Extract JSON from Claude's response
    const responseText = message.content[0].type === 'text' ? message.content[0].text : ''
    const jsonMatch = responseText.match(/\{[\s\S]*\}/)
    
    if (!jsonMatch) {
      throw new Error('Could not parse JSON decision from Claude response')
    }
    
    const decision = JSON.parse(jsonMatch[0]) as AgentDecision
    console.log(`✅ Decision: ${decision.action} (confidence: ${decision.confidence})`)
    console.log(`📝 Reasoning: ${decision.reasoning.substring(0, 200)}...`)
    
    return decision
  }

  private async executeDecision(decision: AgentDecision): Promise<void> {
    console.log(`🚀 Executing: ${decision.action}`)
    
    switch (decision.action) {
      case 'FETCH_VOLATILITY':
        await this.fetchVolatilityData(decision.params)
        break
        
      case 'ANALYZE_REGIME':
        await this.analyzeMarketRegime()
        break
        
      case 'RECOMMEND_POSITION':
        await this.generateTradeRecommendation(decision.params)
        break
        
      case 'UPDATE_POSITIONS':
        await this.updatePositions()
        break
        
      case 'WAIT':
        console.log('⏸️  Agent decided to wait and observe')
        break
        
      default:
        console.warn(`Unknown action: ${decision.action}`)
    }
    
    // Record the action
    this.state.performance.push({
      date: new Date(),
      action: decision.action,
      outcome: 'SUCCESS', // Will be updated based on results
      details: decision.reasoning
    })
  }

  private async fetchVolatilityData(params: any): Promise<void> {
    console.log('📊 Fetching Bloomberg volatility data...')
    
    const currencyPair = params.currencyPair || 'EURUSD'
    const tenors = params.tenors || ['1M', '3M', '6M']
    
    try {
      const response = await axios.post(
        `${process.env.BLOOMBERG_API_URL}/api/volatility/surface`,
        {
          currency_pair: currencyPair,
          tenors: tenors
        },
        {
          headers: {
            'Authorization': `Bearer ${process.env.BLOOMBERG_API_KEY}`,
            'Content-Type': 'application/json'
          }
        }
      )
      
      const data = response.data
      console.log(`✅ Fetched ${data.length} volatility points`)
      
      // Analyze the data with Claude
      await this.analyzeWithClaude(data)
      
    } catch (error) {
      console.error('❌ Failed to fetch Bloomberg data:', error)
      throw error
    }
  }

  private async analyzeWithClaude(data: any): Promise<void> {
    console.log('🔍 Analyzing data with Claude...')
    
    const analysis = await this.anthropic.messages.create({
      model: 'claude-3-sonnet-20240229',
      max_tokens: 1000,
      temperature: 0.5,
      messages: [{
        role: 'user',
        content: `Analyze this FX volatility data and provide insights:

${JSON.stringify(data, null, 2)}

Provide:
1. Current market regime assessment
2. Key observations about the volatility surface
3. Any anomalies or opportunities
4. Risk factors to monitor`
      }]
    })
    
    const analysisText = analysis.content[0].type === 'text' ? analysis.content[0].text : ''
    
    // Update state with analysis
    this.state.lastAnalysis = {
      timestamp: new Date(),
      regime: this.extractRegime(analysisText),
      observations: this.extractObservations(analysisText),
      confidence: 0.85
    }
    
    console.log('✅ Analysis complete')
  }

  private async analyzeMarketRegime(): Promise<void> {
    console.log('🎯 Analyzing market regime...')
    
    // This would fetch more data and perform deeper analysis
    // For now, we'll use the last analysis
    if (this.state.lastAnalysis) {
      this.state.marketRegime = this.state.lastAnalysis.regime
      console.log(`📈 Market regime: ${this.state.marketRegime}`)
    }
  }

  private async generateTradeRecommendation(params: any): Promise<void> {
    console.log('💡 Generating trade recommendation...')
    
    // In a real implementation, this would:
    // 1. Analyze current positions
    // 2. Check risk limits
    // 3. Generate specific trade ideas
    // 4. Calculate expected returns
    
    console.log('📋 Trade recommendation generated (implementation pending)')
  }

  private async updatePositions(): Promise<void> {
    console.log('📊 Updating positions...')
    
    // Update P&L, check stops, etc.
    for (const position of this.state.positions.filter(p => p.status === 'OPEN')) {
      console.log(`Position ${position.id}: ${position.currencyPair} ${position.strategy}`)
    }
  }

  private async handleError(error: any): Promise<void> {
    // Let Claude reason about the error
    const errorDecision = await this.anthropic.messages.create({
      model: 'claude-3-sonnet-20240229',
      max_tokens: 500,
      messages: [{
        role: 'user',
        content: `An error occurred: ${error.message}
        
How should the agent handle this? Should we retry, wait, or take alternative action?`
      }]
    })
    
    console.log('🔧 Error handling:', errorDecision.content[0])
  }

  private extractRegime(text: string): AgentState['marketRegime'] {
    // Simple extraction - in production would use better NLP
    if (text.includes('COMPRESSED')) return 'COMPRESSED'
    if (text.includes('LOW_VOL')) return 'LOW_VOL'
    if (text.includes('STRESSED')) return 'STRESSED'
    if (text.includes('CRISIS')) return 'CRISIS'
    return 'NORMAL'
  }

  private extractObservations(text: string): string[] {
    // Extract key observations from analysis
    const lines = text.split('\n')
    return lines
      .filter(line => line.includes('-') || line.includes('•'))
      .map(line => line.trim())
      .slice(0, 5)
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  stop(): void {
    console.log('🛑 Stopping agent...')
    this.running = false
  }
}

// Run the agent if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const agent = new AutonomousVolatilityAgent()
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    agent.stop()
    process.exit(0)
  })
  
  agent.start().catch(console.error)
}