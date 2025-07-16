import React, { useState, useEffect } from 'react';
import { fetchVolatilitySurface } from '../services/bloombergService';
import type { VolatilityData } from '../types/bloomberg';
import { TENORS, STRIKES } from '../types/bloomberg';

export const VolatilityMatrix: React.FC = () => {
  const [data, setData] = useState<VolatilityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      setError(null);
      const volData = await fetchVolatilitySurface('EURUSD');
      setData(volData);
      console.log('Volatility data loaded:', volData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
      console.error('Failed to load volatility data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div style={{ fontSize: '18px', color: '#646cff' }}>
          Loading real Bloomberg Terminal data...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px', color: '#ff4444' }}>
        Error: {error}
      </div>
    );
  }
  
  // Check if we have volatility data
  const hasVolData = data && Object.keys(data.atmVols).length > 0 && 
    Object.values(data.atmVols).some(v => v > 0);

  if (!data) return null;

  return (
    <div style={{ 
      padding: '20px',
      maxHeight: 'calc(100vh - 200px)',
      overflowY: 'auto',
      overflowX: 'auto'
    }}>
      {/* Spot Rate */}
      <div style={{ 
        marginBottom: '20px', 
        padding: '15px',
        background: '#1a1a1a',
        borderRadius: '8px',
        border: '1px solid #646cff'
      }}>
        <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
          EUR/USD Spot: {data.spot.toFixed(4)}
        </div>
        <div style={{ fontSize: '12px', color: '#999', marginTop: '5px' }}>
          Last Update: {data.timestamp.toLocaleString()}
        </div>
      </div>

      {/* Data Status Notice */}
      {!hasVolData && (
        <div style={{ 
          marginBottom: '20px', 
          padding: '15px',
          background: '#1a1a1a',
          borderRadius: '8px',
          border: '1px solid #ff8c00'
        }}>
          <div style={{ fontSize: '16px', color: '#ff8c00' }}>
            ⚠️ Bloomberg Terminal volatility data not available
          </div>
          <div style={{ fontSize: '12px', color: '#999', marginTop: '5px' }}>
            The API is connected but Bloomberg Terminal is returning null values for volatility fields.
            This may be due to data subscription or market hours.
          </div>
        </div>
      )}

      {/* ATM Volatilities */}
      <div style={{ marginBottom: '30px' }}>
        <h3 style={{ color: '#646cff', marginBottom: '10px' }}>ATM Implied Volatilities</h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fill, minmax(80px, 1fr))',
          gap: '10px',
          padding: '15px',
          background: '#1a1a1a',
          borderRadius: '8px'
        }}>
          {TENORS.map(tenor => (
            <div key={tenor} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '11px', color: '#999' }}>{tenor}</div>
              <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                {data.atmVols[tenor]?.toFixed(2) || '-'}%
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Reversals */}
      <div style={{ marginBottom: '30px' }}>
        <h3 style={{ color: '#646cff', marginBottom: '10px' }}>Risk Reversals (25D Call - 25D Put)</h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#1a1a1a' }}>
            <thead>
              <tr>
                <th style={{ padding: '8px', textAlign: 'left', borderBottom: '1px solid #333' }}>Strike</th>
                {TENORS.map(tenor => (
                  <th key={tenor} style={{ padding: '8px', textAlign: 'center', borderBottom: '1px solid #333', fontSize: '11px' }}>
                    {tenor}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {STRIKES.map(strike => (
                <tr key={strike}>
                  <td style={{ padding: '8px', fontWeight: 'bold' }}>{strike}</td>
                  {TENORS.map(tenor => {
                    const value = data.riskReversals[strike]?.[tenor];
                    return (
                      <td key={tenor} style={{ 
                        padding: '8px', 
                        textAlign: 'center',
                        color: value ? (value > 0 ? '#4ade80' : '#ff4444') : '#666'
                      }}>
                        {value?.toFixed(3) || '-'}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Butterflies */}
      <div style={{ marginBottom: '30px' }}>
        <h3 style={{ color: '#646cff', marginBottom: '10px' }}>Butterflies (25D Strangle - ATM)</h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#1a1a1a' }}>
            <thead>
              <tr>
                <th style={{ padding: '8px', textAlign: 'left', borderBottom: '1px solid #333' }}>Strike</th>
                {TENORS.map(tenor => (
                  <th key={tenor} style={{ padding: '8px', textAlign: 'center', borderBottom: '1px solid #333', fontSize: '11px' }}>
                    {tenor}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {STRIKES.map(strike => (
                <tr key={strike}>
                  <td style={{ padding: '8px', fontWeight: 'bold' }}>{strike}</td>
                  {TENORS.map(tenor => {
                    const value = data.butterflies[strike]?.[tenor];
                    return (
                      <td key={tenor} style={{ 
                        padding: '8px', 
                        textAlign: 'center',
                        color: value ? '#60a5fa' : '#666'
                      }}>
                        {value?.toFixed(3) || '-'}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};