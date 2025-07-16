// Bloomberg FX Volatility Surface Types

export interface VolatilityData {
  spot: number;
  atmVols: Record<string, number>;
  riskReversals: {
    '5D': Record<string, number>;
    '10D': Record<string, number>;
    '15D': Record<string, number>;
    '25D': Record<string, number>;
    '35D': Record<string, number>;
  };
  butterflies: {
    '5D': Record<string, number>;
    '10D': Record<string, number>;
    '15D': Record<string, number>;
    '25D': Record<string, number>;
    '35D': Record<string, number>;
  };
  timestamp: Date;
}

// All tenors from O/N to 5Y
export const TENORS = ['O/N', 'T/N', '1W', '2W', '3W', '1M', '2M', '3M', '4M', '5M', '6M', '9M', '1Y', '18M', '2Y', '3Y', '5Y'] as const;

// All strikes
export const STRIKES = ['5D', '10D', '15D', '25D', '35D'] as const;

export type Tenor = typeof TENORS[number];
export type Strike = typeof STRIKES[number];