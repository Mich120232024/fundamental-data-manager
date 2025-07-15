#!/usr/bin/env python3
"""
Azure Deployment Monitoring
Track deployments, health, and performance
"""

import os
import json
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.resource import ResourceManagementClient
from cosmos_db_manager import get_db_manager

class AzureMonitor:
    """Monitor Azure deployments without complexity"""
    
    def __init__(self):
        self.subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
        self.resource_group = os.environ.get('AZURE_RESOURCE_GROUP', 'research-analytics-rg')
        
        if self.subscription_id:
            self.credential = DefaultAzureCredential()
            self.web_client = WebSiteManagementClient(self.credential, self.subscription_id)
            self.monitor_client = MonitorManagementClient(self.credential, self.subscription_id)
            self.resource_client = ResourceManagementClient(self.credential, self.subscription_id)
        else:
            print("⚠️  AZURE_SUBSCRIPTION_ID not set - using mock mode")
            self.credential = None
    
    def check_function_apps(self):
        """Check status of all Function Apps"""
        if not self.credential:
            return self._mock_function_status()
            
        apps = []
        try:
            for app in self.web_client.web_apps.list_by_resource_group(self.resource_group):
                if app.kind and 'functionapp' in app.kind:
                    # Get app status
                    status = 'running' if app.state == 'Running' else app.state
                    
                    # Get recent logs if available
                    recent_errors = self._get_recent_errors(app.name)
                    
                    apps.append({
                        'name': app.name,
                        'status': status,
                        'url': f"https://{app.default_host_name}",
                        'runtime': app.site_config.linux_fx_version or app.site_config.windows_fx_version,
                        'last_modified': app.last_modified_time_utc.isoformat() if app.last_modified_time_utc else None,
                        'recent_errors': recent_errors
                    })
        except Exception as e:
            return {'error': str(e), 'apps': []}
            
        return {'apps': apps, 'total': len(apps)}
    
    def check_deployment_status(self, app_name):
        """Check recent deployments for an app"""
        if not self.credential:
            return self._mock_deployment_status(app_name)
            
        try:
            deployments = self.web_client.web_apps.list_deployments(
                self.resource_group, 
                app_name
            )
            
            recent = []
            for deployment in deployments:
                recent.append({
                    'id': deployment.id,
                    'status': deployment.status,
                    'author': deployment.author,
                    'message': deployment.message,
                    'timestamp': deployment.received_time.isoformat() if deployment.received_time else None,
                    'active': deployment.active
                })
                
            return recent[:5]  # Last 5 deployments
        except:
            return []
    
    def get_metrics(self, app_name, hours=24):
        """Get app metrics for monitoring"""
        if not self.credential:
            return self._mock_metrics()
            
        try:
            # Resource ID for the function app
            resource_id = f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.Web/sites/{app_name}"
            
            # Time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Get metrics
            metrics = self.monitor_client.metrics.list(
                resource_id,
                timespan=f"{start_time}/{end_time}",
                interval='PT1H',
                metricnames='FunctionExecutionCount,FunctionExecutionUnits,Http5xx',
                aggregation='Total'
            )
            
            result = {}
            for metric in metrics.value:
                result[metric.name.value] = {
                    'unit': metric.unit,
                    'data': [
                        {
                            'timestamp': ts.time_stamp.isoformat(),
                            'value': ts.total
                        }
                        for ts in metric.timeseries[0].data if ts.total is not None
                    ]
                }
                
            return result
        except:
            return {}
    
    def _get_recent_errors(self, app_name):
        """Get recent error count"""
        # Simplified - would query app insights in production
        return 0
    
    def _mock_function_status(self):
        """Mock data for testing without Azure connection"""
        return {
            'apps': [
                {
                    'name': 'func-research-analytics',
                    'status': 'running',
                    'url': 'https://func-research-analytics.azurewebsites.net',
                    'runtime': 'python|3.9',
                    'last_modified': datetime.now().isoformat(),
                    'recent_errors': 0
                }
            ],
            'total': 1
        }
    
    def _mock_deployment_status(self, app_name):
        """Mock deployment data"""
        return [
            {
                'id': 'deploy_001',
                'status': 'Success',
                'author': 'ENGINEERING',
                'message': 'Deployed new message processor',
                'timestamp': datetime.now().isoformat(),
                'active': True
            }
        ]
    
    def _mock_metrics(self):
        """Mock metrics data"""
        return {
            'FunctionExecutionCount': {
                'unit': 'Count',
                'data': [{'timestamp': datetime.now().isoformat(), 'value': 150}]
            }
        }
    
    def log_monitoring_data(self):
        """Log monitoring data to Cosmos DB"""
        monitoring_data = {
            'id': f"azure_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'type': 'AZURE_MONITORING',
            'timestamp': datetime.now().isoformat() + 'Z',
            'function_apps': self.check_function_apps(),
            'partitionKey': 'azure_monitoring'
        }
        
        try:
            db = get_db_manager()
            logs = db.database.get_container_client('logs')
            logs.create_item(body=monitoring_data)
            return True
        except:
            return False

# CLI interface
if __name__ == "__main__":
    import sys
    
    monitor = AzureMonitor()
    
    if len(sys.argv) < 2:
        print("Azure Monitor")
        print("Usage:")
        print("  azure_monitor.py status              # Check all function apps")
        print("  azure_monitor.py deployments <app>   # Check app deployments")
        print("  azure_monitor.py metrics <app>       # Get app metrics")
        print("  azure_monitor.py log                 # Log to Cosmos DB")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        result = monitor.check_function_apps()
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"🚀 AZURE FUNCTION APPS ({result['total']} total)")
            print("-" * 60)
            for app in result['apps']:
                status_icon = "✅" if app['status'] == 'running' else "⚠️"
                print(f"{status_icon} {app['name']}")
                print(f"   Status: {app['status']}")
                print(f"   URL: {app['url']}")
                print(f"   Runtime: {app['runtime']}")
                if app['recent_errors'] > 0:
                    print(f"   ⚠️  Recent errors: {app['recent_errors']}")
    
    elif cmd == "deployments" and len(sys.argv) >= 3:
        app_name = sys.argv[2]
        deployments = monitor.check_deployment_status(app_name)
        print(f"📦 DEPLOYMENTS for {app_name}")
        print("-" * 60)
        for deployment in deployments:
            status_icon = "✅" if deployment['status'] == 'Success' else "❌"
            active = "🟢 ACTIVE" if deployment['active'] else ""
            print(f"{status_icon} {deployment['message']} {active}")
            print(f"   By: {deployment['author']} at {deployment['timestamp']}")
    
    elif cmd == "metrics" and len(sys.argv) >= 3:
        app_name = sys.argv[2]
        metrics = monitor.get_metrics(app_name)
        print(f"📊 METRICS for {app_name}")
        print("-" * 60)
        for metric_name, data in metrics.items():
            print(f"{metric_name} ({data['unit']})")
            for point in data['data'][-5:]:  # Last 5 data points
                print(f"   {point['timestamp']}: {point['value']}")
    
    elif cmd == "log":
        if monitor.log_monitoring_data():
            print("✅ Monitoring data logged to Cosmos DB")
        else:
            print("❌ Failed to log monitoring data")