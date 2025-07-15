import React from 'react';
import { VolatilityData } from '../services/bloomberg';

interface VolatilityMatrixProps {
  data: VolatilityData | null;
  loading: boolean;
  error: string | null;
}

export const VolatilityMatrix: React.FC<VolatilityMatrixProps> = ({
  data,
  loading,
  error
}) => {
  if (loading) {
    return (
      <div style={{
        padding: '20px',
        textAlign: 'center',
        color: '#00ff41',
        fontSize: '14px'
      }}>
        Connecting to Bloomberg Terminal...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        padding: '20px',
        textAlign: 'center',
        color: '#ff4444',
        backgroundColor: 'rgba(255, 68, 68, 0.1)',
        borderRadius: '8px',
        margin: '20px',
        fontSize: '14px'
      }}>
        Error: {error}
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{
        padding: '20px',
        textAlign: 'center',
        color: '#888',
        fontSize: '14px'
      }}>
        No volatility data available
      </div>
    );
  }

  const tenors = Object.keys(data.atmVols).sort((a, b) => {
    const order = ['1W', '1M', '3M', '6M', '1Y', '2Y'];
    return order.indexOf(a) - order.indexOf(b);
  });

  return (
    <div style={{
      backgroundColor: '#0a0a0a',
      color: '#fff',
      padding: '20px',
      borderRadius: '8px',
      border: '1px solid #333',
      fontFamily: 'monospace',
      fontSize: '11px'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '15px',
        borderBottom: '1px solid #333',
        paddingBottom: '10px'
      }}>
        <h3 style={{
          margin: 0,
          color: '#00ff41',
          fontSize: '16px',
          textShadow: '0 0 10px rgba(0, 255, 65, 0.5)'
        }}>
          {data.pair} Volatility Matrix
        </h3>
        <div style={{ fontSize: '10px', color: '#888' }}>
          SPOT: {data.spot.toFixed(4)} | Live Bloomberg Data
        </div>
      </div>

      <table style={{
        width: '100%',
        borderCollapse: 'collapse',
        fontSize: '11px'
      }}>
        <thead>
          <tr style={{ borderBottom: '1px solid #333' }}>
            <th style={{ padding: '8px', textAlign: 'left', color: '#888', minWidth: '60px' }}>
              Tenor
            </th>
            <th style={{ padding: '8px', textAlign: 'right', color: '#888', minWidth: '80px' }}>
              ATM Vol (%)
            </th>
            <th style={{ padding: '8px', textAlign: 'right', color: '#888', minWidth: '70px' }}>
              25Δ RR
            </th>
            <th style={{ padding: '8px', textAlign: 'right', color: '#888', minWidth: '70px' }}>
              25Δ BF
            </th>
            <th style={{ padding: '8px', textAlign: 'right', color: '#888', minWidth: '70px' }}>
              10Δ RR
            </th>
            <th style={{ padding: '8px', textAlign: 'right', color: '#888', minWidth: '70px' }}>
              10Δ BF
            </th>
          </tr>
        </thead>
        <tbody>
          {tenors.map(tenor => (
            <tr key={tenor} style={{ borderBottom: '1px solid #222' }}>
              <td style={{ 
                padding: '8px', 
                color: '#00ff41',
                fontWeight: 'bold'
              }}>
                {tenor}
              </td>
              <td style={{ 
                padding: '8px', 
                textAlign: 'right', 
                color: '#fff',
                fontWeight: 'bold'
              }}>
                {data.atmVols[tenor]?.toFixed(2) || '-'}
              </td>
              <td style={{ 
                padding: '8px', 
                textAlign: 'right',
                color: data.riskReversals25D[tenor] && data.riskReversals25D[tenor] < 0 ? '#ff4444' : '#44ff44'
              }}>
                {data.riskReversals25D[tenor]?.toFixed(3) || '-'}
              </td>
              <td style={{ 
                padding: '8px', 
                textAlign: 'right', 
                color: '#ffaa44'
              }}>
                {data.butterflies25D[tenor]?.toFixed(3) || '-'}
              </td>
              <td style={{ 
                padding: '8px', 
                textAlign: 'right',
                color: data.riskReversals10D[tenor] && data.riskReversals10D[tenor] < 0 ? '#ff4444' : '#44ff44'
              }}>
                {data.riskReversals10D[tenor]?.toFixed(3) || '-'}
              </td>
              <td style={{ 
                padding: '8px', 
                textAlign: 'right', 
                color: '#ffaa44'
              }}>
                {data.butterflies10D[tenor]?.toFixed(3) || '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{
        marginTop: '15px',
        fontSize: '10px',
        color: '#888',
        textAlign: 'center'
      }}>
        Last Updated: {new Date(data.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
};