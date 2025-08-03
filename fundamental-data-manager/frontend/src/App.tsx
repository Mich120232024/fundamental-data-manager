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

interface DiscoveryAPI {
  id: string
  name: string
  provider: string
  description: string
  discovery_status: 'not_started' | 'researching' | 'documented' | 'tested' | 'production_ready'
  tags?: string[]
  access_info: {
    is_free: boolean
    requires_api_key: boolean
    requires_approval: boolean
    pricing_model: string
    rate_limits: string
  }
  technical_info: {
    base_url: string
    protocol: string
    data_formats: string[]
    auth_method: string
  }
  content_summary: {
    data_categories: string[]
    geographic_scope: string
    update_frequency: string
    historical_data: boolean
  }
  research_notes: {
    documentation_url: string
    sample_endpoints: string[]
    data_quality: string
    last_researched: string
    researcher_notes: string
  }
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
  const [discovery, setDiscovery] = useState<DiscoveryAPI[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'catalog' | 'inventory' | 'discovery'>('discovery')
  const [selectedApi, setSelectedApi] = useState<DiscoveryAPI | null>(null)
  
  // Filter states
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [providerFilter, setProviderFilter] = useState<string>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [catalogRes, inventoryRes, discoveryRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/api/catalog`),
        fetch(`${API_BASE}/api/inventory`),
        fetch(`${API_BASE}/api/discovery`),
        fetch(`${API_BASE}/api/stats`)
      ])
      
      if (!catalogRes.ok || !inventoryRes.ok || !discoveryRes.ok || !statsRes.ok) {
        throw new Error('Failed to fetch data')
      }
      
      const catalogData = await catalogRes.json()
      const inventoryData = await inventoryRes.json()
      const discoveryData = await discoveryRes.json()
      const statsData = await statsRes.json()
      
      setApis(catalogData)
      setInventory(inventoryData)
      setDiscovery(discoveryData)
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
          onClick={() => setActiveTab('discovery')}
          style={{
            backgroundColor: 'transparent',
            border: 'none',
            padding: '16px 0',
            color: activeTab === 'discovery' ? '#7A9E65' : '#c8c0b0',
            fontSize: '14px',
            fontWeight: '600',
            cursor: 'pointer',
            borderBottom: activeTab === 'discovery' ? '2px solid #7A9E65' : '2px solid transparent',
            transition: 'all 0.2s ease',
            whiteSpace: 'nowrap'
          }}
        >
          API Catalog ({discovery.length})
        </button>
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
          API Registry ({apis.length})
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
              <div style={{fontSize: '24px', fontWeight: '600', color: '#7A9E65'}}>{inventory?.length || 0}</div>
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
              Application Registry • {inventory?.length || 0} Items
            </h3>
            <div style={gridStyle}>
              {inventory && inventory.length > 0 ? (
                inventory.map((item, index) => {
                  // Safely access nested properties
                  const displayName = item?.name || item?.display_name || item?.id || `Application ${index + 1}`
                  const catalogType = item?.catalog_type || ''
                  const classification = item?.classification?.primary_category || item?.classification || ''
                  const version = item?.version || item?.technical?.api_version || 'N/A'
                  const updatedYear = item?._ts ? new Date(item._ts * 1000).getFullYear() : 'N/A'
                  
                  return (
                    <div key={item?.id || `item-${index}`} style={cardStyle}>
                      <div style={{marginBottom: '12px', borderBottom: '1px solid #3a3632', paddingBottom: '8px'}}>
                        <h4 style={{margin: 0, fontSize: '14px', fontWeight: '600', color: '#95BD78'}}>
                          {displayName}
                        </h4>
                        <div style={{display: 'flex', gap: '12px', marginTop: '4px'}}>
                          {catalogType && (
                            <div style={{fontSize: '11px', color: '#9a9488'}}>
                              {catalogType}
                            </div>
                          )}
                          {catalogType && classification && (
                            <div style={{fontSize: '11px', color: '#9a9488'}}>•</div>
                          )}
                          {classification && (
                            <div style={{fontSize: '11px', color: '#9a9488'}}>
                              {classification}
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
                            {version}
                          </div>
                          <div style={{fontSize: '10px', color: '#9a9488', textTransform: 'uppercase', letterSpacing: '0.5px'}}>
                            Version
                          </div>
                        </div>
                        
                        <div>
                          <div style={{fontSize: '18px', fontWeight: '600', color: '#8BB4DD'}}>
                            {updatedYear}
                          </div>
                          <div style={{fontSize: '10px', color: '#9a9488', textTransform: 'uppercase', letterSpacing: '0.5px'}}>
                            Updated
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })
              ) : (
                <div style={{
                  ...cardStyle,
                  textAlign: 'center',
                  padding: '40px 20px',
                  color: '#c8c0b0'
                }}>
                  {inventory === null ? 'Loading application registry...' : 'No applications found'}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'discovery' && (() => {
          const filteredDiscovery = discovery.filter(api => {
            // Search filter
            if (searchQuery && !api.name.toLowerCase().includes(searchQuery.toLowerCase()) && 
                !api.provider.toLowerCase().includes(searchQuery.toLowerCase()) &&
                !api.description.toLowerCase().includes(searchQuery.toLowerCase())) {
              return false;
            }
            
            // Status filter
            if (statusFilter !== 'all' && api.discovery_status !== statusFilter) {
              return false;
            }
            
            // Provider filter  
            if (providerFilter !== 'all' && api.provider !== providerFilter) {
              return false;
            }
            
            // Category filter
            if (categoryFilter !== 'all') {
              const apiCategories = api.content_summary?.data_categories || [];
              if (!apiCategories.includes(categoryFilter)) {
                return false;
              }
            }
            
            return true;
          });
          
          const uniqueProviders = [...new Set(discovery.map(api => api.provider))].sort();
          const uniqueCategories = [...new Set(discovery.flatMap(api => api.content_summary?.data_categories || []))].sort();
          
          const statusColors = {
            'not_started': '#9a9488',
            'researching': '#D69A82', 
            'documented': '#8BB4DD',
            'tested': '#95BD78',
            'production_ready': '#7A9E65'
          }
          
          return (
            <div>
              {/* Filters */}
              <div style={{
                backgroundColor: '#2A2A2A',
                border: '1px solid #3a3632',
                borderRadius: '4px',
                padding: '16px',
                marginBottom: '16px',
                display: 'flex',
                gap: '16px',
                alignItems: 'center',
                flexWrap: 'wrap'
              }}>
                <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <label style={{fontSize: '12px', color: '#c8c0b0', minWidth: '50px'}}>Search:</label>
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search APIs..."
                    style={{
                      padding: '6px 10px',
                      backgroundColor: '#1A1A1A',
                      border: '1px solid #3a3632',
                      borderRadius: '4px',
                      color: '#f8f6f0',
                      fontSize: '12px',
                      width: '200px'
                    }}
                  />
                </div>
                
                <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <label style={{fontSize: '12px', color: '#c8c0b0', minWidth: '50px'}}>Status:</label>
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    style={{
                      padding: '6px 10px',
                      backgroundColor: '#1A1A1A',
                      border: '1px solid #3a3632',
                      borderRadius: '4px',
                      color: '#f8f6f0',
                      fontSize: '12px'
                    }}
                  >
                    <option value="all">All</option>
                    <option value="not_started">Not Started</option>
                    <option value="researching">Researching</option>
                    <option value="documented">Documented</option>
                    <option value="production_ready">Production Ready</option>
                  </select>
                </div>
                
                <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <label style={{fontSize: '12px', color: '#c8c0b0', minWidth: '60px'}}>Provider:</label>
                  <select
                    value={providerFilter}
                    onChange={(e) => setProviderFilter(e.target.value)}
                    style={{
                      padding: '6px 10px',
                      backgroundColor: '#1A1A1A',
                      border: '1px solid #3a3632',
                      borderRadius: '4px',
                      color: '#f8f6f0',
                      fontSize: '12px',
                      maxWidth: '150px'
                    }}
                  >
                    <option value="all">All Providers</option>
                    {uniqueProviders.map(provider => (
                      <option key={provider} value={provider}>{provider}</option>
                    ))}
                  </select>
                </div>
                
                <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <label style={{fontSize: '12px', color: '#c8c0b0', minWidth: '60px'}}>Category:</label>
                  <select
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                    style={{
                      padding: '6px 10px',
                      backgroundColor: '#1A1A1A',
                      border: '1px solid #3a3632',
                      borderRadius: '4px',
                      color: '#f8f6f0',
                      fontSize: '12px',
                      maxWidth: '120px'
                    }}
                  >
                    <option value="all">All Categories</option>
                    {uniqueCategories.map(category => (
                      <option key={category} value={category}>{category}</option>
                    ))}
                  </select>
                </div>
                
                <div style={{marginLeft: 'auto', fontSize: '12px', color: '#9a9488'}}>
                  {filteredDiscovery.length} of {discovery.length} APIs
                </div>
              </div>
              
              {/* Header */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '250px 120px 80px 60px 60px 120px 100px 1fr',
                gap: '10px',
                padding: '8px 12px',
                backgroundColor: '#2A2A2A',
                borderBottom: '1px solid #3a3632',
                fontSize: '11px',
                fontWeight: '600',
                color: '#9a9488',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                <div>API Name</div>
                <div>Provider</div>
                <div>Status</div>
                <div>Cost</div>
                <div>Auth</div>
                <div>Categories</div>
                <div>Tags</div>
                <div>Description</div>
              </div>
              
              {/* API List */}
              <div style={{
                backgroundColor: '#2A2A2A',
                border: '1px solid #3a3632',
                borderRadius: '0 0 4px 4px',
                maxHeight: '600px',
                overflowY: 'auto'
              }}>
                {filteredDiscovery.length > 0 ? filteredDiscovery.map((api, index) => (
                  <div key={api.id || `discovery-${index}`} style={{
                    display: 'grid',
                    gridTemplateColumns: '250px 120px 80px 60px 60px 120px 100px 1fr',
                    gap: '10px',
                    padding: '10px 12px',
                    borderBottom: index < filteredDiscovery.length - 1 ? '1px solid #3a3632' : 'none',
                    fontSize: '12px',
                    alignItems: 'center',
                    ':hover': {backgroundColor: '#3a3632'}
                  }}>
                    <div 
                      onClick={() => setSelectedApi(api)}
                      style={{
                        fontWeight: '600',
                        color: '#95BD78',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        cursor: 'pointer',
                        textDecoration: 'underline'
                      }}
                    >
                      {api.name}
                    </div>
                    
                    <div style={{
                      color: '#c8c0b0',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {api.provider}
                    </div>
                    
                    <div style={{
                      color: statusColors[api.discovery_status] || '#9a9488',
                      fontSize: '10px',
                      fontWeight: '600',
                      textTransform: 'uppercase'
                    }}>
                      {api.discovery_status.replace('_', ' ')}
                    </div>
                    
                    <div style={{
                      color: api.access_info.is_free === null ? '#9a9488' : 
                            api.access_info.is_free ? '#7A9E65' : '#D69A82',
                      fontSize: '11px',
                      fontWeight: '600'
                    }}>
                      {api.access_info.is_free === null ? 'UNKNOWN' : 
                       api.access_info.is_free ? 'FREE' : 'PAID'}
                    </div>
                    
                    <div style={{
                      color: api.access_info.requires_api_key === null ? '#9a9488' :
                            api.access_info.requires_api_key ? '#8BB4DD' : '#9a9488',
                      fontSize: '11px',
                      fontWeight: '600'
                    }}>
                      {api.access_info.requires_api_key === null ? 'UNKNOWN' :
                       api.access_info.requires_api_key ? 'KEY' : 'NONE'}
                    </div>
                    
                    <div style={{
                      color: '#8BB4DD',
                      fontSize: '10px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {api.content_summary?.data_categories?.join(', ') || 'unknown'}
                    </div>
                    
                    <div style={{
                      color: '#95BD78',
                      fontSize: '10px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {api.tags?.join(', ') || '-'}
                    </div>
                    
                    <div style={{
                      color: '#c8c0b0',
                      fontSize: '11px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {api.description}
                    </div>
                  </div>
                )) : (
                  <div style={{
                    padding: '40px 20px',
                    textAlign: 'center',
                    color: '#9a9488',
                    fontSize: '12px'
                  }}>
                    No APIs match your filters
                  </div>
                )}
              </div>
            </div>
          )
        })()}
        
        {/* API Details Modal */}
        {selectedApi && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <div style={{
              backgroundColor: '#2A2A2A',
              border: '1px solid #3a3632',
              borderRadius: '8px',
              padding: '24px',
              maxWidth: '900px',
              maxHeight: '90vh',
              overflow: 'auto',
              width: '90%'
            }}>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px'}}>
                <div>
                  <h2 style={{margin: 0, fontSize: '20px', fontWeight: '600', color: '#95BD78'}}>
                    {selectedApi.name}
                  </h2>
                  <p style={{margin: '8px 0', fontSize: '14px', color: '#c8c0b0'}}>
                    {selectedApi.provider}
                  </p>
                </div>
                <button 
                  onClick={() => setSelectedApi(null)}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#3a3632',
                    color: '#f8f6f0',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  Close
                </button>
              </div>
              
              {/* API Summary */}
              <div style={{marginBottom: '24px'}}>
                <h3 style={{fontSize: '16px', fontWeight: '600', color: '#c8c0b0', marginBottom: '8px'}}>
                  Overview
                </h3>
                <p style={{fontSize: '14px', color: '#c8c0b0', lineHeight: '1.6'}}>
                  {selectedApi.research_notes?.api_summary || selectedApi.description || 'No summary available'}
                </p>
              </div>
              
              {/* Documentation Links */}
              <div style={{marginBottom: '24px'}}>
                <h3 style={{fontSize: '16px', fontWeight: '600', color: '#c8c0b0', marginBottom: '8px'}}>
                  Documentation
                </h3>
{selectedApi.research_notes?.documentation_url ? (
                  <a 
                    href={selectedApi.research_notes.documentation_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      color: '#7A9E65',
                      fontSize: '14px',
                      textDecoration: 'underline'
                    }}
                  >
                    {selectedApi.research_notes.documentation_url}
                  </a>
                ) : (
                  <span style={{color: '#9a9488', fontSize: '14px'}}>
                    No documentation URL available
                  </span>
                )}
              </div>
              
              {/* Technical Details */}
              <div style={{marginBottom: '24px'}}>
                <h3 style={{fontSize: '16px', fontWeight: '600', color: '#c8c0b0', marginBottom: '12px'}}>
                  Technical Details
                </h3>
                <div style={{
                  backgroundColor: '#1A1A1A',
                  border: '1px solid #3a3632',
                  borderRadius: '4px',
                  padding: '16px'
                }}>
                  <div style={{marginBottom: '12px'}}>
                    <strong style={{color: '#95BD78', fontSize: '12px'}}>Base URL:</strong>
                    <code style={{marginLeft: '8px', color: '#c8c0b0', fontSize: '12px'}}>
                      {selectedApi.technical_info?.base_url || 'Not specified'}
                    </code>
                  </div>
                  <div style={{marginBottom: '12px'}}>
                    <strong style={{color: '#95BD78', fontSize: '12px'}}>Protocol:</strong>
                    <span style={{marginLeft: '8px', color: '#c8c0b0', fontSize: '12px'}}>
                      {selectedApi.technical_info?.protocol || 'Not specified'}
                    </span>
                  </div>
                  <div style={{marginBottom: '12px'}}>
                    <strong style={{color: '#95BD78', fontSize: '12px'}}>Authentication:</strong>
                    <span style={{marginLeft: '8px', color: '#c8c0b0', fontSize: '12px'}}>
                      {selectedApi.technical_info?.auth_method || 'Not specified'}
                    </span>
                  </div>
                  <div>
                    <strong style={{color: '#95BD78', fontSize: '12px'}}>Rate Limits:</strong>
                    <span style={{marginLeft: '8px', color: '#c8c0b0', fontSize: '12px'}}>
                      {selectedApi.access_info?.rate_limits || 'Not specified'}
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Endpoints */}
              <div style={{marginBottom: '24px'}}>
                <h3 style={{fontSize: '16px', fontWeight: '600', color: '#c8c0b0', marginBottom: '12px'}}>
                  Available Endpoints ({selectedApi.technical_info?.endpoints?.length || 0})
                </h3>
                <div style={{
                  backgroundColor: '#1A1A1A',
                  border: '1px solid #3a3632',
                  borderRadius: '4px',
                  padding: '16px'
                }}>
                  {selectedApi.technical_info?.endpoints?.length > 0 ? (
                    selectedApi.technical_info.endpoints.map((endpoint, index) => (
                      <div key={index} style={{
                        marginBottom: index < selectedApi.technical_info.endpoints.length - 1 ? '12px' : 0,
                        paddingBottom: index < selectedApi.technical_info.endpoints.length - 1 ? '12px' : 0,
                        borderBottom: index < selectedApi.technical_info.endpoints.length - 1 ? '1px solid #3a3632' : 'none'
                      }}>
                        <code style={{color: '#7A9E65', fontSize: '13px', fontFamily: 'monospace'}}>
                          {typeof endpoint === 'string' ? endpoint : endpoint.path || 'Endpoint details available'}
                        </code>
                      </div>
                    ))
                  ) : (
                    <div style={{color: '#9a9488', fontSize: '12px', textAlign: 'center'}}>
                      No endpoints documented
                    </div>
                  )}
                </div>
              </div>
              
              {/* Access Information */}
              <div>
                <h3 style={{fontSize: '16px', fontWeight: '600', color: '#c8c0b0', marginBottom: '12px'}}>
                  Access Information
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '16px'
                }}>
                  <div>
                    <strong style={{color: '#95BD78', fontSize: '12px'}}>Pricing:</strong>
                    <span style={{marginLeft: '8px', color: '#c8c0b0', fontSize: '12px'}}>
                      {selectedApi.access_info?.pricing_model || 'Not specified'}
                    </span>
                  </div>
                  <div>
                    <strong style={{color: '#95BD78', fontSize: '12px'}}>API Key Required:</strong>
                    <span style={{marginLeft: '8px', color: '#c8c0b0', fontSize: '12px'}}>
                      {selectedApi.access_info?.requires_api_key === null ? 'Unknown' : 
                       selectedApi.access_info?.requires_api_key ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App