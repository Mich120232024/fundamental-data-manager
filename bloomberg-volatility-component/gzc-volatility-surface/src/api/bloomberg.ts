// Bloomberg API Client for Volatility Surface
import axios from 'axios'

// Always use direct Bloomberg VM API URL
const BLOOMBERG_API_URL = 'http://20.172.249.92:8080'
const API_KEY = 'test'

export interface VolatilityData {
  tenor: string
  atm_bid: number | null
  atm_ask: number | null
  rr_5d_bid: number | null
  rr_5d_ask: number | null
  bf_5d_bid: number | null
  bf_5d_ask: number | null
  rr_10d_bid: number | null
  rr_10d_ask: number | null
  bf_10d_bid: number | null
  bf_10d_ask: number | null
  rr_15d_bid: number | null
  rr_15d_ask: number | null
  bf_15d_bid: number | null
  bf_15d_ask: number | null
  rr_25d_bid: number | null
  rr_25d_ask: number | null
  bf_25d_bid: number | null
  bf_25d_ask: number | null
  rr_35d_bid: number | null
  rr_35d_ask: number | null
  bf_35d_bid: number | null
  bf_35d_ask: number | null
}

export interface SecurityData {
  security: string
  fields: {
    PX_LAST?: number
    PX_BID?: number
    PX_ASK?: number
  }
  success: boolean
  error?: string
}

// Standard FX option tenors - only those with available Bloomberg data
export const STANDARD_TENORS = [
  "ON",   // Overnight (O/N)
  "1W",   // 1 week
  "2W",   // 2 weeks
  "3W",   // 3 weeks
  "1M",   // 1 month
  "2M",   // 2 months
  "3M",   // 3 months
  "4M",   // 4 months
  "6M",   // 6 months
  "9M",   // 9 months
  "1Y",   // 1 year
  "18M",  // 18 months
  "2Y"    // 2 years
]

