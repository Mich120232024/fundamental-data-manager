import { BrowserRouter as Router } from 'react-router-dom'
import { ThemeProvider, useTheme } from './contexts/ThemeContext'
import { Header } from './components/Header'
import { MainAppContainer } from './components/MainAppContainer'

// Inner app component that uses theme
function AppContent() {
  const { currentTheme } = useTheme()
  
  return (
    <div className="min-h-screen flex flex-col" style={{ 
      backgroundColor: currentTheme.background, 
      color: currentTheme.text 
    }}>
      {/* Header */}
      <Header />
      
      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        <MainAppContainer />
      </main>
      
      {/* Status Bar */}
      <div style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: currentTheme.surface + 'EE',
        borderTop: `1px solid ${currentTheme.border}`,
        padding: "6px 16px",
        fontSize: "12px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        height: "40px",
        zIndex: 1000,
        backdropFilter: "blur(12px)"
      }}>
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <span style={{ color: currentTheme.success }}>● Bloomberg Connected</span>
          <span style={{ color: currentTheme.textSecondary }}>API: 20.172.249.92:8080</span>
          <span style={{ color: currentTheme.textSecondary }}>Real-time Data</span>
        </div>
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <span style={{ color: currentTheme.textSecondary }}>Last Update: Live</span>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <ThemeProvider>
      <Router>
        <AppContent />
      </Router>
    </ThemeProvider>
  )
}

export default App