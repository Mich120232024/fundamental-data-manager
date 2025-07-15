# Azure Copilot Deployment Request - FRED Metadata Collection System

## Project Overview

Dear Azure Copilot,

I need your assistance in deploying a comprehensive FRED (Federal Reserve Economic Data) metadata collection system to Azure. We have completed all the groundwork and validated collection methods for all 31 FRED API endpoints. Now we need to architect and deploy a production-grade solution in Azure.

## What We Have Completed

### 1. Full API Analysis
- ✅ All 31 FRED API endpoints tested and documented
- ✅ Rate limits understood (120 req/min, 1000 results max per call)
- ✅ Pagination patterns validated
- ✅ Complete data schemas mapped

### 2. Foundation Data Collected
- 91 sources (24.6 KB)
- 326 releases (171.6 KB)
- 8,000+ tags (1.09 MB)
- 5,183 categories with hierarchy (1.81 MB)
- 150 series sample with metadata (231.9 KB)

### 3. Collection Methods Proven
- Single API calls for complete datasets
- Pagination with offset for large results
- Hierarchical traversal for categories
- Graph relationships for 10.4M tag connections
- Adaptive rate limiting (0.5-1.0s delays)

### 4. Scale Requirements
- ~800,000 total series to collect
- ~3.3 million API calls needed
- 10-15 GB uncompressed data
- 3-5 GB compressed in Delta Lake
- 45-50 hours collection time with 10 parallel workers

## Azure Architecture Requirements

### 1. Data Storage
- **Delta Lake** on Azure Data Lake Storage Gen2
- Hierarchical namespace enabled
- Tables partitioned by frequency/date
- Z-ordering for query optimization

### 2. Collection Orchestration
Please design:
- **Azure Data Factory** pipelines for orchestration
- **Azure Functions** for API collection workers
- **Event Grid** for workflow coordination
- **Service Bus** for work queue management

### 3. Stream Processing
Need real-time processing for:
- **Event Hubs** for API response streaming
- **Stream Analytics** for data transformation
- Real-time Delta Lake writes
- Checkpoint management

### 4. Automated Maintenance
Critical requirement - calendar-based automation:
- **Daily**: Check `/series/updates` for changed series
- **Release Schedule**: Monitor 326 releases for their specific calendar
- **Incremental Updates**: Only refresh changed data
- **Automatic Retries**: Handle rate limits and failures

### 5. Monitoring & Alerting
- Collection progress dashboards
- API rate limit monitoring
- Data quality validation
- Missing relationship detection
- Cost optimization tracking

## Specific Questions for Copilot

### 1. Resource Setup
What Azure resources should I create and in what order? Please provide:
- Resource group structure
- Storage account configuration
- Networking requirements
- Security/RBAC setup
- Managed identities configuration

### 2. Event-Driven Architecture
How should I implement:
- Release calendar monitoring (326 different schedules)
- Automatic collection triggers based on FRED release dates
- Event Hub partitioning strategy for 800k series
- Stream Analytics queries for data transformation

### 3. Cost Optimization
Given our scale (3.3M API calls, 50 hours runtime):
- Optimal Function App pricing tier?
- Stream Analytics streaming units needed?
- Storage redundancy recommendations?
- Estimated monthly costs?

### 4. Implementation Steps
Please provide detailed steps for:
1. Infrastructure deployment (IaC templates?)
2. Initial data load strategy
3. Incremental update implementation
4. Monitoring setup
5. Go-live checklist

### 5. Best Practices
- How to handle the 1000-result API limit efficiently?
- Optimal parallelization (10 workers? more?)
- Delta Lake optimization schedules
- Backup and disaster recovery

## Deliverables Needed

1. **Architecture Diagram** showing all components
2. **ARM/Bicep Templates** for resource deployment
3. **Data Factory Pipeline JSONs**
4. **Azure Function Code** structure
5. **Stream Analytics Queries**
6. **Monitoring Dashboards** configuration
7. **Cost Estimate** breakdown
8. **Timeline** for implementation

## Additional Context

- We already have the Python collection code tested
- API key is available and working
- All endpoint parameters documented
- Complete data model designed
- No observations data needed (metadata only)

Please provide a comprehensive deployment plan that leverages Azure's best practices for this large-scale data collection system. Focus especially on the automated maintenance based on FRED's release calendar - this is critical for keeping data current.

Thank you for your assistance in bringing this project to production on Azure!

---
*All documentation and code samples are available in the attached project files*