import React, { useState } from 'react';
import { ScenarioSelector } from './ScenarioSelector';
import { theme } from '../theme';

const scenarios = [
  {
    id: 'normalization',
    name: 'Expected curve normalization',
    icon: '📈',
    description: 'Gradual steepening over 12-18 months'
  },
  {
    id: 'inversion',
    name: 'Deeper yield curve inversion',
    icon: '📉',
    description: 'Short rates exceed long rates'
  },
  {
    id: 'steepening',
    name: 'Rapid curve steepening',
    icon: '📊',
    description: 'Fed cuts driving short end lower'
  },
  {
    id: 'flattening',
    name: 'Bear flattening scenario',
    icon: '📋',
    description: 'Long rates rise faster than short'
  },
  {
    id: 'parallel',
    name: 'Parallel shift upward',
    icon: '⬆️',
    description: 'All rates rise equally'
  }
];

export const YieldCurveScenarios: React.FC = () => {
  const [selectedScenario, setSelectedScenario] = useState('normalization');

  return (
    <div style={{
      background: theme.surface,
      border: `1px solid ${theme.border}`,
      borderRadius: '8px',
      padding: '20px'
    }}>
      <h2 style={{
        fontSize: theme.typography.h2.fontSize,
        fontWeight: theme.typography.h2.fontWeight,
        color: theme.text,
        marginBottom: '20px'
      }}>
        G10 YIELD CURVE ANIMATOR
      </h2>
      
      <ScenarioSelector
        scenarios={scenarios}
        selectedScenario={selectedScenario}
        onScenarioChange={setSelectedScenario}
      />
      
      <div style={{
        marginTop: '20px',
        padding: '16px',
        background: theme.surfaceAlt,
        borderRadius: '6px',
        border: `1px solid ${theme.border}`
      }}>
        <div style={{
          fontSize: theme.typography.bodySmall.fontSize,
          color: theme.textSecondary
        }}>
          Selected scenario: <strong style={{ color: theme.text }}>{scenarios.find(s => s.id === selectedScenario)?.name}</strong>
        </div>
      </div>
    </div>
  );
};