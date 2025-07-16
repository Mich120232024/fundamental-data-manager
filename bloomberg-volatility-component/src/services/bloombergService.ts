// Bloomberg FX Volatility API Service - REAL DATA ONLY
import type { VolatilityData } from '../types/bloomberg';
import { STRIKES } from '../types/bloomberg';

const API_BASE = '/api';
const API_TOKEN = import.meta.env.VITE_BLOOMBERG_API_TOKEN || 'test';

// All available tenors from the API (based on health endpoint)
const API_TENORS = ['1W', '2W', '1M', '2M', '3M', '6M', '9M', '1Y', '2Y'];


export async function fetchVolatilitySurface(pair: string = 'EURUSD'): Promise<VolatilityData> {
  try {
    // Get spot rate
    const ratesResponse = await fetch(`${API_BASE}/fx/rates/live`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_TOKEN}`
      },
      body: JSON.stringify({ currency_pairs: [pair] })
    });
    
    if (!ratesResponse.ok) {
      throw new Error(`Rates API error: ${ratesResponse.status}`);
    }
    
    const ratesData = await ratesResponse.json();
    console.log('Rates response:', ratesData);
    
    // Get volatility surface - all tenors
    const volResponse = await fetch(`${API_BASE}/fx/volatility/live`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_TOKEN}`
      },
      body: JSON.stringify({ 
        currency_pairs: [pair],
        tenors: API_TENORS
      })
    });
    
    if (!volResponse.ok) {
      throw new Error(`Volatility API error: ${volResponse.status}`);
    }
    
    const volData = await volResponse.json();
    console.log('Volatility response:', volData);
    console.log('Volatility data structure:', JSON.stringify(volData, null, 2));
    
    // Transform API response to our format
    return transformApiData(pair, ratesData, volData);
  } catch (error) {
    console.error('Failed to fetch volatility surface:', error);
    throw error;
  }
}

function transformApiData(_pair: string, ratesData: unknown, volData: unknown): VolatilityData {
  // Initialize structure with all strikes
  const result: VolatilityData = {
    spot: 0,
    atmVols: {},
    riskReversals: {
      '5D': {},
      '10D': {},
      '15D': {},
      '25D': {},
      '35D': {}
    },
    butterflies: {
      '5D': {},
      '10D': {},
      '15D': {},
      '25D': {},
      '35D': {}
    },
    timestamp: new Date()
  };
  
  // Extract spot rate
  const ratesResponse = ratesData as { success: boolean; data?: { raw_data?: Array<{ PX_LAST: string }> } };
  if (ratesResponse.success && ratesResponse.data?.raw_data?.length > 0) {
    result.spot = parseFloat(ratesResponse.data.raw_data[0].PX_LAST);
  }
  
  // Parse volatility data - handle various response formats
  const volResponse = volData as { success: boolean; data?: { raw_data?: Array<Record<string, unknown>>; volatility_surface?: unknown; volatilities?: unknown } };
  if (volResponse.success && volResponse.data) {
    console.log('Processing volatility data:', volResponse.data);
    
    // Check for raw_data like in rates response
    if (volResponse.data.raw_data) {
      console.log('Found raw_data array with', volResponse.data.raw_data.length, 'items');
      // Process raw data array
      volResponse.data.raw_data.forEach((item: Record<string, unknown>) => {
        console.log('Processing item:', item);
        // Extract tenor and values from security name
        const security = (item.security || '') as string;
        
        // Parse ATM vols (e.g., "EURUSDV1M Curncy")
        if (security.includes('V') && !security.includes('RR') && !security.includes('BF')) {
          const match = security.match(/V(\w+)\s+Curncy/);
          if (match) {
            const tenor = mapTenor(match[1]);
            result.atmVols[tenor] = parseFloat(String(item.PX_LAST || item.value || 0));
            console.log('Added ATM vol:', tenor, result.atmVols[tenor]);
          }
        }
        
        // Parse RR (e.g., "EUR25RR1M Curncy")
        if (security.includes('RR')) {
          const match = security.match(/(\d+)RR(\w+)\s+Curncy/);
          if (match) {
            const strike = `${match[1]}D`;
            const tenor = mapTenor(match[2]);
            if (result.riskReversals[strike as keyof typeof result.riskReversals]) {
              result.riskReversals[strike as keyof typeof result.riskReversals][tenor] = parseFloat(String(item.PX_LAST || item.value || 0));
            }
          }
        }
        
        // Parse BF (e.g., "EUR25BF1M Curncy")
        if (security.includes('BF')) {
          const match = security.match(/(\d+)BF(\w+)\s+Curncy/);
          if (match) {
            const strike = `${match[1]}D`;
            const tenor = mapTenor(match[2]);
            if (result.butterflies[strike as keyof typeof result.butterflies]) {
              result.butterflies[strike as keyof typeof result.butterflies][tenor] = parseFloat(String(item.PX_LAST || item.value || 0));
            }
          }
        }
      });
    } else {
      const volSurface = volResponse.data.volatility_surface || volResponse.data.volatilities || volResponse.data;
      
      // If the data is an array, convert to object
      if (Array.isArray(volSurface)) {
        volSurface.forEach((item: Record<string, unknown>) => {
          processVolatilityItem(item, result);
        });
      } else {
        // Process each tenor in the surface
        Object.entries(volSurface).forEach(([key, value]: [string, unknown]) => {
          processVolatilityEntry(key, value, result);
        });
      }
    }
  }
  
  return result;
}

