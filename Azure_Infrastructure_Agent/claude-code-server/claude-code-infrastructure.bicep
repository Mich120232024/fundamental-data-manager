// Claude Code Server Infrastructure - Bicep Template
@description('Location for all resources')
param location string = 'eastus'

@description('Environment name')
param environment string = 'production'

@description('Existing AKS cluster name')
param aksClusterName string = 'gzc-k8s-engine'

@description('Existing resource group name')
param aksResourceGroup string = 'gzc-kubernetes-rg'

@description('Swiss Key Vault name')
param keyVaultName string = 'gzc-finma-keyvault'

@description('Swiss Key Vault resource group')
param keyVaultResourceGroup string = 'gzc-finma-compliance-rg'

@description('Container Registry name')
param acrName string = 'gzcacr'

// Managed Identity for Claude Code Server
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'claude-code-identity'
  location: location
  tags: {
    environment: environment
    application: 'claude-code-server'
    managedBy: 'Azure_Infrastructure_Agent'
  }
}

// Get existing Key Vault reference
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
  scope: resourceGroup(keyVaultResourceGroup)
}

// Get existing AKS cluster
resource aksCluster 'Microsoft.ContainerService/managedClusters@2023-08-01' existing = {
  name: aksClusterName
  scope: resourceGroup(aksResourceGroup)
}

// Get existing ACR
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: acrName
}

// Note: Key Vault role assignment must be done separately via Azure CLI
// due to cross-resource group scope limitations in Bicep

// Role assignment for ACR pull
resource acrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(managedIdentity.id, containerRegistry.id, 'AcrPull')
  scope: containerRegistry
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Note: Federated identity must be configured after AKS OIDC issuer is available
// This will be done via Azure CLI after deployment

// Log Analytics workspace for monitoring
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'claude-code-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Application Insights for APM
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'claude-code-insights'
  location: location
  kind: 'other'
  properties: {
    Application_Type: 'other'
    WorkspaceResourceId: logAnalyticsWorkspace.id
  }
}

// Outputs
output managedIdentityClientId string = managedIdentity.properties.clientId
output managedIdentityResourceId string = managedIdentity.id
output logAnalyticsWorkspaceId string = logAnalyticsWorkspace.id
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey