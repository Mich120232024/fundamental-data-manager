import React from 'react';
import { motion } from 'framer-motion';
import { useSharedFilters } from './SharedFilterContext';
import { theme } from '../../theme';

export const FilterBar: React.FC = () => {
  const { timeRange, currencies, aggregation, updateFilter } = useSharedFilters();

  const timeRangeOptions = [
    { value: '1H', label: '1 Hour' },
    { value: '1D', label: '1 Day' },
    { value: '1W', label: '1 Week' },
    { value: '1M', label: '1 Month' },
    { value: '1Y', label: '1 Year' }
  ];

  const currencyPairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CHF'];

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        background: theme.surfaceAlt,
        padding: '12px 16px',
        borderRadius: '8px',
        display: 'flex',
        gap: '16px',
        alignItems: 'center',
        marginBottom: '16px',
        flexWrap: 'wrap'
      }}
    >
      {/* Time Range Selector */}
      <div style={{ display: 'flex', gap: '8px' }}>
        {timeRangeOptions.map(option => (
          <motion.button
            key={option.value}
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => updateFilter('timeRange', option.value as any)}
            style={{
              background: timeRange === option.value ? theme.gradient : 'transparent',
              color: timeRange === option.value ? theme.text : theme.textSecondary,
              border: `1px solid ${timeRange === option.value ? theme.primary : theme.border}`,
              borderRadius: '6px',
              padding: '4px 12px',
              fontSize: '11px',
              fontWeight: '400',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              opacity: timeRange === option.value ? 0.85 : 1
            }}
          >
            {option.label}
          </motion.button>
        ))}
      </div>

      {/* Currency Multi-Select */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center',
        gap: '8px',
        flex: 1
      }}>
        <span style={{ fontSize: '11px', color: theme.textSecondary }}>Pairs:</span>
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {currencyPairs.map(pair => (
            <motion.button
              key={pair}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                const newCurrencies = currencies.includes(pair)
                  ? currencies.filter(c => c !== pair)
                  : [...currencies, pair];
                updateFilter('currencies', newCurrencies);
              }}
              style={{
                background: currencies.includes(pair) ? `${theme.primary}20` : theme.surface,
                color: currencies.includes(pair) ? theme.primary : theme.textSecondary,
                border: `1px solid ${currencies.includes(pair) ? theme.primary : theme.border}`,
                borderRadius: '4px',
                padding: '3px 8px',
                fontSize: '10px',
                fontWeight: '400',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              {pair}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Aggregation Selector */}
      <div style={{ position: 'relative' }}>
        <select
          value={aggregation}
          onChange={(e) => updateFilter('aggregation', e.target.value as any)}
          style={{
            background: `linear-gradient(to bottom, ${theme.surfaceAlt}CC, ${theme.surface}EE)`,
            color: theme.text,
            border: `1px solid ${theme.border}`,
            borderRadius: '6px',
            padding: '6px 28px 6px 12px',
            fontSize: theme.typography.body.fontSize,
            fontWeight: theme.typography.body.fontWeight,
            cursor: 'pointer',
            outline: 'none',
            appearance: 'none',
            backdropFilter: 'blur(8px)',
            transition: 'all 0.2s ease'
          }}
        >
          <option value="tick">Tick</option>
          <option value="1m">1 Min</option>
          <option value="5m">5 Min</option>
          <option value="15m">15 Min</option>
          <option value="1h">1 Hour</option>
          <option value="1d">1 Day</option>
        </select>
        <div style={{
          position: 'absolute',
          right: '8px',
          top: '50%',
          transform: 'translateY(-50%)',
          pointerEvents: 'none'
        }}>
          <svg width="10" height="6" viewBox="0 0 10 6" fill="none">
            <path d="M1 1L5 5L9 1" stroke={theme.textSecondary} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      </div>
    </motion.div>
  );
};