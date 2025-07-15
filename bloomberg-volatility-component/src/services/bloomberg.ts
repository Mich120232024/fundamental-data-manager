export interface BloombergResponse {
  security: string;
  fields: Record<string, number>;
  timestamp: string;
  source: string;
}

export interface VolatilityData {
  pair: string;
  spot: number;
  atmVols: Record<string, number>;
  riskReversals25D: Record<string, number>;
  riskReversals10D: Record<string, number>;
  butterflies25D: Record<string, number>;
  butterflies10D: Record<string, number>;
  timestamp: string;
}

const PROXY_API_URL = '/api/bloomberg';

export const bloombergService = {
  async fetchVolatilitySurface(pair: string = 'EURUSD'): Promise<VolatilityData> {
    const securities = [
      // Spot
      `${pair} Curncy`,
      // ATM Volatilities
      `${pair}V1W Curncy`, `${pair}V1M Curncy`, `${pair}V3M Curncy`,
      `${pair}V6M Curncy`, `${pair}V1Y Curncy`, `${pair}V2Y Curncy`,
      // 25D Risk Reversals
      `EUR25R1W Curncy`, `EUR25R1M Curncy`, `EUR25R3M Curncy`,
      `EUR25R6M Curncy`, `EUR25R1Y Curncy`, `EUR25R2Y Curncy`,
      // 25D Butterflies
      `EUR25B1W Curncy`, `EUR25B1M Curncy`, `EUR25B3M Curncy`,
      `EUR25B6M Curncy`, `EUR25B1Y Curncy`, `EUR25B2Y Curncy`,
      // 10D Risk Reversals
      `EUR10R1M Curncy`, `EUR10R3M Curncy`, `EUR10R6M Curncy`, `EUR10R1Y Curncy`,
      // 10D Butterflies
      `EUR10B1M Curncy`, `EUR10B3M Curncy`, `EUR10B6M Curncy`, `EUR10B1Y Curncy`
    ];

    try {
      const response = await fetch(`${PROXY_API_URL}/market-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          securities,
          fields: ['PX_LAST', 'PX_MID']
        })
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data: BloombergResponse[] = await response.json();
      
      // Process Bloomberg response into volatility surface
      const getValue = (security: string) => {
        const item = data.find(d => d.security === security);
        return item?.fields?.PX_LAST || item?.fields?.PX_MID || 0;
      };

      const spot = getValue(`${pair} Curncy`);
      
      const atmVols: Record<string, number> = {};
      const tenors = ['1W', '1M', '3M', '6M', '1Y', '2Y'];
      tenors.forEach(tenor => {
        const vol = getValue(`${pair}V${tenor} Curncy`);
        if (vol > 0) atmVols[tenor] = vol;
      });

      const riskReversals25D: Record<string, number> = {};
      tenors.forEach(tenor => {
        const rr = getValue(`EUR25R${tenor} Curncy`);
        if (rr !== 0) riskReversals25D[tenor] = rr;
      });

      const riskReversals10D: Record<string, number> = {};
      ['1M', '3M', '6M', '1Y'].forEach(tenor => {
        const rr = getValue(`EUR10R${tenor} Curncy`);
        if (rr !== 0) riskReversals10D[tenor] = rr;
      });

      const butterflies25D: Record<string, number> = {};
      tenors.forEach(tenor => {
        const bf = getValue(`EUR25B${tenor} Curncy`);
        if (bf !== 0) butterflies25D[tenor] = bf;
      });

      const butterflies10D: Record<string, number> = {};
      ['1M', '3M', '6M', '1Y'].forEach(tenor => {
        const bf = getValue(`EUR10B${tenor} Curncy`);
        if (bf !== 0) butterflies10D[tenor] = bf;
      });

      return {
        pair,
        spot,
        atmVols,
        riskReversals25D,
        riskReversals10D,
        butterflies25D,
        butterflies10D,
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      console.error('Bloomberg API error:', error);
      throw error;
    }
  }
};