class BloombergAPIClient {
  private headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_KEY}`,
    'X-API-Key': API_KEY
  }

  async healthCheck() {
    try {
      const response = await axios.get(`${BLOOMBERG_API_URL}/health`)
      return response.data
    } catch (error) {
      console.error('Health check failed:', error)
      throw error
    }
  }

  async getReferenceData(securities: string[], fields: string[]) {
    try {
      console.log('Sending request to bloomberg/reference:', { securities, fields })
      const response = await axios.post(
        `${BLOOMBERG_API_URL}/api/bloomberg/reference`,
        { securities, fields },
        { headers: this.headers }
      )
      console.log('Raw API response:', JSON.stringify(response.data, null, 2))
      return response.data
    } catch (error) {
      console.error('Reference data request failed:', error)
      throw error
    }
  }

  async startBloombergService() {
    try {
      // Use Azure CLI to start the Bloomberg API service on the VM
      const response = await axios.post(
        `${BLOOMBERG_API_URL}/api/vm/service/start`,
        {},
        { headers: this.headers }
      )
      return response.data
    } catch (error) {
      console.error('Failed to start Bloomberg service:', error)
      throw error
    }
  }

  async stopBloombergService() {
    try {
      // Use Azure CLI to stop the Bloomberg API service on the VM
      const response = await axios.post(
        `${BLOOMBERG_API_URL}/api/vm/service/stop`,
        {},
        { headers: this.headers }
      )
      return response.data
    } catch (error) {
      console.error('Failed to stop Bloomberg service:', error)
      throw error
    }
  }

  async getServiceStatus() {
    try {
      // Check if the Bloomberg API service is running on the VM
      const response = await axios.get(
        `${BLOOMBERG_API_URL}/api/vm/service/status`,
        { headers: this.headers }
      )
      return response.data
    } catch (error) {
      console.error('Failed to get service status:', error)
      // If we can't reach the status endpoint, the service is probably down
      return { success: false, service_running: false, error: 'Service unreachable' }
    }
  }

  async getHistoricalData(security: string, fields: string[], startDate: string, endDate: string) {
    try {
      console.log('Fetching historical data:', { security, fields, startDate, endDate })
      const response = await axios.post(
        `${BLOOMBERG_API_URL}/api/bloomberg/historical`,
        { 
          security, 
          fields, 
          start_date: startDate,
          end_date: endDate,
          periodicity: 'DAILY'
        },
        { headers: this.headers }
      )
      console.log('Historical data response:', response.data)
      return response.data
    } catch (error) {
      console.error('Historical data request failed:', error)
      throw error
    }
  }

  async getVolatilitySurface(currencyPair: string = "EURUSD", tenors: string[] = STANDARD_TENORS, date?: string): Promise<VolatilityData[]> {
    const results: VolatilityData[] = []
    
    // If date is provided, we need to use historical data endpoint
    if (date) {
      // Get historical data for the specific date
      return this.getHistoricalVolatilitySurface(currencyPair, tenors, date)
    }
    
    // Process tenors in batches (live data)
    for (const tenor of tenors) {
      try {
        // For ON tenor, use different format (no BGN)
        const isON = tenor === 'ON'
        // For 1D/2D/3D tenors, use special format per production requirements
        const isShortDated = ['1D', '2D', '3D'].includes(tenor)
        
        const securities = [
          // ATM Volatility
          isON ? `${currencyPair}V${tenor} Curncy` : `${currencyPair}V${tenor} BGN Curncy`,
          
          // Risk Reversals - All available deltas
          `${currencyPair}5R${tenor} BGN Curncy`,    // 5D RR
          `${currencyPair}10R${tenor} BGN Curncy`,   // 10D RR
          `${currencyPair}15R${tenor} BGN Curncy`,   // 15D RR
          `${currencyPair}25R${tenor} BGN Curncy`,   // 25D RR
          `${currencyPair}35R${tenor} BGN Curncy`,   // 35D RR
          
          // Butterflies - All available deltas
          `${currencyPair}5B${tenor} BGN Curncy`,    // 5D BF
          `${currencyPair}10B${tenor} BGN Curncy`,   // 10D BF
          `${currencyPair}15B${tenor} BGN Curncy`,   // 15D BF
          `${currencyPair}25B${tenor} BGN Curncy`,   // 25D BF
          `${currencyPair}35B${tenor} BGN Curncy`    // 35D BF
        ]
        
        const response = await this.getReferenceData(securities, ["PX_LAST", "PX_BID", "PX_ASK"])
        
        if (response.success && response.data) {
          console.log(`Processing ${tenor}:`, response.data.securities_data.length, 'securities')
          console.log('Securities data:', response.data.securities_data.map((s: any) => ({ 
            security: s.security, 
            success: s.success,
            fields: s.fields 
          })))
          const data = response.data.securities_data as SecurityData[]
          
          const tenorData: VolatilityData = {
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
          
          // Process each security with proper regex matching
          data.forEach((sec) => {
            if (sec.success && sec.fields) {
              const security = sec.security
              console.log(`Processing security: ${security}, value: ${sec.fields.PX_LAST}`)
              
              // Use regex to properly match delta and type
              // Pattern: EURUSD + delta + type + tenor + BGN Curncy (or just Curncy for ON)
              const atmMatch = isON 
                ? security.match(new RegExp(`${currencyPair}V${tenor}\\s+Curncy`))
                : security.match(new RegExp(`${currencyPair}V${tenor}\\s+BGN`))
              const rrBfMatch = security.match(new RegExp(`${currencyPair}(\\d+)(R|B)${tenor}\\s+BGN`))
              
              if (atmMatch) {
                // ATM volatility
                tenorData.atm_bid = sec.fields.PX_BID ?? null
                tenorData.atm_ask = sec.fields.PX_ASK ?? null
              } else if (rrBfMatch) {
                const delta = rrBfMatch[1]
                const type = rrBfMatch[2]
                
                if (type === 'R') {
                  // Risk Reversal
                  switch(delta) {
                    case '5': 
                      tenorData.rr_5d_bid = sec.fields.PX_BID ?? null
                      tenorData.rr_5d_ask = sec.fields.PX_ASK ?? null
                      break
                    case '10': 
                      tenorData.rr_10d_bid = sec.fields.PX_BID ?? null
                      tenorData.rr_10d_ask = sec.fields.PX_ASK ?? null
                      break
                    case '15': 
                      tenorData.rr_15d_bid = sec.fields.PX_BID ?? null
                      tenorData.rr_15d_ask = sec.fields.PX_ASK ?? null
                      break
                    case '25': 
                      tenorData.rr_25d_bid = sec.fields.PX_BID ?? null
                      tenorData.rr_25d_ask = sec.fields.PX_ASK ?? null
                      break
                    case '35': 
                      tenorData.rr_35d_bid = sec.fields.PX_BID ?? null
                      tenorData.rr_35d_ask = sec.fields.PX_ASK ?? null
                      break
                  }
                } else if (type === 'B') {
                  // Butterfly
                  switch(delta) {
                    case '5': 
                      tenorData.bf_5d_bid = sec.fields.PX_BID ?? null
                      tenorData.bf_5d_ask = sec.fields.PX_ASK ?? null
                      break
                    case '10': 
                      tenorData.bf_10d_bid = sec.fields.PX_BID ?? null
                      tenorData.bf_10d_ask = sec.fields.PX_ASK ?? null
                      break
                    case '15': 
                      tenorData.bf_15d_bid = sec.fields.PX_BID ?? null
                      tenorData.bf_15d_ask = sec.fields.PX_ASK ?? null
                      break
                    case '25': 
                      tenorData.bf_25d_bid = sec.fields.PX_BID ?? null
                      tenorData.bf_25d_ask = sec.fields.PX_ASK ?? null
                      break
                    case '35': 
                      tenorData.bf_35d_bid = sec.fields.PX_BID ?? null
                      tenorData.bf_35d_ask = sec.fields.PX_ASK ?? null
                      break
                  }
                }
              }
            }
          })
          
          console.log(`Final data for ${tenor}:`, {
            atm: { bid: tenorData.atm_bid, ask: tenorData.atm_ask },
            '5D': { rr_bid: tenorData.rr_5d_bid, rr_ask: tenorData.rr_5d_ask, bf_bid: tenorData.bf_5d_bid, bf_ask: tenorData.bf_5d_ask },
            '10D': { rr_bid: tenorData.rr_10d_bid, rr_ask: tenorData.rr_10d_ask, bf_bid: tenorData.bf_10d_bid, bf_ask: tenorData.bf_10d_ask }
          })
          console.log('Full tenorData:', tenorData)
          results.push(tenorData)
        }
      } catch (error) {
        console.error(`Failed to fetch data for tenor ${tenor}:`, error)
        // Add empty data for failed tenor
        results.push({
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
        })
      }
    }
    
    return results
  }

  async getHistoricalVolatilitySurface(currencyPair: string, tenors: string[], date: string): Promise<VolatilityData[]> {
    console.log('getHistoricalVolatilitySurface called with:', { currencyPair, date, tenorCount: tenors.length })
    const results: VolatilityData[] = []
    
    // For historical data, we need to fetch each security individually
    for (const tenor of tenors) {
      const tenorData: VolatilityData = {
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

      try {
        // Fetch all securities for this tenor
        const isON = tenor === 'ON'
        // For 1D/2D/3D tenors, use special format per production requirements
        const isShortDated = ['1D', '2D', '3D'].includes(tenor)
        
        const securities = [
          isON ? `${currencyPair}V${tenor} Curncy` : `${currencyPair}V${tenor} BGN Curncy`,
          `${currencyPair}5R${tenor} BGN Curncy`,
          `${currencyPair}10R${tenor} BGN Curncy`,
          `${currencyPair}15R${tenor} BGN Curncy`,
          `${currencyPair}25R${tenor} BGN Curncy`,
          `${currencyPair}35R${tenor} BGN Curncy`,
          `${currencyPair}5B${tenor} BGN Curncy`,
          `${currencyPair}10B${tenor} BGN Curncy`,
          `${currencyPair}15B${tenor} BGN Curncy`,
          `${currencyPair}25B${tenor} BGN Curncy`,
          `${currencyPair}35B${tenor} BGN Curncy`
        ]

        // Fetch historical data for each security
        const promises = securities.map(security => 
          this.getHistoricalData(security, ['PX_LAST', 'PX_BID', 'PX_ASK'], date, date)
            .then(result => {
              console.log(`Historical data for ${security}:`, result)
              return result
            })
            .catch(err => {
              console.error(`Failed to get historical data for ${security}:`, err)
              return { success: false, error: err.message, security }
            })
        )

        const responses = await Promise.all(promises)

        // Process responses
        responses.forEach((resp, index) => {
          if (resp.success && resp.data?.data?.length > 0) {
            const security = securities[index]
            const data = resp.data.data[0] // Get data for the specific date
            
            if (index === 0) {
              // ATM
              tenorData.atm_bid = data.PX_BID ?? null
              tenorData.atm_ask = data.PX_ASK ?? null
            } else {
              // Parse delta and type from security name
              const match = security.match(new RegExp(`${currencyPair}(\\d+)(R|B)${tenor}`))
              if (match) {
                const delta = match[1]
                const type = match[2]
                
                if (type === 'R') {
                  // Risk Reversal
                  switch(delta) {
                    case '5': 
                      tenorData.rr_5d_bid = data.PX_BID ?? null
                      tenorData.rr_5d_ask = data.PX_ASK ?? null
                      break
                    case '10': 
                      tenorData.rr_10d_bid = data.PX_BID ?? null
                      tenorData.rr_10d_ask = data.PX_ASK ?? null
                      break
                    case '15': 
                      tenorData.rr_15d_bid = data.PX_BID ?? null
                      tenorData.rr_15d_ask = data.PX_ASK ?? null
                      break
                    case '25': 
                      tenorData.rr_25d_bid = data.PX_BID ?? null
                      tenorData.rr_25d_ask = data.PX_ASK ?? null
                      break
                    case '35': 
                      tenorData.rr_35d_bid = data.PX_BID ?? null
                      tenorData.rr_35d_ask = data.PX_ASK ?? null
                      break
                  }
                } else if (type === 'B') {
                  // Butterfly
                  switch(delta) {
                    case '5': 
                      tenorData.bf_5d_bid = data.PX_BID ?? null
                      tenorData.bf_5d_ask = data.PX_ASK ?? null
                      break
                    case '10': 
                      tenorData.bf_10d_bid = data.PX_BID ?? null
                      tenorData.bf_10d_ask = data.PX_ASK ?? null
                      break
                    case '15': 
                      tenorData.bf_15d_bid = data.PX_BID ?? null
                      tenorData.bf_15d_ask = data.PX_ASK ?? null
                      break
                    case '25': 
                      tenorData.bf_25d_bid = data.PX_BID ?? null
                      tenorData.bf_25d_ask = data.PX_ASK ?? null
                      break
                    case '35': 
                      tenorData.bf_35d_bid = data.PX_BID ?? null
                      tenorData.bf_35d_ask = data.PX_ASK ?? null
                      break
                  }
                }
              }
            }
          }
        })

        results.push(tenorData)
      } catch (error) {
        console.error(`Failed to fetch historical data for tenor ${tenor}:`, error)
        results.push(tenorData) // Push empty data
      }
    }

    return results
  }
}

export const bloombergAPI = new BloombergAPIClient()