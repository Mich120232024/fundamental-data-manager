// Error recovery and retry logic for Bloomberg API
import { VolatilityData, SecurityData } from '../api/bloomberg'

export interface RetryConfig {
  maxRetries: number
  initialDelay: number
  maxDelay: number
  backoffMultiplier: number
  timeout: number
}

export interface RetryResult<T> {
  success: boolean
  data?: T
  error?: Error
  attempts: number
  duration: number
}

export class BloombergErrorRecovery {
  private static readonly DEFAULT_RETRY_CONFIG: RetryConfig = {
    maxRetries: 3,
    initialDelay: 1000,
    maxDelay: 10000,
    backoffMultiplier: 2,
    timeout: 30000
  }
  
  private static readonly RETRYABLE_ERRORS = [
    'ECONNREFUSED',
    'ETIMEDOUT',
    'ENOTFOUND',
    'NetworkError',
    'Request timeout',
    'Service temporarily unavailable'
  ]
  
  static isRetryableError(error: any): boolean {
    if (!error) return false
    
    const errorMessage = error.message || error.toString()
    return this.RETRYABLE_ERRORS.some(retryable => 
      errorMessage.includes(retryable)
    )
  }
  
  static async withRetry<T>(
    operation: () => Promise<T>,
    config: Partial<RetryConfig> = {}
  ): Promise<RetryResult<T>> {
    const finalConfig = { ...this.DEFAULT_RETRY_CONFIG, ...config }
    const startTime = Date.now()
    let lastError: Error | undefined
    
    for (let attempt = 1; attempt <= finalConfig.maxRetries; attempt++) {
      try {
        const result = await Promise.race([
          operation(),
          new Promise<never>((_, reject) => 
            setTimeout(() => reject(new Error('Request timeout')), finalConfig.timeout)
          )
        ])
        
        return {
          success: true,
          data: result,
          attempts: attempt,
          duration: Date.now() - startTime
        }
      } catch (error) {
        lastError = error as Error
        console.log(`Attempt ${attempt} failed:`, error)
        
        if (!this.isRetryableError(error) || attempt === finalConfig.maxRetries) {
          break
        }
        
        // Calculate delay with exponential backoff
        const delay = Math.min(
          finalConfig.initialDelay * Math.pow(finalConfig.backoffMultiplier, attempt - 1),
          finalConfig.maxDelay
        )
        
        console.log(`Retrying in ${delay}ms...`)
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
    
    return {
      success: false,
      error: lastError,
      attempts: finalConfig.maxRetries,
      duration: Date.now() - startTime
    }
  }
  
  static async batchWithRecovery<T>(
    items: T[],
    batchSize: number,
    processor: (batch: T[]) => Promise<any>,
    onBatchError?: (batch: T[], error: Error) => void
  ): Promise<{
    successful: T[]
    failed: T[]
    errors: Map<T[], Error>
  }> {
    const successful: T[] = []
    const failed: T[] = []
    const errors = new Map<T[], Error>()
    
    // Process in batches
    for (let i = 0; i < items.length; i += batchSize) {
      const batch = items.slice(i, i + batchSize)
      
      const result = await this.withRetry(
        () => processor(batch),
        { maxRetries: 2, initialDelay: 500 }
      )
      
      if (result.success) {
        successful.push(...batch)
      } else {
        failed.push(...batch)
        if (result.error) {
          errors.set(batch, result.error)
          onBatchError?.(batch, result.error)
        }
        
        // Try individual items from failed batch
        for (const item of batch) {
          const individualResult = await this.withRetry(
            () => processor([item]),
            { maxRetries: 1, initialDelay: 200 }
          )
          
          if (individualResult.success) {
            successful.push(item)
            const index = failed.indexOf(item)
            if (index > -1) failed.splice(index, 1)
          }
        }
      }
    }
    
    return { successful, failed, errors }
  }
  
  static createFallbackData(tenor: string): VolatilityData {
    // Create placeholder data when Bloomberg is unavailable
    return {
      tenor,
      atm_bid: null,
      atm_ask: null,
      rr_5d_bid: null,
      rr_5d_ask: null,
      bf_5d_bid: null,
      bf_5d_ask: null,
      rr_10d_bid: null,
      rr_10d_ask: null,
      bf_10d_bid: null,
      bf_10d_ask: null,
      rr_15d_bid: null,
      rr_15d_ask: null,
      bf_15d_bid: null,
      bf_15d_ask: null,
      rr_25d_bid: null,
      rr_25d_ask: null,
      bf_25d_bid: null,
      bf_25d_ask: null,
      rr_35d_bid: null,
      rr_35d_ask: null,
      bf_35d_bid: null,
      bf_35d_ask: null
    }
  }
  
  static async healthCheckWithRecovery(
    healthCheckFn: () => Promise<any>,
    recoveryFn: () => Promise<void>
  ): Promise<boolean> {
    const healthResult = await this.withRetry(healthCheckFn, {
      maxRetries: 2,
      initialDelay: 1000,
      timeout: 5000
    })
    
    if (!healthResult.success) {
      console.log('Health check failed, attempting recovery...')
      
      try {
        await recoveryFn()
        
        // Re-check after recovery
        const recheckResult = await this.withRetry(healthCheckFn, {
          maxRetries: 1,
          timeout: 5000
        })
        
        return recheckResult.success
      } catch (error) {
        console.error('Recovery failed:', error)
        return false
      }
    }
    
    return true
  }
  
  static getErrorMessage(error: any): string {
    if (!error) return 'Unknown error'
    
    // Handle different error types
    if (error.response?.data?.error) {
      return error.response.data.error
    }
    
    if (error.message) {
      // Make error messages more user-friendly
      if (error.message.includes('ECONNREFUSED')) {
        return 'Bloomberg service is unavailable. Please try again later.'
      }
      if (error.message.includes('timeout')) {
        return 'Request timed out. The Bloomberg service may be busy.'
      }
      if (error.message.includes('Network')) {
        return 'Network error. Please check your connection.'
      }
      
      return error.message
    }
    
    return String(error)
  }
  
  static createErrorSummary(errors: Error[]): {
    summary: string
    details: string[]
    isRecoverable: boolean
  } {
    const uniqueErrors = [...new Set(errors.map(e => this.getErrorMessage(e)))]
    const retryableCount = errors.filter(e => this.isRetryableError(e)).length
    
    let summary = 'Multiple errors occurred'
    if (retryableCount === errors.length) {
      summary = 'Temporary connection issues with Bloomberg service'
    } else if (retryableCount === 0) {
      summary = 'Data validation or configuration errors'
    }
    
    return {
      summary,
      details: uniqueErrors,
      isRecoverable: retryableCount > 0
    }
  }
}

// Circuit breaker pattern for API protection
export class CircuitBreaker {
  private failures = 0
  private lastFailure: Date | null = null
  private state: 'closed' | 'open' | 'half-open' = 'closed'
  
  constructor(
    private readonly threshold: number = 5,
    private readonly timeout: number = 60000 // 1 minute
  ) {}
  
  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === 'open') {
      if (Date.now() - (this.lastFailure?.getTime() || 0) > this.timeout) {
        this.state = 'half-open'
      } else {
        throw new Error('Circuit breaker is open - service unavailable')
      }
    }
    
    try {
      const result = await operation()
      
      if (this.state === 'half-open') {
        this.reset()
      }
      
      return result
    } catch (error) {
      this.recordFailure()
      throw error
    }
  }
  
  private recordFailure() {
    this.failures++
    this.lastFailure = new Date()
    
    if (this.failures >= this.threshold) {
      this.state = 'open'
      console.warn(`Circuit breaker opened after ${this.failures} failures`)
    }
  }
  
  private reset() {
    this.failures = 0
    this.lastFailure = null
    this.state = 'closed'
    console.log('Circuit breaker reset')
  }
  
  getState() {
    return {
      state: this.state,
      failures: this.failures,
      lastFailure: this.lastFailure
    }
  }
}