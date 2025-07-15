import React from 'react';
import { motion } from 'framer-motion';
import { theme } from '../theme';

interface Scenario {
  id: string;
  name: string;
  icon?: string;
  description?: string;
}

interface ScenarioSelectorProps {
  scenarios: Scenario[];
  selectedScenario: string;
  onScenarioChange: (scenarioId: string) => void;
  label?: string;
}

export const ScenarioSelector: React.FC<ScenarioSelectorProps> = ({
  scenarios,
  selectedScenario,
  onScenarioChange,
  label = "SCENARIO"
}) => {
  const selectedScenarioData = scenarios.find(s => s.id === selectedScenario);

  return (
    <div style={{ width: '100%' }}>
      {label && (
        <div style={{
          fontSize: theme.typography.label.fontSize,
          fontWeight: theme.typography.label.fontWeight,
          color: theme.textSecondary,
          marginBottom: '8px',
          textTransform: theme.typography.label.textTransform,
          letterSpacing: theme.typography.label.letterSpacing
        }}>
          {label}
        </div>
      )}
      
      <motion.div
        whileHover={{ scale: 1.002 }}
        style={{
          position: 'relative',
          background: `linear-gradient(135deg, ${theme.surface}EE 0%, ${theme.surfaceAlt}CC 100%)`,
          border: `1px solid ${theme.border}`,
          borderRadius: '8px',
          padding: '12px 16px',
          cursor: 'pointer',
          backdropFilter: 'blur(10px)',
          boxShadow: `0 2px 8px ${theme.background}40, inset 0 1px 2px ${theme.background}20`,
          transition: 'all 0.3s ease'
        }}
      >
        <select
          value={selectedScenario}
          onChange={(e) => onScenarioChange(e.target.value)}
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            opacity: 0,
            cursor: 'pointer'
          }}
        >
          {scenarios.map((scenario) => (
            <option key={scenario.id} value={scenario.id}>
              {scenario.name}
            </option>
          ))}
        </select>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {selectedScenarioData?.icon && (
            <div style={{
              fontSize: '16px',
              opacity: 0.8
            }}>
              {selectedScenarioData.icon}
            </div>
          )}
          
          <div style={{ flex: 1 }}>
            <div style={{
              fontSize: theme.typography.body.fontSize,
              fontWeight: '500',
              color: theme.text
            }}>
              {selectedScenarioData?.name || 'Select scenario...'}
            </div>
            {selectedScenarioData?.description && (
              <div style={{
                fontSize: theme.typography.bodyTiny.fontSize,
                color: theme.textSecondary,
                marginTop: '2px',
                opacity: 0.8
              }}>
                {selectedScenarioData.description}
              </div>
            )}
          </div>
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            marginLeft: 'auto'
          }}>
            <motion.svg
              animate={{ rotate: 0 }}
              whileHover={{ rotate: 180 }}
              transition={{ duration: 0.3 }}
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M4 6L8 10L12 6"
                stroke={theme.textSecondary}
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </motion.svg>
          </div>
        </div>
      </motion.div>
    </div>
  );
};