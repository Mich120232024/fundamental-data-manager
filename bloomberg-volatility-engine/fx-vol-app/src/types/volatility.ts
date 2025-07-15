export interface VolatilitySurface {
  pair: string;
  timestamp: string;
  spot: {
    pair: string;
    spot: number;
    bid: number;
    ask: number;
    timestamp: string;
  };
  atmVols: Record<string, number>;
  riskReversals: Record<string, Record<string, number>>;
  butterflies: Record<string, Record<string, number>>;
}

export interface BloombergResponse {
  security: string;
  fields: {
    PX_LAST?: number;
    PX_MID?: number;
    PX_BID?: number;
    PX_ASK?: number;
  };
  timestamp: string;
  source: string;
}