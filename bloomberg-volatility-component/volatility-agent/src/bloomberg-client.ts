import axios, { AxiosInstance } from 'axios'

export interface VolatilitySurfaceRequest {
  currency_pair: string
  tenors?: string[]
  date?: string
}

export interface VolatilitySurfaceResponse {
  currency_pair: string
  data: Array<{
    tenor: string
    atm_vol: number
    rr_25d: number
    bf_25d: number
    timestamp: string
  }>
  status: string
}

export class BloombergClient {
  private client: AxiosInstance
  
  constructor(baseURL: string, apiKey: string) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      timeout: 30000
    })
  }
  
  async getVolatilitySurface(params: VolatilitySurfaceRequest): Promise<VolatilitySurfaceResponse> {
    const response = await this.client.post('/api/volatility/surface', params)
    return response.data
  }
  
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health')
      return response.status === 200
    } catch {
      return false
    }
  }
}