import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { theme } from '../theme';

// FX Position interface
interface FXPosition {
  currency_pair: string;
  trader: string;
  counter_party_code: string;
  net_position: number;
  trade_count: number;
  weighted_avg_rate: number;
  last_trade_date: string;
  first_trade_date: string;
  active_trades: number;
  total_volume: number;
  position_status: 'LONG' | 'SHORT' | 'FLAT';
}

interface PositionSummary {
  total_positions: number;
  long_positions: number;
  short_positions: number;
  total_volume: number;
  unique_pairs: number;
  unique_traders: number;
}

interface PositionsResponse {
  as_of_date: string;
  summary: PositionSummary;
  positions: FXPosition[];
}

export const FXPositionsComponent: React.FC = () => {
  const [positionsData, setPositionsData] = useState<PositionsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFund, setSelectedFund] = useState<string>('all');
  const [selectedTrader, setSelectedTrader] = useState<string>('all');
  const [groupBy, setGroupBy] = useState<'pair' | 'trader'>('pair');

  // Fetch FX Positions from API
  const fetchFXPositions = async () => {
    try {
      let url = '/api/fx-positions';
      const params = new URLSearchParams();
      
      if (selectedFund !== 'all') {
        params.append('fund_id', selectedFund);
      }
      
      if (selectedTrader !== 'all') {
        params.append('trader', selectedTrader);
      }
      
      if (params.toString()) {
        url += '?' + params.toString();
      }

      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: PositionsResponse = await response.json();
      setPositionsData(data);
    } catch (err) {
      console.error('Error fetching positions:', err);
      setError('Failed to fetch position data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFXPositions();
  }, [selectedFund, selectedTrader]);

  const formatNumber = (num: number, decimals = 0) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(num);
  };

  const formatRate = (rate: number, pair: string) => {
    const decimals = pair.includes('JPY') ? 2 : 4;
    return rate.toFixed(decimals);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'LONG': return theme.success;
      case 'SHORT': return theme.danger;
      case 'FLAT': return theme.textSecondary;
      default: return theme.text;
    }
  };

  // Group positions by currency pair or trader
  const groupPositions = (positions: FXPosition[]) => {
    if (groupBy === 'pair') {
      const grouped: { [key: string]: { net: number, count: number, volume: number } } = {};
      
      positions.forEach(pos => {
        if (!grouped[pos.currency_pair]) {
          grouped[pos.currency_pair] = { net: 0, count: 0, volume: 0 };
        }
        grouped[pos.currency_pair].net += pos.net_position;
        grouped[pos.currency_pair].count += pos.trade_count;
        grouped[pos.currency_pair].volume += pos.total_volume;
      });
      
      return Object.entries(grouped).map(([pair, data]) => ({
        key: pair,
        net_position: data.net,
        trade_count: data.count,
        total_volume: data.volume,
        position_status: data.net > 0 ? 'LONG' : data.net < 0 ? 'SHORT' : 'FLAT'
      }));
    } else {
      const grouped: { [key: string]: { net: number, count: number, volume: number } } = {};
      
      positions.forEach(pos => {
        if (!grouped[pos.trader]) {
          grouped[pos.trader] = { net: 0, count: 0, volume: 0 };
        }
        grouped[pos.trader].net += pos.net_position;
        grouped[pos.trader].count += pos.trade_count;
        grouped[pos.trader].volume += pos.total_volume;
      });
      
      return Object.entries(grouped).map(([trader, data]) => ({
        key: trader,
        net_position: data.net,
        trade_count: data.count,
        total_volume: data.volume,
        position_status: data.net > 0 ? 'LONG' : data.net < 0 ? 'SHORT' : 'FLAT'
      }));
    }
  };

  if (loading) {
    return (
      <div style={{
        background: theme.surface,
        borderRadius: '8px',
        padding: '24px',
        border: `1px solid ${theme.border}`,
        textAlign: 'center'
      }}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          style={{
            width: '24px',
            height: '24px',
            borderRadius: '50%',
            border: `3px solid ${theme.border}`,
            borderTop: `3px solid ${theme.primary}`,
            margin: '0 auto 16px'
          }}
        />
        <div style={{ color: theme.textSecondary, fontSize: '14px' }}>
          Calculating Positions...
        </div>
      </div>
    );
  }

  if (error || !positionsData) {
    return (
      <div style={{
        background: theme.surface,
        borderRadius: '8px',
        padding: '24px',
        border: `1px solid ${theme.danger}`,
        textAlign: 'center'
      }}>
        <div style={{ color: theme.danger, fontSize: '14px' }}>
          ❌ {error || 'No data available'}
        </div>
        <button
          onClick={fetchFXPositions}
          style={{
            background: theme.primary,
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            padding: '8px 16px',
            marginTop: '12px',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  const groupedPositions = groupPositions(positionsData.positions);

  return (
    <div style={{
      background: theme.surface,
      borderRadius: '8px',
      padding: '20px',
      border: `1px solid ${theme.border}`,
      height: '100%',
      overflow: 'auto'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
        borderBottom: `1px solid ${theme.border}`,
        paddingBottom: '16px'
      }}>
        <div>
          <h2 style={{
            color: theme.text,
            fontSize: '18px',
            fontWeight: '600',
            margin: '0 0 4px 0'
          }}>
            FX Positions Analysis
          </h2>
          <div style={{
            color: theme.textSecondary,
            fontSize: '12px'
          }}>
            GZCDB Position Calculation • {positionsData.summary.total_positions} positions • {positionsData.summary.unique_pairs} pairs
          </div>
        </div>
        
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          {/* Fund Filter */}
          <select
            value={selectedFund}
            onChange={(e) => setSelectedFund(e.target.value)}
            style={{
              background: theme.surfaceAlt,
              color: theme.text,
              border: `1px solid ${theme.border}`,
              borderRadius: '4px',
              padding: '6px 12px',
              fontSize: '11px',
              cursor: 'pointer'
            }}
          >
            <option value="all">All Funds</option>
            <option value="1">GMF</option>
            <option value="6">GCF</option>
          </select>

          {/* Group By */}
          <select
            value={groupBy}
            onChange={(e) => setGroupBy(e.target.value as 'pair' | 'trader')}
            style={{
              background: theme.surfaceAlt,
              color: theme.text,
              border: `1px solid ${theme.border}`,
              borderRadius: '4px',
              padding: '6px 12px',
              fontSize: '11px',
              cursor: 'pointer'
            }}
          >
            <option value="pair">By Currency Pair</option>
            <option value="trader">By Trader</option>
          </select>
          
          <motion.div
            animate={{ 
              backgroundColor: [theme.success, theme.primary, theme.success]
            }}
            transition={{ duration: 2, repeat: Infinity }}
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%'
            }}
          />
          <span style={{ color: theme.textSecondary, fontSize: '10px' }}>
            Live Calculation
          </span>
        </div>
      </div>

      {/* Summary Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '12px',
        marginBottom: '20px'
      }}>
        <div style={{
          background: theme.surfaceAlt,
          borderRadius: '6px',
          padding: '12px',
          border: `1px solid ${theme.border}`
        }}>
          <div style={{ color: theme.textSecondary, fontSize: '10px', marginBottom: '4px' }}>
            TOTAL VOLUME
          </div>
          <div style={{ color: theme.text, fontSize: '16px', fontWeight: '600' }}>
            {formatNumber(positionsData.summary.total_volume)}
          </div>
        </div>

        <div style={{
          background: theme.surfaceAlt,
          borderRadius: '6px',
          padding: '12px',
          border: `1px solid ${theme.border}`
        }}>
          <div style={{ color: theme.textSecondary, fontSize: '10px', marginBottom: '4px' }}>
            LONG POSITIONS
          </div>
          <div style={{ 
            color: theme.success,
            fontSize: '16px', 
            fontWeight: '600' 
          }}>
            {positionsData.summary.long_positions}
          </div>
        </div>

        <div style={{
          background: theme.surfaceAlt,
          borderRadius: '6px',
          padding: '12px',
          border: `1px solid ${theme.border}`
        }}>
          <div style={{ color: theme.textSecondary, fontSize: '10px', marginBottom: '4px' }}>
            SHORT POSITIONS
          </div>
          <div style={{ 
            color: theme.danger,
            fontSize: '16px', 
            fontWeight: '600' 
          }}>
            {positionsData.summary.short_positions}
          </div>
        </div>

        <div style={{
          background: theme.surfaceAlt,
          borderRadius: '6px',
          padding: '12px',
          border: `1px solid ${theme.border}`
        }}>
          <div style={{ color: theme.textSecondary, fontSize: '10px', marginBottom: '4px' }}>
            UNIQUE TRADERS
          </div>
          <div style={{ color: theme.text, fontSize: '16px', fontWeight: '600' }}>
            {positionsData.summary.unique_traders}
          </div>
        </div>
      </div>

      {/* Grouped Positions Table */}
      <div style={{
        background: theme.background,
        borderRadius: '6px',
        border: `1px solid ${theme.border}`,
        overflow: 'hidden'
      }}>
        {/* Table Header */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '200px 150px 100px 150px',
          gap: '8px',
          padding: '12px',
          background: theme.surfaceAlt,
          borderBottom: `1px solid ${theme.border}`,
          fontSize: '10px',
          fontWeight: '600',
          color: theme.textSecondary
        }}>
          <div>{groupBy === 'pair' ? 'CURRENCY PAIR' : 'TRADER'}</div>
          <div>NET POSITION</div>
          <div>TRADES</div>
          <div>TOTAL VOLUME</div>
        </div>

        {/* Table Rows */}
        {groupedPositions
          .sort((a, b) => Math.abs(b.net_position) - Math.abs(a.net_position))
          .slice(0, 20)
          .map((group, index) => (
            <motion.div
              key={group.key}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              style={{
                display: 'grid',
                gridTemplateColumns: '200px 150px 100px 150px',
                gap: '8px',
                padding: '12px',
                borderBottom: index < groupedPositions.length - 1 ? `1px solid ${theme.border}` : 'none',
                fontSize: '11px',
                color: theme.text,
                cursor: 'pointer',
                transition: 'background-color 0.2s ease'
              }}
              whileHover={{
                backgroundColor: theme.surfaceAlt
              }}
            >
              <div style={{ fontWeight: '600' }}>{group.key}</div>
              <div style={{
                color: getStatusColor(group.position_status),
                fontWeight: '600'
              }}>
                {formatNumber(group.net_position)}
              </div>
              <div>{formatNumber(group.trade_count)}</div>
              <div>{formatNumber(group.total_volume)}</div>
            </motion.div>
          ))}
      </div>

      {/* Detailed Positions */}
      {positionsData.positions.length > 0 && (
        <>
          <h3 style={{
            color: theme.text,
            fontSize: '14px',
            fontWeight: '600',
            margin: '20px 0 12px 0'
          }}>
            Detailed Positions (Top 10 by Size)
          </h3>
          
          <div style={{
            background: theme.background,
            borderRadius: '6px',
            border: `1px solid ${theme.border}`,
            overflow: 'hidden'
          }}>
            {/* Detailed Header */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: '120px 60px 100px 120px 100px 80px 100px',
              gap: '8px',
              padding: '12px',
              background: theme.surfaceAlt,
              borderBottom: `1px solid ${theme.border}`,
              fontSize: '10px',
              fontWeight: '600',
              color: theme.textSecondary
            }}>
              <div>PAIR</div>
              <div>TRADER</div>
              <div>COUNTERPARTY</div>
              <div>NET POSITION</div>
              <div>AVG RATE</div>
              <div>TRADES</div>
              <div>LAST TRADE</div>
            </div>

            {/* Detailed Rows */}
            {positionsData.positions
              .slice(0, 10)
              .map((pos, index) => (
                <motion.div
                  key={`${pos.currency_pair}-${pos.trader}-${pos.counter_party_code}`}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.05 }}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '120px 60px 100px 120px 100px 80px 100px',
                    gap: '8px',
                    padding: '12px',
                    borderBottom: index < 9 ? `1px solid ${theme.border}` : 'none',
                    fontSize: '11px',
                    color: theme.text
                  }}
                >
                  <div style={{ fontWeight: '600' }}>{pos.currency_pair}</div>
                  <div>{pos.trader}</div>
                  <div style={{ fontSize: '10px', color: theme.textSecondary }}>
                    {pos.counter_party_code}
                  </div>
                  <div style={{
                    color: getStatusColor(pos.position_status),
                    fontWeight: '600'
                  }}>
                    {formatNumber(pos.net_position)}
                  </div>
                  <div>{formatRate(pos.weighted_avg_rate, pos.currency_pair)}</div>
                  <div>{pos.trade_count}</div>
                  <div style={{ fontSize: '10px', color: theme.textSecondary }}>
                    {new Date(pos.last_trade_date).toLocaleDateString()}
                  </div>
                </motion.div>
              ))}
          </div>
        </>
      )}

      {/* Footer */}
      <div style={{
        marginTop: '16px',
        padding: '12px',
        background: theme.surfaceAlt,
        borderRadius: '6px',
        border: `1px solid ${theme.border}`,
        fontSize: '10px',
        color: theme.textSecondary,
        textAlign: 'center'
      }}>
        📊 Position Calculation: Net = SUM(BUY) - SUM(SELL) • 🔄 Updated: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};