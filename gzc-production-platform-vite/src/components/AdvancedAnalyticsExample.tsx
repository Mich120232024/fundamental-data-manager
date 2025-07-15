import React, { useState, useMemo, useCallback, createContext, useContext, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { theme } from '../theme';

// 1. SHARED FILTER CONTEXT PATTERN
interface FilterContextType {
  timeRange: { start: Date; end: Date };
  currencies: string[];
  aggregation: 'tick' | '1m' | '5m' | '1h' | '1d';
  updateFilter: (updates: Partial<FilterContextType>) => void;
}

const FilterContext = createContext<FilterContextType | null>(null);

export const useFilters = () => {
  const context = useContext(FilterContext);
  if (!context) throw new Error('useFilters must be used within FilterProvider');
  return context;
};

// 2. VIRTUALIZED TIME SERIES COMPONENT (for large datasets)
interface VirtualizedTimeSeriesProps {
  data: Array<{ time: number; value: number }>;
  height: number;
  itemHeight: number;
}

const VirtualizedTimeSeries: React.FC<VirtualizedTimeSeriesProps> = ({ data, height, itemHeight }) => {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  
  const visibleItems = useMemo(() => {
    const start = Math.floor(scrollTop / itemHeight);
    const end = Math.ceil((scrollTop + height) / itemHeight);
    return data.slice(start, end).map((item, idx) => ({
      ...item,
      index: start + idx
    }));
  }, [data, scrollTop, height, itemHeight]);

  return (
    <div 
      ref={containerRef}
      style={{ height, overflow: 'auto', position: 'relative' }}
      onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
    >
      <div style={{ height: data.length * itemHeight }}>
        {visibleItems.map(item => (
          <div
            key={item.index}
            style={{
              position: 'absolute',
              top: item.index * itemHeight,
              height: itemHeight,
              width: '100%'
            }}
          >
            {new Date(item.time).toLocaleTimeString()} - ${item.value.toFixed(2)}
          </div>
        ))}
      </div>
    </div>
  );
};

// 3. COMPOUND COMPONENT PATTERN (flexible composition)
interface AnalyticsPanelProps {
  children: React.ReactNode;
  title: string;
}

const AnalyticsPanel: React.FC<AnalyticsPanelProps> & {
  Header: typeof PanelHeader;
  Body: typeof PanelBody;
  Chart: typeof PanelChart;
  Metrics: typeof PanelMetrics;
} = ({ children, title }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  
  return (
    <motion.div
      layout
      style={{
        background: theme.surface,
        border: `1px solid ${theme.border}`,
        borderRadius: '8px',
        overflow: 'hidden'
      }}
    >
      {React.Children.map(children, child => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as React.ReactElement<any>, { isExpanded, setIsExpanded, title });
        }
        return child;
      })}
    </motion.div>
  );
};

const PanelHeader: React.FC<any> = ({ title, isExpanded, setIsExpanded, children }) => (
  <div style={{
    background: theme.surfaceAlt,
    padding: '10px 14px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    cursor: 'pointer'
  }} onClick={() => setIsExpanded(!isExpanded)}>
    <span style={{ fontSize: '13px', fontWeight: '600' }}>{title}</span>
    {children}
  </div>
);

const PanelBody: React.FC<any> = ({ isExpanded, children }) => (
  <AnimatePresence>
    {isExpanded && (
      <motion.div
        initial={{ height: 0 }}
        animate={{ height: 'auto' }}
        exit={{ height: 0 }}
        style={{ overflow: 'hidden' }}
      >
        {children}
      </motion.div>
    )}
  </AnimatePresence>
);

const PanelChart: React.FC<{ data: any }> = ({ data }) => (
  <div style={{ padding: '16px' }}>
    {/* Chart implementation */}
    Chart Component
  </div>
);

const PanelMetrics: React.FC<{ metrics: any }> = ({ metrics }) => (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px', padding: '16px' }}>
    {/* Metrics grid */}
  </div>
);

AnalyticsPanel.Header = PanelHeader;
AnalyticsPanel.Body = PanelBody;
AnalyticsPanel.Chart = PanelChart;
AnalyticsPanel.Metrics = PanelMetrics;

// 4. RENDER PROPS PATTERN (for flexible data rendering)
interface TimeSeriesRendererProps<T> {
  data: T[];
  loading: boolean;
  error: Error | null;
  children: (props: {
    data: T[];
    loading: boolean;
    error: Error | null;
    refetch: () => void;
  }) => React.ReactNode;
}

function TimeSeriesRenderer<T>({ data, loading, error, children }: TimeSeriesRendererProps<T>) {
  const refetch = useCallback(() => {
    // Refetch logic
  }, []);

  return <>{children({ data, loading, error, refetch })}</>;
}

// 5. OPTIMIZED MEMO PATTERN (for expensive computations)
interface AnalyticsData {
  raw: number[];
  timestamps: number[];
}

