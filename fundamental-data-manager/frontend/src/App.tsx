import React, { useState, useEffect } from 'react'

const API_BASE = 'http://localhost:8850'

interface APIEntry {
  id: string
  apiName?: string
  provider?: string
  category?: string
  endpoints: any[]
  datasets: any[]
  fields: Record<string, any>
}

interface Stats {
  total_apis: number
  total_endpoints: number
  total_datasets: number
  total_fields: number
  providers: Record<string, number>
  categories: Record<string, number>
}

function App() {
  const [apis, setApis] = useState<APIEntry[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [catalogRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/api/catalog`),
        fetch(`${API_BASE}/api/stats`)
      ])
      
      if (!catalogRes.ok || !statsRes.ok) {
        throw new Error('Failed to fetch data')
      }
      
      const catalogData = await catalogRes.json()
      const statsData = await statsRes.json()
      
      setApis(catalogData)
      setStats(statsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const appStyle: React.CSSProperties = {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    backgroundColor: '#1A1A1A',
    color: '#f8f6f0',
    minHeight: '100vh',
    margin: 0,
    padding: 0
  }

  const headerStyle: React.CSSProperties = {
    backgroundColor: '#2A2A2A',
    padding: '12px 24px',
    borderBottom: '1px solid #3a3632',
    height: '60px',
    display: 'flex',
    alignItems: 'center'
  }

  const containerStyle: React.CSSProperties = {
    padding: '20px',
    maxWidth: '1600px',
    margin: '0 auto'
  }

  const cardStyle: React.CSSProperties = {
    backgroundColor: '#2A2A2A',
    border: '1px solid #3a3632',
    borderRadius: '4px',
    padding: '16px 20px',
    marginBottom: '12px'
  }

  const gridStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '16px',
    marginTop: '16px'
  }

  if (loading) {
    return (
      <div style={appStyle}>
        <div style={{...containerStyle, textAlign: 'center', paddingTop: '120px'}}>
          <div style={{fontSize: '14px', color: '#c8c0b0'}}>
            Loading Fundamental Data Catalog...
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={appStyle}>
        <div style={containerStyle}>
          <div style={{...cardStyle, borderColor: '#D69A82', marginTop: '60px'}}>
            <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
              <div>
                <h3 style={{margin: 0, fontSize: '14px', fontWeight: '600', color: '#D69A82'}}>
                  Error Loading Data
                </h3>
                <p style={{margin: '4px 0 0 0', fontSize: '12px', color: '#c8c0b0'}}>
                  {error}
                </p>
              </div>
              <button 
                onClick={loadData}
                style={{
                  padding: '6px 16px',
                  backgroundColor: '#7A9E65',
                  color: '#f8f6f0',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '12px',
                  fontWeight: '500'
                }}
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div style={appStyle}>
      <header style={headerStyle}>
        <h1 style={{margin: 0, fontSize: '16px', fontWeight: '600'}}>
          Fundamental Data Manager • Economic Data API Catalog
        </h1>
      </header>

      <div style={containerStyle}>
        {stats && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '12px',
            marginBottom: '24px'
          }}>
            <div style={{...cardStyle, padding: '12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
              <div style={{fontSize: '12px', color: '#c8c0b0'}}>Total APIs</div>
              <div style={{fontSize: '24px', fontWeight: '600', color: '#7A9E65'}}>{stats.total_apis}</div>
            </div>
            
            <div style={{...cardStyle, padding: '12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
              <div style={{fontSize: '12px', color: '#c8c0b0'}}>Endpoints</div>
              <div style={{fontSize: '24px', fontWeight: '600', color: '#7A9E65'}}>{stats.total_endpoints}</div>
            </div>
            
            <div style={{...cardStyle, padding: '12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
              <div style={{fontSize: '12px', color: '#c8c0b0'}}>Datasets</div>
              <div style={{fontSize: '24px', fontWeight: '600', color: '#7A9E65'}}>{stats.total_datasets}</div>
            </div>
            
            <div style={{...cardStyle, padding: '12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
              <div style={{fontSize: '12px', color: '#c8c0b0'}}>Data Fields</div>
              <div style={{fontSize: '24px', fontWeight: '600', color: '#7A9E65'}}>{stats.total_fields.toLocaleString()}</div>
            </div>
          </div>
        )}

        <div style={{marginTop: '24px'}}>
          <h3 style={{fontSize: '14px', fontWeight: '600', color: '#c8c0b0', marginBottom: '16px'}}>
            API Catalog • {apis.length} Economic Data APIs
          </h3>
          <div style={gridStyle}>
            {apis.map((api) => (
              <div key={api.id} style={cardStyle}>
                <div style={{marginBottom: '12px', borderBottom: '1px solid #3a3632', paddingBottom: '8px'}}>
                  <h4 style={{margin: 0, fontSize: '14px', fontWeight: '600', color: '#95BD78'}}>
                    {api.apiName || api.id}
                  </h4>
                  <div style={{display: 'flex', gap: '12px', marginTop: '4px'}}>
                    {api.provider && (
                      <div style={{fontSize: '11px', color: '#9a9488'}}>
                        {api.provider}
                      </div>
                    )}
                    {api.provider && api.category && (
                      <div style={{fontSize: '11px', color: '#9a9488'}}>•</div>
                    )}
                    {api.category && (
                      <div style={{fontSize: '11px', color: '#9a9488'}}>
                        {api.category}
                      </div>
                    )}
                  </div>
                </div>
                
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(3, 1fr)',
                  gap: '12px',
                  textAlign: 'center'
                }}>
                  <div>
                    <div style={{fontSize: '18px', fontWeight: '600', color: '#7A9E65'}}>
                      {api.endpoints?.length || 0}
                    </div>
                    <div style={{fontSize: '10px', color: '#9a9488', textTransform: 'uppercase', letterSpacing: '0.5px'}}>
                      Endpoints
                    </div>
                  </div>
                  
                  <div>
                    <div style={{fontSize: '18px', fontWeight: '600', color: '#95BD78'}}>
                      {api.datasets?.length || 0}
                    </div>
                    <div style={{fontSize: '10px', color: '#9a9488', textTransform: 'uppercase', letterSpacing: '0.5px'}}>
                      Datasets
                    </div>
                  </div>
                  
                  <div>
                    <div style={{fontSize: '18px', fontWeight: '600', color: '#8BB4DD'}}>
                      {Object.keys(api.fields || {}).length}
                    </div>
                    <div style={{fontSize: '10px', color: '#9a9488', textTransform: 'uppercase', letterSpacing: '0.5px'}}>
                      Fields
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App