import React from 'react';
import { motion } from 'framer-motion';
import { theme } from '../theme';

interface StyledSelectProps {
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
  placeholder?: string;
  width?: string;
}

export const StyledSelect: React.FC<StyledSelectProps> = ({
  value,
  onChange,
  options,
  placeholder = "Select...",
  width = "100%"
}) => {
  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      style={{
        position: 'relative',
        width
      }}
    >
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{
          width: '100%',
          background: `linear-gradient(to bottom, ${theme.surfaceAlt}CC, ${theme.surface}EE)`,
          border: `1px solid ${theme.border}`,
          borderRadius: '6px',
          padding: '8px 32px 8px 12px',
          color: theme.text,
          fontSize: theme.typography.body.fontSize,
          fontWeight: theme.typography.body.fontWeight,
          cursor: 'pointer',
          outline: 'none',
          appearance: 'none',
          backdropFilter: 'blur(8px)',
          boxShadow: `inset 0 1px 2px ${theme.background}40`,
          transition: 'all 0.2s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = `linear-gradient(to bottom, ${theme.surfaceAlt}, ${theme.surface})`;
          e.currentTarget.style.borderColor = theme.primary + '40';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = `linear-gradient(to bottom, ${theme.surfaceAlt}CC, ${theme.surface}EE)`;
          e.currentTarget.style.borderColor = theme.border;
        }}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      
      {/* Custom dropdown arrow */}
      <div
        style={{
          position: 'absolute',
          right: '12px',
          top: '50%',
          transform: 'translateY(-50%)',
          pointerEvents: 'none',
          display: 'flex',
          alignItems: 'center'
        }}
      >
        <svg
          width="12"
          height="8"
          viewBox="0 0 12 8"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M1 1.5L6 6.5L11 1.5"
            stroke={theme.textSecondary}
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
    </motion.div>
  );
};