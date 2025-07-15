import React, { useMemo, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSharedFilters } from './SharedFilterContext';
import { theme } from '../../theme';

// This component demonstrates how filters propagate
export const FilterAwareChart: React.FC<{ title: string }> = ({ title }) => {
  const { timeRange, currencies, aggregation } = useSharedFilters();
  const [data, setData] = useState<any[]>([]);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);

  // Handle ESC key to exit fullscreen
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isMaximized) {
        setIsMaximized(false);
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isMaximized]);

  // Calculate date range based on timeRange filter
  const dateRange = useMemo(() => {
    const end = new Date();
    const start = new Date();
    
    switch (timeRange) {
      case '1H': start.setHours(end.getHours() - 1); break;
      case '1D': start.setDate(end.getDate() - 1); break;
      case '1W': start.setDate(end.getDate() - 7); break;
      case '1M': start.setMonth(end.getMonth() - 1); break;
      case '1Y': start.setFullYear(end.getFullYear() - 1); break;
    }
    
    return { start, end };
  }, [timeRange]);

  // Generate data based on filters
  useEffect(() => {
    // Calculate number of data points based on aggregation
    const { start, end } = dateRange;
    const duration = end.getTime() - start.getTime();
    let points = 100;
    
    switch (aggregation) {
      case 'tick': points = 1000; break;
      case '1m': points = Math.floor(duration / 60000); break;
      case '5m': points = Math.floor(duration / 300000); break;
      case '15m': points = Math.floor(duration / 900000); break;
      case '1h': points = Math.floor(duration / 3600000); break;
      case '1d': points = Math.floor(duration / 86400000); break;
    }

    // Generate data for each selected currency
    const newData = currencies.flatMap(currency => 
      Array.from({ length: Math.min(points, 100) }, (_, i) => ({
        time: start.getTime() + (duration / points) * i,
        currency,
        value: 1.08 + Math.random() * 0.02 + (Math.random() - 0.5) * 0.001 * i,
        volume: Math.floor(Math.random() * 1000000)
      }))
    );

    setData(newData);
  }, [timeRange, currencies, aggregation, dateRange]);

  // Calculate summary statistics
  const stats = useMemo(() => {
    if (data.length === 0) return null;
    
    const values = data.map(d => d.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const totalVolume = data.reduce((sum, d) => sum + d.volume, 0);
    
    return { min, max, avg, totalVolume };
  }, [data]);

  return (
    <>
      {/* Fullscreen backdrop */}
      <AnimatePresence>
        {isMaximized && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              inset: 0,
              background: `${theme.background}EE`,
              zIndex: 998,
              backdropFilter: 'blur(4px)'
            }}
            onClick={() => setIsMaximized(false)}
          />
        )}
      </AnimatePresence>

      <motion.div
        layout
        animate={{
          scale: isMaximized ? 1 : 1,
          opacity: 1
        }}
        style={{
          background: theme.surface,
          border: `1px solid ${theme.border}`,
          borderRadius: '8px',
          padding: isCollapsed ? '12px 16px' : '16px',
          height: isCollapsed ? 'auto' : '100%',
          position: isMaximized ? 'fixed' : 'relative',
          inset: isMaximized ? '20px' : 'auto',
          zIndex: isMaximized ? 999 : 'auto',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: isMaximized ? `0 20px 60px ${theme.background}CC` : 'none'
        }}
      >
        {/* Header */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          marginBottom: isCollapsed ? 0 : '8px',
          cursor: 'pointer'
        }}>
          <div 
            onClick={() => !isMaximized && setIsCollapsed(!isCollapsed)}
            style={{ flex: 1 }}
          >
            <h3 style={{ 
              fontSize: theme.typography.h4.fontSize, 
              fontWeight: theme.typography.h4.fontWeight, 
              color: theme.text,
              marginBottom: '4px'
            }}>
              {title}
              {isMaximized && (
                <span style={{ 
                  fontSize: theme.typography.bodyTiny.fontSize, 
                  color: theme.textSecondary, 
                  marginLeft: '8px',
                  fontWeight: '400'
                }}>
                  (Press ESC to exit)
                </span>
              )}
            </h3>
            
            {/* Show active filters - subtle */}
            <div style={{ 
              fontSize: theme.typography.bodyTiny.fontSize, 
              color: theme.textSecondary,
              opacity: 0.8
            }}>
              {timeRange} • {aggregation} • {currencies.join(', ')}
            </div>
          </div>

          {/* Action buttons */}
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            {/* Collapse/Expand button */}
            <motion.button
              whileHover={{ scale: 1.1, backgroundColor: `${theme.primary}20` }}
              whileTap={{ scale: 0.9 }}
              onClick={(e) => {
                e.stopPropagation();
                setIsCollapsed(!isCollapsed);
              }}
              style={{
                background: 'transparent',
                border: 'none',
                borderRadius: '4px',
                width: '24px',
                height: '24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: theme.textSecondary,
                padding: '4px'
              }}
            >
              <motion.svg
                animate={{ rotate: isCollapsed ? 180 : 0 }}
                transition={{ duration: 0.2 }}
                width="12"
                height="12"
                viewBox="0 0 12 12"
                fill="none"
              >
                <path
                  d="M3 5L6 8L9 5"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </motion.svg>
            </motion.button>

            {/* Maximize button */}
            <motion.button
              whileHover={{ scale: 1.1, backgroundColor: `${theme.primary}20` }}
              whileTap={{ scale: 0.9 }}
              onClick={(e) => {
                e.stopPropagation();
                setIsMaximized(!isMaximized);
                if (!isMaximized && isCollapsed) {
                  setIsCollapsed(false);
                }
              }}
              style={{
                background: 'transparent',
                border: 'none',
                borderRadius: '4px',
                width: '24px',
                height: '24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: theme.textSecondary,
                padding: '4px'
              }}
            >
              <svg
                width="12"
                height="12"
                viewBox="0 0 12 12"
                fill="none"
              >
                {isMaximized ? (
                  <path
                    d="M9 1L7 3M5 9L3 11M3 1L5 3M9 11L7 9"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                ) : (
                  <path
                    d="M7 1H11V5M11 1L7 5M5 11H1V7M1 11L5 7"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                )}
              </svg>
            </motion.button>
          </div>
        </div>

        {/* Collapsible content */}
        <AnimatePresence initial={false}>
          {!isCollapsed && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              style={{ overflow: 'hidden', flex: isMaximized ? 1 : 'auto' }}
            >
              {/* Data summary - simple text */}
              {stats && (
                <div style={{
                  fontSize: theme.typography.bodyTiny.fontSize,
                  color: theme.textSecondary,
                  marginBottom: '8px',
                  display: 'flex',
                  gap: '12px',
                  flexWrap: 'wrap'
                }}>
                  <span>Points: <span style={{ color: theme.text }}>{data.length}</span></span>
                  <span>Min: <span style={{ color: theme.danger }}>{stats.min.toFixed(5)}</span></span>
                  <span>Max: <span style={{ color: theme.success }}>{stats.max.toFixed(5)}</span></span>
                  <span>Volume: <span style={{ color: theme.text }}>{(stats.totalVolume / 1000000).toFixed(1)}M</span></span>
                </div>
              )}

              {/* Chart placeholder showing data density */}
              <div style={{
                background: theme.surfaceAlt,
                borderRadius: '8px',
                height: isMaximized ? '100%' : '200px',
                minHeight: '200px',
                position: 'relative',
                overflow: 'hidden'
              }}>
                {/* Visual representation of data points */}
                <div style={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  alignItems: 'flex-end',
                  padding: '10px',
                  gap: '2px'
                }}>
                  {data.slice(0, isMaximized ? 100 : 50).map((point, i) => (
                    <motion.div
                      key={i}
                      initial={{ height: 0 }}
                      animate={{ height: `${((point.value - 1.07) / 0.03) * 100}%` }}
                      transition={{ delay: i * 0.01 }}
                      style={{
                        flex: 1,
                        background: currencies.includes(point.currency) ? theme.primary : theme.textSecondary,
                        opacity: 0.7,
                        borderRadius: '2px 2px 0 0'
                      }}
                    />
                  ))}
                </div>
                
                <div style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  textAlign: 'center',
                  color: theme.text,
                  fontSize: theme.typography.body.fontSize,
                  background: `${theme.background}CC`,
                  padding: '8px 16px',
                  borderRadius: '4px'
                }}>
                  Chart updates with filters
                  <div style={{ fontSize: theme.typography.bodyTiny.fontSize, color: theme.textSecondary, marginTop: '4px' }}>
                    Showing {Math.min(isMaximized ? 100 : 50, data.length)} of {data.length} bars
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </>
  );
};