import React, { useState, ReactNode, createContext, useContext, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { theme } from '../../theme';

// Context for compound component communication
interface PanelContextType {
  isExpanded: boolean;
  setIsExpanded: (expanded: boolean) => void;
  isFullscreen: boolean;
  setIsFullscreen: (fullscreen: boolean) => void;
}

const PanelContext = createContext<PanelContextType | null>(null);

// Main compound component
interface AnalyticsPanelProps {
  children: ReactNode;
  defaultExpanded?: boolean;
}

export const AnalyticsPanel: React.FC<AnalyticsPanelProps> & {
  Header: typeof Header;
  Body: typeof Body;
  MetricGrid: typeof MetricGrid;
  Chart: typeof Chart;
  Table: typeof Table;
  MinimalView: typeof MinimalView;
  MiniMetric: typeof MiniMetric;
} = ({ children, defaultExpanded = true }) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [isFullscreen, setIsFullscreen] = useState(false);

  return (
    <PanelContext.Provider value={{ isExpanded, setIsExpanded, isFullscreen, setIsFullscreen }}>
      <motion.div
        layout
        animate={{
          scale: isFullscreen ? 1 : 1,
          opacity: 1
        }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        style={{
          background: theme.surface,
          border: `1px solid ${theme.border}`,
          borderRadius: '8px',
          overflow: 'hidden',
          position: isFullscreen ? 'fixed' : 'relative',
          inset: isFullscreen ? '20px' : 'auto',
          zIndex: isFullscreen ? 1000 : 'auto',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: isFullscreen ? `0 20px 60px ${theme.background}CC` : 'none'
        }}
      >
        {isFullscreen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              inset: 0,
              background: `${theme.background}EE`,
              zIndex: 999,
              backdropFilter: 'blur(4px)'
            }}
            onClick={() => setIsFullscreen(false)}
          />
        )}
        {children}
      </motion.div>
    </PanelContext.Provider>
  );
};

// Header component
const Header: React.FC<{ title: string; subtitle?: string; actions?: ReactNode }> = ({ 
  title, 
  subtitle, 
  actions 
}) => {
  const context = useContext(PanelContext);
  if (!context) throw new Error('Header must be used within AnalyticsPanel');
  
  const { isExpanded, setIsExpanded, isFullscreen, setIsFullscreen } = context;

  // Handle ESC key to exit fullscreen
  React.useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isFullscreen, setIsFullscreen]);

  return (
    <div style={{
      background: theme.surfaceAlt,
      padding: '12px 16px',
      borderBottom: `1px solid ${theme.border}`,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      cursor: 'pointer'
    }}>
      <div 
        onClick={() => !isFullscreen && setIsExpanded(!isExpanded)} 
        style={{ 
          flex: 1, 
          cursor: isFullscreen ? 'default' : 'pointer' 
        }}
      >
        <div style={{ fontSize: '11px', fontWeight: '500', color: theme.text }}>
          {title}
          {isFullscreen && (
            <span style={{ 
              fontSize: '9px', 
              color: theme.textSecondary, 
              marginLeft: '8px',
              fontWeight: '400'
            }}>
              (Press ESC to exit)
            </span>
          )}
        </div>
        {subtitle && (
          <div style={{ fontSize: '10px', color: theme.textSecondary, marginTop: '2px' }}>
            {subtitle}
          </div>
        )}
      </div>
      
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        {actions}
        <motion.button
          whileHover={{ 
            scale: 1.1,
            backgroundColor: `${theme.primary}20`
          }}
          whileTap={{ scale: 0.9 }}
          onClick={(e) => {
            e.stopPropagation();
            setIsFullscreen(!isFullscreen);
            // Auto-expand when maximizing
            if (!isFullscreen) {
              setIsExpanded(true);
            }
          }}
          style={{
            background: isFullscreen ? `${theme.primary}20` : 'transparent',
            border: `1px solid ${isFullscreen ? theme.primary : 'transparent'}`,
            borderRadius: '4px',
            color: isFullscreen ? theme.primary : theme.textSecondary,
            cursor: 'pointer',
            padding: '4px 8px',
            fontSize: '11px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            transition: 'all 0.2s ease'
          }}
          title={isFullscreen ? 'Exit Fullscreen' : 'Maximize'}
        >
          {isFullscreen ? (
            <>
              <span style={{ fontSize: '14px' }}>⊡</span>
              <span>Exit</span>
            </>
          ) : (
            <>
              <span style={{ fontSize: '14px' }}>⊞</span>
              <span>Max</span>
            </>
          )}
        </motion.button>
        {!isFullscreen && (
          <motion.div
            animate={{ rotate: isExpanded ? 0 : -90 }}
            style={{ color: theme.textSecondary, fontSize: '12px' }}
          >
            ▼
          </motion.div>
        )}
      </div>
    </div>
  );
};

