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
  const [inventory, setInventory] = useState<any[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'catalog' | 'inventory'>('catalog')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [catalogRes, inventoryRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/api/catalog`),
        fetch(`${API_BASE}/api/inventory`),
        fetch(`${API_BASE}/api/stats`)
      ])
      
      if (!catalogRes.ok || !inventoryRes.ok || !statsRes.ok) {
        throw new Error('Failed to fetch data')
      }
      
      const catalogData = await catalogRes.json()
      const inventoryData = await inventoryRes.json()
      const statsData = await statsRes.json()
      
      setApis(catalogData)
      setInventory(inventoryData)
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
    padding: '16px 24px',
    maxWidth: '1800px',
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
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '12px',
    marginTop: '12px'
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

      {/* Bloomberg-style Tab Navigation - integrated with header */}
      <div style={{
        backgroundColor: '#2A2A2A',
        borderBottom: '1px solid #3a3632',
        padding: '0 24px',
        display: 'flex',
        gap: '32px',
        overflowX: 'auto'
      }}>
        <button
          onClick={() => setActiveTab('catalog')}
          style={{
            backgroundColor: 'transparent',
            border: 'none',
            padding: '16px 0',
            color: activeTab === 'catalog' ? '#7A9E65' : '#c8c0b0',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer',
            borderBottom: activeTab === 'catalog' ? '2px solid #7A9E65' : '2px solid transparent',
            transition: 'all 0.2s ease',
            whiteSpace: 'nowrap'
          }}
        >
          API Catalog ({apis.length})
        </button>
        <button
          onClick={() => setActiveTab('inventory')}
          style={{
            backgroundColor: 'transparent',
            border: 'none',
            padding: '16px 0',
            color: activeTab === 'inventory' ? '#7A9E65' : '#c8c0b0',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer',
            borderBottom: activeTab === 'inventory' ? '2px solid #7A9E65' : '2px solid transparent',
            transition: 'all 0.2s ease',
            whiteSpace: 'nowrap'
          }}
        >
          Full Application Registry ({inventory.length})
        </button>
      </div>

      <div style={containerStyle}>

        {stats && activeTab === 'catalog' && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '12px',
            marginBottom: '16px'
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

        {activeTab === 'inventory' && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '12px',
            marginBottom: '16px'
          }}>
            <div style={{...cardStyle, padding: '12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
              <div style={{fontSize: '12px', color: '#c8c0b0'}}>Total Applications</div>
              <div style={{fontSize: '24px', fontWeight: '600', color: '#7A9E65'}}>{inventory.length}</div>
            </div>
            
            <div style={{...cardStyle, padding: '12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
              <div style={{fontSize: '12px', color: '#c8c0b0'}}>Registry Size</div>
              <div style={{fontSize: '24px', fontWeight: '600', color: '#95BD78'}}>Full</div>
            </div>
            
            <div style={{...cardStyle, padding: '12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
              <div style={{fontSize: '12px', color: '#c8c0b0'}}>Source</div>
              <div style={{fontSize: '24px', fontWeight: '600', color: '#8BB4DD'}}>Cosmos DB</div>
            </div>
            
            <div style={{...cardStyle, padding: '12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
              <div style={{fontSize: '12px', color: '#c8c0b0'}}>Container</div>
              <div style={{fontSize: '14px', fontWeight: '600', color: '#c8c0b0'}}>api_inventory</div>
            </div>
          </div>
        )}

        {activeTab === 'catalog' && (
          <div>
            <h3 style={{fontSize: '13px', fontWeight: '600', color: '#c8c0b0', marginBottom: '12px', marginTop: '8px'}}>
              Economic Data APIs
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
        )}

        {activeTab === 'inventory' && (
          <div>
            <h3 style={{fontSize: '13px', fontWeight: '600', color: '#c8c0b0', marginBottom: '12px', marginTop: '8px'}}>
              Application Registry • {inventory.length} Items
            </h3>
            <div style={gridStyle}>
              {inventory.map((item, index) => (
                <div key={item.id || index} style={cardStyle}>
                  <div style={{marginBottom: '12px', borderBottom: '1px solid #3a3632', paddingBottom: '8px'}}>
                    <h4 style={{margin: 0, fontSize: '14px', fontWeight: '600', color: '#95BD78'}}>
                      {item.name || item.title || item.id || `Application ${index + 1}`}
                    </h4>
                    <div style={{display: 'flex', gap: '12px', marginTop: '4px'}}>
                      {item.catalog_type && (
                        <div style={{fontSize: '11px', color: '#9a9488'}}>
                          {item.catalog_type}
                        </div>
                      )}
                      {item.catalog_type && item.classification && (
                        <div style={{fontSize: '11px', color: '#9a9488'}}>•</div>
                      )}
                      {item.classification && (
                        <div style={{fontSize: '11px', color: '#9a9488'}}>
                          {item.classification}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '12px',
                    textAlign: 'center'
                  }}>
                    <div>
                      <div style={{fontSize: '18px', fontWeight: '600', color: '#7A9E65'}}>
                        {item.version || 'N/A'}
                      </div>
                      <div style={{fontSize: '10px', color: '#9a9488', textTransform: 'uppercase', letterSpacing: '0.5px'}}>
                        Version
                      </div>
                    </div>
                    
                    <div>
                      <div style={{fontSize: '18px', fontWeight: '600', color: '#8BB4DD'}}>
                        {item._ts ? new Date(item._ts * 1000).getFullYear() : 'N/A'}
                      </div>
                      <div style={{fontSize: '10px', color: '#9a9488', textTransform: 'uppercase', letterSpacing: '0.5px'}}>
                        Updated
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App