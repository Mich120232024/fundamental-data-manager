import React, { useState, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { theme } from '../../theme';

interface PriceData {
  id: string;
  time: number;
  symbol: string;
  bid: number;
  ask: number;
  volume: number;
  change: number;
}

// Generate mock data for demonstration
const generateMockData = (count: number): PriceData[] => {
  const currencies = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD'];
  return Array.from({ length: count }, (_, i) => ({
    id: `price-${i}`,
    time: Date.now() - (count - i) * 1000,
    symbol: currencies[Math.floor(Math.random() * currencies.length)],
    bid: 1.0800 + Math.random() * 0.01,
    ask: 1.0805 + Math.random() * 0.01,
    volume: Math.floor(Math.random() * 1000000),
    change: (Math.random() - 0.5) * 0.005
  }));
};

export const VirtualizedPriceListStandalone: React.FC = () => {
  const [scrollTop, setScrollTop] = useState(0);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const ITEM_HEIGHT = 40;
  const CONTAINER_HEIGHT = 400;
  
  // Generate large dataset
  const allData = useMemo(() => generateMockData(10000), []);

  // Calculate visible items
  const visibleItems = useMemo(() => {
    const startIndex = Math.floor(scrollTop / ITEM_HEIGHT);
    const endIndex = Math.min(
      startIndex + Math.ceil(CONTAINER_HEIGHT / ITEM_HEIGHT) + 1,
      allData.length
    );
    
    return allData.slice(startIndex, endIndex).map((item, idx) => ({
      ...item,
      index: startIndex + idx
    }));
  }, [allData, scrollTop]);

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  };

  return (
    <div style={{
      background: theme.surface,
      borderRadius: '8px',
      border: `1px solid ${theme.border}`,
      overflow: 'hidden'
    }}>
      <div 
        onClick={() => setIsCollapsed(!isCollapsed)}
        style={{
          background: theme.surfaceAlt,
          padding: '10px 14px',
          borderBottom: `1px solid ${theme.border}`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer'
        }}
      >
        <span style={{ fontSize: '12px', fontWeight: '500' }}>
          VIRTUALIZED PRICE FEED ({allData.length.toLocaleString()} items)
        </span>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <span style={{ fontSize: '10px', color: theme.textSecondary }}>
            Real-time streaming
          </span>
          <span style={{ fontSize: '11px', color: theme.success }}>
            Rendering {visibleItems.length} items
          </span>
          {/* Collapse/Expand arrow */}
          <motion.svg
            animate={{ rotate: isCollapsed ? 180 : 0 }}
            transition={{ duration: 0.2 }}
            width="14"
            height="14"
            viewBox="0 0 14 14"
            fill="none"
            style={{ marginLeft: '8px' }}
          >
            <path
              d="M3 5L7 9L11 5"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </motion.svg>
        </div>
      </div>

      <AnimatePresence initial={false}>
        {!isCollapsed && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            style={{ overflow: 'hidden' }}
          >
            {/* Header */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: '120px 100px 100px 100px 80px',
              gap: '8px',
              padding: '8px 14px',
              background: theme.surfaceAlt,
              fontSize: '10px',
              fontWeight: '600',
              color: theme.textSecondary,
              textTransform: 'uppercase',
              borderBottom: `1px solid ${theme.border}`
            }}>
              <div>Time</div>
              <div>Symbol</div>
              <div>Bid/Ask</div>
              <div>Volume</div>
              <div>Change</div>
            </div>

            {/* Virtualized List */}
            <div
              ref={containerRef}
              onScroll={handleScroll}
              style={{
                height: CONTAINER_HEIGHT,
                overflow: 'auto',
                position: 'relative'
              }}
            >
              <div style={{ height: allData.length * ITEM_HEIGHT }}>
                {visibleItems.map(item => (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    style={{
                      position: 'absolute',
                      top: item.index * ITEM_HEIGHT,
                      left: 0,
                      right: 0,
                      height: ITEM_HEIGHT,
                      display: 'grid',
                      gridTemplateColumns: '120px 100px 100px 100px 80px',
                      gap: '8px',
                      padding: '0 14px',
                      alignItems: 'center',
                      borderBottom: `1px solid ${theme.border}20`,
                      fontSize: '11px'
                    }}
                  >
                    <div style={{ color: theme.textSecondary, fontSize: '10px' }}>
                      {new Date(item.time).toLocaleTimeString()}
                    </div>
                    <div style={{ fontWeight: '500', color: theme.text }}>
                      {item.symbol}
                    </div>
                    <div>
                      <span style={{ color: theme.danger }}>{item.bid.toFixed(5)}</span>
                      {' / '}
                      <span style={{ color: theme.success }}>{item.ask.toFixed(5)}</span>
                    </div>
                    <div style={{ color: theme.textSecondary }}>
                      {(item.volume / 1000).toFixed(0)}K
                    </div>
                    <div style={{ 
                      color: item.change > 0 ? theme.success : theme.danger,
                      fontWeight: '500'
                    }}>
                      {item.change > 0 ? '+' : ''}{(item.change * 100).toFixed(2)}%
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};