// Body component with animation and minimal view
const Body: React.FC<{ 
  children: ReactNode; 
  padding?: string;
  minimalContent?: ReactNode;
}> = ({ 
  children, 
  padding = '16px',
  minimalContent 
}) => {
  const context = useContext(PanelContext);
  if (!context) throw new Error('Body must be used within AnalyticsPanel');
  
  const { isExpanded } = context;

  return (
    <>
      <AnimatePresence mode="wait">
        {isExpanded ? (
          <motion.div
            key="expanded"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            style={{ 
              overflow: 'hidden',
              flex: context.isFullscreen ? 1 : 'auto'
            }}
          >
            <div style={{ padding }}>
              {children}
            </div>
          </motion.div>
        ) : minimalContent ? (
          <motion.div
            key="minimal"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            style={{ overflow: 'hidden' }}
          >
            {minimalContent}
          </motion.div>
        ) : null}
      </AnimatePresence>
    </>
  );
};

// Metric Grid component
const MetricGrid: React.FC<{ 
  metrics: Array<{ 
    label: string; 
    value: string | number; 
    change?: number;
    trend?: 'up' | 'down' | 'neutral';
  }> 
}> = ({ metrics }) => {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
      gap: '12px',
      marginBottom: '16px'
    }}>
      {metrics.map((metric, index) => (
        <motion.div
          key={metric.label}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
          style={{
            background: theme.surfaceAlt,
            padding: '12px',
            borderRadius: '6px',
            border: `1px solid ${theme.border}`
          }}
        >
          <div style={{ fontSize: '10px', color: theme.textSecondary, marginBottom: '4px' }}>
            {metric.label}
          </div>
          <div style={{ fontSize: '16px', fontWeight: '600', color: theme.text }}>
            {metric.value}
          </div>
          {metric.change !== undefined && (
            <div style={{ 
              fontSize: '10px', 
              color: metric.change > 0 ? theme.success : theme.danger,
              marginTop: '4px' 
            }}>
              {metric.change > 0 ? '+' : ''}{metric.change}%
              {metric.trend && (
                <span style={{ marginLeft: '4px' }}>
                  {metric.trend === 'up' ? '↑' : metric.trend === 'down' ? '↓' : '→'}
                </span>
              )}
            </div>
          )}
        </motion.div>
      ))}
    </div>
  );
};

// Chart placeholder component
const Chart: React.FC<{ type: 'line' | 'bar' | 'candlestick'; height?: number }> = ({ 
  type, 
  height = 200 
}) => {
  return (
    <div style={{
      background: theme.surfaceAlt,
      borderRadius: '8px',
      height,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      border: `1px solid ${theme.border}`,
      color: theme.textSecondary,
      fontSize: '12px'
    }}>
      {type.charAt(0).toUpperCase() + type.slice(1)} Chart
    </div>
  );
};

// Table component
const Table: React.FC<{ 
  columns: string[]; 
  data: Array<Record<string, any>> 
}> = ({ columns, data }) => {
  return (
    <div style={{ 
      overflowX: 'auto',
      border: `1px solid ${theme.border}`,
      borderRadius: '6px'
    }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ background: theme.surfaceAlt }}>
            {columns.map(col => (
              <th key={col} style={{
                padding: '8px 12px',
                textAlign: 'left',
                fontSize: '11px',
                fontWeight: '600',
                color: theme.textSecondary,
                textTransform: 'uppercase',
                borderBottom: `1px solid ${theme.border}`
              }}>
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <motion.tr 
              key={idx}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: idx * 0.02 }}
              whileHover={{ backgroundColor: `${theme.primary}05` }}
              style={{ 
                borderBottom: `1px solid ${theme.border}20`,
                cursor: 'pointer'
              }}
            >
              {columns.map(col => (
                <td key={col} style={{
                  padding: '10px 12px',
                  fontSize: '11px',
                  color: theme.text
                }}>
                  {row[col]}
                </td>
              ))}
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Minimal view component for collapsed state
const MinimalView: React.FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <div style={{
      padding: '8px 16px',
      borderTop: `1px solid ${theme.border}`,
      background: theme.surface,
      display: 'flex',
      gap: '16px',
      alignItems: 'center',
      flexWrap: 'wrap'
    }}>
      {children}
    </div>
  );
};

// Mini metric component for minimal view
const MiniMetric: React.FC<{ 
  label: string; 
  value: string | number; 
  color?: string;
  trend?: 'up' | 'down' | 'neutral';
}> = ({ label, value, color, trend }) => {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
      <span style={{ fontSize: '10px', color: theme.textSecondary }}>
        {label}:
      </span>
      <span style={{ 
        fontSize: '11px', 
        fontWeight: '600', 
        color: color || theme.text 
      }}>
        {value}
      </span>
      {trend && (
        <span style={{ 
          fontSize: '10px',
          color: trend === 'up' ? theme.success : trend === 'down' ? theme.danger : theme.textSecondary
        }}>
          {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
        </span>
      )}
    </div>
  );
};

// Attach sub-components
AnalyticsPanel.Header = Header;
AnalyticsPanel.Body = Body;
AnalyticsPanel.MetricGrid = MetricGrid;
AnalyticsPanel.Chart = Chart;
AnalyticsPanel.Table = Table;
AnalyticsPanel.MinimalView = MinimalView;
AnalyticsPanel.MiniMetric = MiniMetric;