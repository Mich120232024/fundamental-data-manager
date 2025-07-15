import axios from 'axios';
import type { BloombergResponse } from '../types/volatility';

const BLOOMBERG_API_URL = 'http://20.172.249.92:8080';

export const bloombergService = {
  async fetchMarketData(securities: string[], fields: string[] = ['PX_LAST', 'PX_MID']) {
    try {
      const response = await axios.post<BloombergResponse[]>(
        `${BLOOMBERG_API_URL}/api/market-data`,
        {
          securities,
          fields
        }
      );
      return response.data;
    } catch (error) {
      console.error('Bloomberg API error:', error);
      throw error;
    }
  },

  async fetchVolatilitySurface(pair: string = 'EURUSD') {
    const securities = [
      // Spot
      `${pair} Curncy`,
      // ATM Volatilities
      `${pair}V1W Curncy`, `${pair}V2W Curncy`, `${pair}V1M Curncy`,
      `${pair}V2M Curncy`, `${pair}V3M Curncy`, `${pair}V6M Curncy`,
      `${pair}V9M Curncy`, `${pair}V1Y Curncy`, `${pair}V2Y Curncy`,
      `${pair}V3Y Curncy`, `${pair}V5Y Curncy`,
      // 25D Risk Reversals
      `EUR25R1W Curncy`, `EUR25R2W Curncy`, `EUR25R1M Curncy`,
      `EUR25R2M Curncy`, `EUR25R3M Curncy`, `EUR25R6M Curncy`,
      `EUR25R9M Curncy`, `EUR25R1Y Curncy`, `EUR25R2Y Curncy`,
      `EUR25R3Y Curncy`, `EUR25R5Y Curncy`,
      // 25D Butterflies
      `EUR25B1W Curncy`, `EUR25B2W Curncy`, `EUR25B1M Curncy`,
      `EUR25B2M Curncy`, `EUR25B3M Curncy`, `EUR25B6M Curncy`,
      `EUR25B9M Curncy`, `EUR25B1Y Curncy`, `EUR25B2Y Curncy`,
      `EUR25B3Y Curncy`, `EUR25B5Y Curncy`,
      // 10D Risk Reversals
      `EUR10R1M Curncy`, `EUR10R3M Curncy`, `EUR10R6M Curncy`, `EUR10R1Y Curncy`,
      // 10D Butterflies
      `EUR10B1M Curncy`, `EUR10B3M Curncy`, `EUR10B6M Curncy`, `EUR10B1Y Curncy`
    ];

    return this.fetchMarketData(securities);
  }
};