import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { theme } from '../theme';

// Interfaces
interface FXForwardTrade {
  id: string;
  trade_date: string;
  value_date: string;
  currency_pair: string;
  notional: number;
  rate: number;
  market_rate: number;
  pnl: number;
  counterparty: string;
  status: string;
  trader: string;
}

interface FXPosition {
  currency_pair: string;
  net_position: number;
  trade_count: number;
  weighted_avg_rate: number;
  total_volume: number;
  last_trade_date: string;
  position_status: 'LONG' | 'SHORT' | 'FLAT';
}

interface PositionsSummary {
  total_positions: number;
  long_positions: number;
  short_positions: number;
  total_volume: number;
  unique_pairs: number;
}

export const GZCPortfolioComponent: React.FC = () => {
  const [viewMode, setViewMode] = useState<'trades' | 'positions'>('trades');
  const [trades, setTrades] = useState<FXForwardTrade[]>([]);
  const [positions, setPositions] = useState<FXPosition[]>([]);
  const [positionsSummary, setPositionsSummary] = useState<PositionsSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFund, setSelectedFund] = useState<string>('6'); // GCF default
  const [isActive, setIsActive] = useState(true); // true = active, false = closed/inactive

  // Fetch trades
  const fetchTrades = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams();
      if (selectedFund !== 'all') {
        params.append('fund_id', selectedFund);
      }
      params.append('active_status', isActive ? 'active' : 'inactive');

      const response = await fetch(`/api/fx-forward-trades?${params}`);
      if (!response.ok) throw new Error('Failed to fetch trades');
      
      const data = await response.json();
      setTrades(data.trades || []);
    } catch (err) {
      console.error('Error fetching trades:', err);
      setError('Failed to fetch trades');
    } finally {
      setLoading(false);
    }
  };

  // Fetch aggregated positions
  const fetchPositions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams();
      if (selectedFund !== 'all') {
        params.append('fund_id', selectedFund);
      }
      params.append('active_status', isActive ? 'active' : 'inactive');

      const response = await fetch(`/api/fx-positions-aggregated?${params}`);
      if (!response.ok) throw new Error('Failed to fetch positions');
      
      const data = await response.json();
      setPositions(data.positions || []);
      setPositionsSummary(data.summary || null);
    } catch (err) {
      console.error('Error fetching positions:', err);
      setError('Failed to fetch positions');
    } finally {
      setLoading(false);
    }
  };

  // Fetch data based on view mode
  useEffect(() => {
    if (viewMode === 'trades') {
      fetchTrades();
    } else {
      fetchPositions();
    }
  }, [viewMode, selectedFund, isActive]);

  // Format helpers
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatRate = (rate: number, pair: string) => {
    if (!rate) return '-';
    const decimals = pair?.includes('JPY') ? 2 : 4;
    return rate.toFixed(decimals);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(Math.round(num));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return theme.success;
      case 'LONG': return theme.success;
      case 'SHORT': return theme.danger;
      case 'FLAT': return theme.textSecondary;
      default: return theme.textSecondary;
    }
  };

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
            margin: 0
          }}>
            GZC Portfolio - {viewMode === 'trades' ? 'FX Forward Trades' : 'FX Positions'}
          </h2>
          <div style={{
            color: theme.textSecondary,
            fontSize: '12px',
            marginTop: '4px'
          }}>
            {viewMode === 'trades' 
              ? `${trades.length} trades • ${isActive ? 'Active' : 'Closed'} • ${selectedFund === 'all' ? 'All Funds' : selectedFund === '6' ? 'GCF' : 'GMF'}`
              : `${positions.length} positions • ${isActive ? 'Active' : 'Closed'} • ${selectedFund === 'all' ? 'All Funds' : selectedFund === '6' ? 'GCF' : 'GMF'}`
            }
          </div>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          {/* View Toggle */}
          <div style={{
            display: 'flex',
            background: theme.surfaceAlt,
            borderRadius: '4px',
            padding: '2px',
            border: `1px solid ${theme.border}`
          }}>
            <button
              onClick={() => setViewMode('trades')}
              disabled={loading}
              style={{
                background: viewMode === 'trades' ? theme.primary : 'transparent',
                color: viewMode === 'trades' ? 'white' : theme.text,
                border: 'none',
                borderRadius: '3px',
                padding: '4px 12px',
                fontSize: '11px',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                opacity: loading ? 0.7 : 1
              }}
            >
              Trades
            </button>
            <button
              onClick={() => setViewMode('positions')}
              disabled={loading}
              style={{
                background: viewMode === 'positions' ? theme.primary : 'transparent',
                color: viewMode === 'positions' ? 'white' : theme.text,
                border: 'none',
                borderRadius: '3px',
                padding: '4px 12px',
                fontSize: '11px',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                opacity: loading ? 0.7 : 1
              }}
            >
              Positions
            </button>
          </div>

          {/* Fund Filter */}
          <select
            value={selectedFund}
            onChange={(e) => setSelectedFund(e.target.value)}
            disabled={loading}
            style={{
              background: theme.surfaceAlt,
              color: theme.text,
              border: `1px solid ${theme.border}`,
              borderRadius: '4px',
              padding: '6px 12px',
              fontSize: '11px',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1
            }}
          >
            <option value="6">GCF</option>
            <option value="1">GMF</option>
            <option value="all">All Funds</option>
          </select>

          {/* Active/Closed Button */}
          <button
            onClick={() => setIsActive(!isActive)}
            disabled={loading}
            style={{
              background: theme.primary,
              color: 'white',
              border: `1px solid ${theme.border}`,
              borderRadius: '4px',
              padding: '6px 16px',
              fontSize: '11px',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s',
              opacity: loading ? 0.7 : 1,
              minWidth: '100px'
            }}
          >
            {isActive ? '📂 Active' : '📁 Closed'}
          </button>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              border: `3px solid ${theme.border}`,
              borderTop: `3px solid ${theme.primary}`,
              margin: '0 auto 16px'
            }}
          />
          <div style={{ color: theme.textSecondary, fontSize: '14px' }}>
            Loading {viewMode}...
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div style={{
          background: theme.surfaceAlt,
          border: `1px solid ${theme.danger}`,
          borderRadius: '4px',
          padding: '12px',
          color: theme.danger,
          marginBottom: '20px'
        }}>
          {error}
          <button
            onClick={() => viewMode === 'trades' ? fetchTrades() : fetchPositions()}
            style={{
              background: theme.danger,
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '4px 12px',
              marginLeft: '12px',
              fontSize: '11px',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Trades View */}
      {!loading && viewMode === 'trades' && trades.length > 0 && (
        <>
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
                TOTAL NOTIONAL
              </div>
              <div style={{ color: theme.text, fontSize: '16px', fontWeight: '600' }}>
                {formatCurrency(trades.reduce((sum, t) => sum + t.notional, 0))}
              </div>
            </div>

            <div style={{
              background: theme.surfaceAlt,
              borderRadius: '6px',
              padding: '12px',
              border: `1px solid ${theme.border}`
            }}>
              <div style={{ color: theme.textSecondary, fontSize: '10px', marginBottom: '4px' }}>
                TOTAL P&L
              </div>
              <div style={{ 
                color: trades.reduce((sum, t) => sum + t.pnl, 0) >= 0 ? theme.success : theme.danger,
                fontSize: '16px', 
                fontWeight: '600' 
              }}>
                {formatCurrency(trades.reduce((sum, t) => sum + t.pnl, 0))}
              </div>
            </div>

            <div style={{
              background: theme.surfaceAlt,
              borderRadius: '6px',
              padding: '12px',
              border: `1px solid ${theme.border}`
            }}>
              <div style={{ color: theme.textSecondary, fontSize: '10px', marginBottom: '4px' }}>
                ACTIVE TRADES
              </div>
              <div style={{ color: theme.text, fontSize: '16px', fontWeight: '600' }}>
                {trades.filter(t => t.status === 'ACTIVE').length}
              </div>
            </div>
          </div>

          {/* Trades Table */}
          <div style={{
            background: theme.background,
            borderRadius: '6px',
            border: `1px solid ${theme.border}`,
            overflow: 'hidden'
          }}>
            <div style={{
              display: 'grid',
              gridTemplateColumns: '80px 100px 120px 80px 80px 100px 100px 80px',
              gap: '12px',
              padding: '12px',
              background: theme.surfaceAlt,
              borderBottom: `1px solid ${theme.border}`,
              fontSize: '10px',
              fontWeight: '600',
              color: theme.textSecondary
            }}>
              <div>ID</div>
              <div>PAIR</div>
              <div>NOTIONAL</div>
              <div>RATE</div>
              <div>MARKET</div>
              <div>P&L</div>
              <div>COUNTERPARTY</div>
              <div>STATUS</div>
            </div>

            <div style={{ maxHeight: '400px', overflow: 'auto' }}>
              {trades.map((trade, index) => (
                <motion.div
                  key={trade.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.01 }}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '80px 100px 120px 80px 80px 100px 100px 80px',
                    gap: '12px',
                    padding: '12px',
                    borderBottom: index < trades.length - 1 ? `1px solid ${theme.border}` : 'none',
                    fontSize: '11px'
                  }}
                >
                  <div style={{ fontSize: '10px' }}>{trade.id}</div>
                  <div style={{ fontWeight: '600' }}>{trade.currency_pair}</div>
                  <div>{formatCurrency(trade.notional)}</div>
                  <div>{formatRate(trade.rate, trade.currency_pair)}</div>
                  <div>{formatRate(trade.market_rate, trade.currency_pair)}</div>
                  <div style={{
                    color: trade.pnl >= 0 ? theme.success : theme.danger,
                    fontWeight: '600'
                  }}>
                    {formatCurrency(trade.pnl)}
                  </div>
                  <div style={{ fontSize: '10px' }}>{trade.counterparty}</div>
                  <div>
                    <span style={{
                      color: getStatusColor(trade.status),
                      fontSize: '9px',
                      fontWeight: '600'
                    }}>
                      {trade.status}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Positions View */}
      {!loading && viewMode === 'positions' && positions.length > 0 && (
        <>
          {/* Summary Cards */}
          {positionsSummary && (
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
                  {formatCurrency(positionsSummary.total_volume)}
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
                  {positionsSummary.long_positions}
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
                  {positionsSummary.short_positions}
                </div>
              </div>
            </div>
          )}

          {/* Positions Table */}
          <div style={{
            background: theme.background,
            borderRadius: '6px',
            border: `1px solid ${theme.border}`,
            overflow: 'hidden'
          }}>
            <div style={{
              display: 'grid',
              gridTemplateColumns: '150px 150px 120px 100px 150px',
              gap: '12px',
              padding: '12px',
              background: theme.surfaceAlt,
              borderBottom: `1px solid ${theme.border}`,
              fontSize: '10px',
              fontWeight: '600',
              color: theme.textSecondary
            }}>
              <div>CURRENCY PAIR</div>
              <div>NET POSITION</div>
              <div>AVG RATE</div>
              <div>TRADES</div>
              <div>STATUS</div>
            </div>

            <div style={{ maxHeight: '400px', overflow: 'auto' }}>
              {positions.map((pos, index) => (
                <motion.div
                  key={pos.currency_pair}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.01 }}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '150px 150px 120px 100px 150px',
                    gap: '12px',
                    padding: '12px',
                    borderBottom: index < positions.length - 1 ? `1px solid ${theme.border}` : 'none',
                    fontSize: '11px'
                  }}
                >
                  <div style={{ fontWeight: '600' }}>{pos.currency_pair}</div>
                  <div style={{
                    color: getStatusColor(pos.position_status),
                    fontWeight: '600'
                  }}>
                    {formatNumber(pos.net_position)}
                  </div>
                  <div>{formatRate(pos.weighted_avg_rate, pos.currency_pair)}</div>
                  <div>{pos.trade_count}</div>
                  <div>
                    <span style={{
                      color: getStatusColor(pos.position_status),
                      fontSize: '10px',
                      fontWeight: '600'
                    }}>
                      {pos.position_status}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Empty State */}
      {!loading && !error && (
        (viewMode === 'trades' && trades.length === 0) || 
        (viewMode === 'positions' && positions.length === 0)
      ) && (
        <div style={{
          textAlign: 'center',
          padding: '60px',
          color: theme.textSecondary
        }}>
          <div style={{ fontSize: '16px', marginBottom: '8px' }}>
            No {isActive ? 'active' : 'closed'} {viewMode} found
          </div>
          <div style={{ fontSize: '12px' }}>
            Try changing the filters or toggling between active and closed
          </div>
        </div>
      )}
    </div>
  );
};