function processVolatilityItem(item: Record<string, unknown>, result: VolatilityData) {
  const tenor = item.tenor as string;
  const mappedTenor = mapTenor(tenor);
  
  // ATM volatility
  if (item.atm !== undefined) {
    result.atmVols[mappedTenor] = item.atm as number;
  }
  
  // Risk Reversals and Butterflies
  STRIKES.forEach(strike => {
    const strikeNum = strike.replace('D', '');
    
    if (item[`rr${strikeNum}`] !== undefined) {
      result.riskReversals[strike][mappedTenor] = item[`rr${strikeNum}`] as number;
    }
    
    if (item[`bf${strikeNum}`] !== undefined) {
      result.butterflies[strike][mappedTenor] = item[`bf${strikeNum}`] as number;
    }
  });
}

function processVolatilityEntry(key: string, value: unknown, result: VolatilityData) {
  // Check if key is a tenor
  const mappedTenor = mapTenor(key);
  
  if (typeof value === 'object' && value !== null) {
    const valueObj = value as Record<string, unknown>;
    // Process ATM
    if (valueObj.ATM !== undefined || valueObj.atm !== undefined) {
      result.atmVols[mappedTenor] = (valueObj.ATM || valueObj.atm) as number;
    }
    
    // Process Risk Reversals and Butterflies
    STRIKES.forEach(strike => {
      const strikeNum = strike.replace('D', '');
      
      // Try various naming conventions
      const rrKeys = [`${strikeNum}RR`, `rr${strikeNum}`, `RR${strikeNum}`];
      const bfKeys = [`${strikeNum}BF`, `bf${strikeNum}`, `BF${strikeNum}`];
      
      for (const rrKey of rrKeys) {
        if (valueObj[rrKey] !== undefined) {
          result.riskReversals[strike][mappedTenor] = valueObj[rrKey] as number;
          break;
        }
      }
      
      for (const bfKey of bfKeys) {
        if (valueObj[bfKey] !== undefined) {
          result.butterflies[strike][mappedTenor] = valueObj[bfKey] as number;
          break;
        }
      }
    });
  }
}

// Map API tenor format to display format
function mapTenor(tenor: string): string {
  // Handle overnight tenors
  if (tenor === 'ON' || tenor === 'O/N') return 'O/N';
  if (tenor === 'TN' || tenor === 'T/N') return 'T/N';
  
  // Standard tenors
  const tenorMap: Record<string, string> = {
    '1W': '1W',
    '2W': '2W',
    '3W': '3W',
    '1M': '1M',
    '2M': '2M',
    '3M': '3M',
    '4M': '4M',
    '5M': '5M',
    '6M': '6M',
    '9M': '9M',
    '1Y': '1Y',
    '18M': '18M',
    '2Y': '2Y',
    '3Y': '3Y',
    '5Y': '5Y'
  };
  
  return tenorMap[tenor] || tenor;
}