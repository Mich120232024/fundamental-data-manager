import { useState, useEffect } from 'react';
import './App.css';
import { VolatilitySurface3D } from './components/VolatilitySurface3D';
import { bloombergService } from './services/bloomberg';
import type { VolatilitySurface, BloombergResponse } from './types/volatility';

function App() {
  const [surface, setSurface] = useState<VolatilitySurface | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadVolatilityData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await bloombergService.fetchVolatilitySurface('EURUSD');
      
      // Process Bloomberg response into volatility surface
      const getValue = (security: string) => {
        const item = data.find((d: BloombergResponse) => d.security === security);
        return item?.fields?.PX_LAST || item?.fields?.PX_MID || 0;
      };
      
      const spot = getValue('EURUSD Curncy');
      
      const atmVols: Record<string, number> = {};
      const tenors = ['1W', '2W', '1M', '2M', '3M', '6M', '9M', '1Y', '2Y', '3Y', '5Y'];
      tenors.forEach(tenor => {
        const vol = getValue(`EURUSDV${tenor} Curncy`);
        if (vol > 0) atmVols[tenor] = vol;
      });
      
      const riskReversals: Record<string, Record<string, number>> = {
        '25D': {},
        '10D': {}
      };
      
      tenors.forEach(tenor => {
        const rr25 = getValue(`EUR25R${tenor} Curncy`);
        if (rr25 !== 0) riskReversals['25D'][tenor] = rr25;
      });
      
      ['1M', '3M', '6M', '1Y'].forEach(tenor => {
        const rr10 = getValue(`EUR10R${tenor} Curncy`);
        if (rr10 !== 0) riskReversals['10D'][tenor] = rr10;
      });
      
      const butterflies: Record<string, Record<string, number>> = {
        '25D': {},
        '10D': {}
      };
      
      tenors.forEach(tenor => {
        const bf25 = getValue(`EUR25B${tenor} Curncy`);
        if (bf25 !== 0) butterflies['25D'][tenor] = bf25;
      });
      
      ['1M', '3M', '6M', '1Y'].forEach(tenor => {
        const bf10 = getValue(`EUR10B${tenor} Curncy`);
        if (bf10 !== 0) butterflies['10D'][tenor] = bf10;
      });
      
      const volSurface: VolatilitySurface = {
        pair: 'EURUSD',
        timestamp: new Date().toISOString(),
        spot: {
          pair: 'EURUSD',
          spot: spot,
          bid: spot - 0.0002,
          ask: spot + 0.0002,
          timestamp: new Date().toISOString()
        },
        atmVols,
        riskReversals,
        butterflies
      };
      
      setSurface(volSurface);
      
    } catch (err) {
      console.error('Error loading volatility data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVolatilityData();
    const interval = setInterval(loadVolatilityData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <header style={{
        background: '#0a0a0a',
        borderBottom: '1px solid #333',
        padding: '20px',
        marginBottom: '20px'
      }}>
        <h1 style={{
          margin: 0,
          fontSize: '24px',
          color: '#00ff41',
          textShadow: '0 0 10px rgba(0, 255, 65, 0.5)'
        }}>
          FX Volatility Surface Engine
        </h1>
        <p style={{
          margin: '5px 0 0 0',
          color: '#888',
          fontSize: '14px'
        }}>
          Real-time Bloomberg Terminal Data
        </p>
      </header>

      <main style={{ padding: '0 20px' }}>
        {loading && !surface && (
          <div style={{ textAlign: 'center', padding: '50px', color: '#888' }}>
            Connecting to Bloomberg Terminal...
          </div>
        )}
        
        {error && (
          <div style={{ 
            textAlign: 'center', 
            padding: '20px', 
            color: '#ff4444',
            background: 'rgba(255, 68, 68, 0.1)',
            borderRadius: '8px',
            margin: '20px auto',
            maxWidth: '600px'
          }}>
            Error: {error}
          </div>
        )}
        
        {surface && <VolatilitySurface3D surface={surface} />}
        
        {surface && (
          <div style={{
            marginTop: '20px',
            padding: '20px',
            background: '#0a0a0a',
            borderRadius: '8px',
            border: '1px solid #333'
          }}>
            <h3 style={{ color: '#00ff41', marginBottom: '15px' }}>
              Volatility Matrix
            </h3>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: '12px',
              fontFamily: 'monospace'
            }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #333' }}>
                  <th style={{ padding: '8px', textAlign: 'left', color: '#888' }}>Tenor</th>
                  <th style={{ padding: '8px', textAlign: 'right', color: '#888' }}>ATM Vol (%)</th>
                  <th style={{ padding: '8px', textAlign: 'right', color: '#888' }}>25D RR</th>
                  <th style={{ padding: '8px', textAlign: 'right', color: '#888' }}>25D BF</th>
                  <th style={{ padding: '8px', textAlign: 'right', color: '#888' }}>10D RR</th>
                  <th style={{ padding: '8px', textAlign: 'right', color: '#888' }}>10D BF</th>
                </tr>
              </thead>
              <tbody>
                {Object.keys(surface.atmVols).map(tenor => (
                  <tr key={tenor} style={{ borderBottom: '1px solid #222' }}>
                    <td style={{ padding: '8px', color: '#00ff41' }}>{tenor}</td>
                    <td style={{ padding: '8px', textAlign: 'right', color: '#fff' }}>
                      {surface.atmVols[tenor]?.toFixed(2) || '-'}
                    </td>
                    <td style={{ 
                      padding: '8px', 
                      textAlign: 'right', 
                      color: surface.riskReversals['25D']?.[tenor] && surface.riskReversals['25D'][tenor] < 0 ? '#ff4444' : '#44ff44' 
                    }}>
                      {surface.riskReversals['25D']?.[tenor]?.toFixed(3) || '-'}
                    </td>
                    <td style={{ padding: '8px', textAlign: 'right', color: '#ffaa44' }}>
                      {surface.butterflies['25D']?.[tenor]?.toFixed(3) || '-'}
                    </td>
                    <td style={{ 
                      padding: '8px', 
                      textAlign: 'right', 
                      color: surface.riskReversals['10D']?.[tenor] && surface.riskReversals['10D'][tenor] < 0 ? '#ff4444' : '#44ff44' 
                    }}>
                      {surface.riskReversals['10D']?.[tenor]?.toFixed(3) || '-'}
                    </td>
                    <td style={{ padding: '8px', textAlign: 'right', color: '#ffaa44' }}>
                      {surface.butterflies['10D']?.[tenor]?.toFixed(3) || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

export default App