const ExpensiveAnalytics: React.FC<{ data: AnalyticsData }> = React.memo(({ data }) => {
  // Expensive calculations memoized
  const calculations = useMemo(() => {
    const mean = data.raw.reduce((a, b) => a + b, 0) / data.raw.length;
    const variance = data.raw.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.raw.length;
    const stdDev = Math.sqrt(variance);
    
    return { mean, variance, stdDev };
  }, [data.raw]);

  return (
    <div>
      <div>Mean: {calculations.mean.toFixed(2)}</div>
      <div>Std Dev: {calculations.stdDev.toFixed(2)}</div>
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison for re-rendering
  return prevProps.data.raw.length === nextProps.data.raw.length &&
         prevProps.data.raw[0] === nextProps.data.raw[0];
});

// 6. PORTAL PATTERN (for modals/tooltips)
const AnalyticsTooltip: React.FC<{ x: number; y: number; data: any }> = ({ x, y, data }) => {
  return ReactDOM.createPortal(
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      style={{
        position: 'fixed',
        left: x,
        top: y,
        background: theme.surface,
        border: `1px solid ${theme.border}`,
        borderRadius: '6px',
        padding: '8px',
        zIndex: 9999
      }}
    >
      {data.value}
    </motion.div>,
    document.body
  );
};

// 7. HOOK COMPOSITION PATTERN
const useTimeSeriesData = (symbol: string, interval: string) => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // WebSocket connection for real-time updates
    wsRef.current = new WebSocket(`ws://localhost:8080/stream/${symbol}`);
    
    wsRef.current.onmessage = (event) => {
      const newData = JSON.parse(event.data);
      setData(prev => [...prev.slice(-999), newData]); // Keep last 1000 points
    };

    return () => wsRef.current?.close();
  }, [symbol]);

  return { data, loading };
};

// 8. EXAMPLE USAGE - Advanced Analytics Dashboard
export const AdvancedAnalyticsDashboard: React.FC = () => {
  const [filters, setFilters] = useState<FilterContextType>({
    timeRange: { start: new Date(Date.now() - 86400000), end: new Date() },
    currencies: ['EUR/USD', 'GBP/USD'],
    aggregation: '1m',
    updateFilter: (updates) => setFilters(prev => ({ ...prev, ...updates }))
  });

  const { data: euroData } = useTimeSeriesData('EUR/USD', filters.aggregation);

  return (
    <FilterContext.Provider value={filters}>
      <div style={{ padding: '16px', display: 'grid', gap: '16px' }}>
        
        {/* Global Filter Bar */}
        <div style={{
          background: theme.surface,
          padding: '12px',
          borderRadius: '8px',
          display: 'flex',
          gap: '12px'
        }}>
          <select 
            value={filters.aggregation}
            onChange={(e) => filters.updateFilter({ aggregation: e.target.value as any })}
            style={{
              background: theme.surfaceAlt,
              border: `1px solid ${theme.border}`,
              borderRadius: '4px',
              padding: '6px',
              color: theme.text
            }}
          >
            <option value="tick">Tick</option>
            <option value="1m">1 Minute</option>
            <option value="5m">5 Minutes</option>
            <option value="1h">1 Hour</option>
          </select>
        </div>

        {/* Compound Component Usage */}
        <AnalyticsPanel title="EUR/USD Analysis">
          <AnalyticsPanel.Header>
            <span style={{ fontSize: '11px', color: theme.success }}>Live</span>
          </AnalyticsPanel.Header>
          <AnalyticsPanel.Body>
            <AnalyticsPanel.Metrics metrics={euroData} />
            <AnalyticsPanel.Chart data={euroData} />
          </AnalyticsPanel.Body>
        </AnalyticsPanel>

        {/* Render Props Pattern */}
        <TimeSeriesRenderer data={euroData} loading={false} error={null}>
          {({ data, loading, error, refetch }) => (
            <div>
              {loading && <div>Loading...</div>}
              {error && <div>Error: {error.message}</div>}
              {data && <VirtualizedTimeSeries data={data} height={300} itemHeight={30} />}
            </div>
          )}
        </TimeSeriesRenderer>

      </div>
    </FilterContext.Provider>
  );
};

// 9. PERFORMANCE TIPS:
/*
1. Use React.memo() for expensive components
2. useMemo() for expensive calculations
3. useCallback() for stable function references
4. Virtualization for large lists
5. Web Workers for heavy computations
6. RequestAnimationFrame for smooth animations
7. Intersection Observer for lazy loading
8. Debounce/throttle for frequent updates
*/

// 10. SHARED STATE PATTERNS:
/*
1. Context API for cross-component state
2. Zustand for lightweight global state
3. Redux Toolkit for complex state
4. Jotai for atomic state management
5. Valtio for proxy-based state
*/