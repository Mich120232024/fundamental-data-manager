import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { VirtualizedPriceListStandalone } from './VirtualizedPriceListStandalone';
import { AnalyticsPanel } from './CompoundAnalyticsPanel';
import { FilterAwareAnalyticsContainer } from './FilterAwareAnalyticsContainer';
import { theme } from '../../theme';

// Custom hook for real-time data simulation
const useRealtimeMetrics = (symbol: string) => {
  const [metrics, setMetrics] = useState({
    price: 1.0852,
    volume: 2453000,
    high: 1.0875,
    low: 1.0823,
    vwap: 1.0845
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        price: prev.price + (Math.random() - 0.5) * 0.0005,
        volume: prev.volume + Math.floor(Math.random() * 10000),
        high: Math.max(prev.high, prev.price),
        low: Math.min(prev.low, prev.price),
        vwap: prev.vwap + (Math.random() - 0.5) * 0.0001
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, [symbol]);

  return metrics;
};

// Main Analytics Dashboard Example
export const AnalyticsDashboardExample: React.FC = () => {
  const eurMetrics = useRealtimeMetrics('EUR/USD');
  const gbpMetrics = useRealtimeMetrics('GBP/USD');

  // Calculate derived metrics
  const marketMetrics = useMemo(() => [
    { 
      label: 'Total Volume', 
      value: ((eurMetrics.volume + gbpMetrics.volume) / 1000000).toFixed(2) + 'M',
      change: 12.5,
      trend: 'up' as const
    },
    { 
      label: 'Avg Spread', 
      value: '0.00012',
      change: -2.3,
      trend: 'down' as const
    },
    { 
      label: 'Market Volatility', 
      value: '14.2%',
      change: 8.7,
      trend: 'up' as const
    },
    { 
      label: 'Open Positions', 
      value: '247',
      change: 0,
      trend: 'neutral' as const
    }
  ], [eurMetrics.volume, gbpMetrics.volume]);

  const orderBookData = useMemo(() => 
    Array.from({ length: 10 }, (_, i) => ({
      price: (1.0850 + i * 0.0001).toFixed(5),
      bidSize: Math.floor(Math.random() * 1000),
      askSize: Math.floor(Math.random() * 1000),
      spread: '0.00002'
    })), 
    []
  );

  return (
    <div style={{ 
      padding: '20px',
      background: theme.background,
      minHeight: '100vh',
      position: 'relative'
    }}>
      <motion.h2 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ 
          fontSize: '20px', 
          fontWeight: '600', 
          color: theme.text,
          marginBottom: '20px' 
        }}
      >
        Analytics Dashboard Example
      </motion.h2>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: '16px',
          marginBottom: '16px'
        }}>
          {/* EUR/USD Analysis Panel */}
          <AnalyticsPanel defaultExpanded={true}>
            <AnalyticsPanel.Header 
              title="EUR/USD Analysis" 
              subtitle="Real-time market data"
              actions={
                <motion.div
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: theme.success
                  }}
                />
              }
            />
            <AnalyticsPanel.Body
              minimalContent={
                <AnalyticsPanel.MinimalView>
                  <AnalyticsPanel.MiniMetric 
                    label="Price" 
                    value={eurMetrics.price.toFixed(5)} 
                    trend="up"
                  />
                  <AnalyticsPanel.MiniMetric 
                    label="24h High" 
                    value={eurMetrics.high.toFixed(5)}
                    color={theme.success}
                  />
                  <AnalyticsPanel.MiniMetric 
                    label="24h Low" 
                    value={eurMetrics.low.toFixed(5)}
                    color={theme.danger}
                  />
                  <AnalyticsPanel.MiniMetric 
                    label="Volume" 
                    value={(eurMetrics.volume / 1000000).toFixed(2) + 'M'}
                  />
                  <AnalyticsPanel.MiniMetric 
                    label="VWAP" 
                    value={eurMetrics.vwap.toFixed(5)}
                  />
                  <div style={{ 
                    marginLeft: 'auto',
                    fontSize: '10px',
                    color: theme.textSecondary,
                    fontStyle: 'italic'
                  }}>
                    Click header to expand
                  </div>
                </AnalyticsPanel.MinimalView>
              }
            >
              <AnalyticsPanel.MetricGrid 
                metrics={[
                  { label: 'Current Price', value: eurMetrics.price.toFixed(5), change: 0.12 },
                  { label: 'Daily High', value: eurMetrics.high.toFixed(5) },
                  { label: 'Daily Low', value: eurMetrics.low.toFixed(5) },
                  { label: 'VWAP', value: eurMetrics.vwap.toFixed(5) }
                ]}
              />
              <AnalyticsPanel.Chart type="candlestick" height={250} />
            </AnalyticsPanel.Body>
          </AnalyticsPanel>

          {/* Market Overview Panel */}
          <AnalyticsPanel defaultExpanded={false}>
            <AnalyticsPanel.Header 
              title="Market Overview" 
              subtitle="Cross-pair analytics"
            />
            <AnalyticsPanel.Body
              minimalContent={
                <AnalyticsPanel.MinimalView>
                  <AnalyticsPanel.MiniMetric 
                    label="Total Vol" 
                    value={((eurMetrics.volume + gbpMetrics.volume) / 1000000).toFixed(1) + 'M'} 
                    trend="up"
                  />
                  <AnalyticsPanel.MiniMetric 
                    label="Volatility" 
                    value="14.2%"
                    color={theme.warning}
                  />
                  <AnalyticsPanel.MiniMetric 
                    label="Positions" 
                    value="247"
                  />
                  <AnalyticsPanel.MiniMetric 
                    label="Avg Spread" 
                    value="0.00012"
                    trend="down"
                    color={theme.success}
                  />
                  <div style={{
                    display: 'flex',
                    gap: '4px',
                    marginLeft: 'auto'
                  }}>
                    {['EUR', 'GBP', 'JPY', 'CHF'].map(pair => (
                      <div
                        key={pair}
                        style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '2px',
                          background: Math.random() > 0.5 ? theme.success : theme.danger,
                          opacity: 0.8
                        }}
                        title={`${pair} ${Math.random() > 0.5 ? '↑' : '↓'}`}
                      />
                    ))}
                  </div>
                </AnalyticsPanel.MinimalView>
              }
            >
              <AnalyticsPanel.MetricGrid metrics={marketMetrics} />
              
              {/* Mini heat map */}
              <div style={{ marginTop: '16px' }}>
                <h4 style={{ fontSize: '12px', color: theme.text, marginBottom: '8px' }}>
                  Correlation Matrix
                </h4>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(4, 1fr)',
                  gap: '4px'
                }}>
                  {Array.from({ length: 16 }, (_, i) => {
                    const correlation = Math.random() * 2 - 1;
                    const intensity = Math.abs(correlation);
                    return (
                      <motion.div
                        key={i}
                        whileHover={{ scale: 1.1 }}
                        style={{
                          aspectRatio: '1',
                          background: correlation > 0 
                            ? `rgba(171, 211, 143, ${intensity})` 
                            : `rgba(221, 139, 139, ${intensity})`,
                          borderRadius: '4px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '10px',
                          color: theme.text,
                          cursor: 'pointer'
                        }}
                      >
                        {correlation.toFixed(2)}
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            </AnalyticsPanel.Body>
          </AnalyticsPanel>
        </div>

        {/* Order Book Panel */}
        <AnalyticsPanel>
          <AnalyticsPanel.Header 
            title="Order Book" 
            subtitle="Level 2 Market Data"
          />
          <AnalyticsPanel.Body padding="0">
            <AnalyticsPanel.Table
              columns={['Price', 'Bid Size', 'Ask Size', 'Spread']}
              data={orderBookData}
            />
          </AnalyticsPanel.Body>
        </AnalyticsPanel>

        {/* Horizontal Scrollable Analytics Section with Filters */}
        <FilterAwareAnalyticsContainer />

        {/* Virtualized Price Feed */}
        <div style={{ marginTop: '16px' }}>
          <VirtualizedPriceListStandalone />
        </div>

        {/* Performance Metrics */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          style={{
            marginTop: '20px',
            padding: '12px',
            background: theme.surfaceAlt,
            borderRadius: '8px',
            fontSize: '11px',
            color: theme.textSecondary,
            textAlign: 'center'
          }}
        >
          This dashboard demonstrates: Shared Filter Context • Virtualization (10K items) • 
          Compound Components • Real-time Updates • Memoization • Responsive Grid
        </motion.div>
      </div>
  );
};