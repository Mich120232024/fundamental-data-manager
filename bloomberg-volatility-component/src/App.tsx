import { useState, useEffect } from 'react';
import { VolatilityMatrix } from './components/VolatilityMatrix';
import { bloombergService, VolatilityData } from './services/bloomberg';
import './App.css';

function App() {
  const [volatilityData, setVolatilityData] = useState<VolatilityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadVolatilityData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await bloombergService.fetchVolatilitySurface('EURUSD');
      setVolatilityData(data);
      
    } catch (err) {
      console.error('Error loading volatility data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVolatilityData();
    
    // Refresh every 30 seconds
    const interval = setInterval(loadVolatilityData, 30000);
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
          textShadow: '0 0 10px rgba(0, 255, 65, 0.5)',
          fontFamily: 'monospace'
        }}>
          Bloomberg Volatility Component
        </h1>
        <p style={{
          margin: '5px 0 0 0',
          color: '#888',
          fontSize: '14px',
          fontFamily: 'monospace'
        }}>
          Real-time FX Volatility Surface • Bloomberg Terminal Data
        </p>
      </header>

      <main style={{ padding: '0 20px', maxWidth: '1200px', margin: '0 auto' }}>
        <VolatilityMatrix
          data={volatilityData}
          loading={loading}
          error={error}
        />
        
        {!loading && !error && (
          <div style={{
            marginTop: '20px',
            textAlign: 'center'
          }}>
            <button
              onClick={loadVolatilityData}
              style={{
                background: '#00ff41',
                color: '#000',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '4px',
                fontSize: '12px',
                fontWeight: 'bold',
                cursor: 'pointer',
                fontFamily: 'monospace'
              }}
            >
              Refresh Data
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
