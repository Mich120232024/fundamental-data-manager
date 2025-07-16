import { VolatilityMatrix } from './components/VolatilityMatrix'
import './App.css'

function App() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      background: '#242424', 
      color: 'rgba(255, 255, 255, 0.87)',
      padding: '20px',
      fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, sans-serif'
    }}>
      <h1 style={{ color: '#646cff', marginBottom: '20px' }}>Bloomberg Volatility Surface</h1>
      <p style={{ marginBottom: '30px' }}>Real-time FX volatility surface - ALL strikes and tenors</p>
      
      {/* Bloomberg Terminal real data */}
      <VolatilityMatrix />
    </div>
  )
}

export default App