#!/usr/bin/env python3
"""
System Health Monitoring
Minimalistic health checks for all components
"""

import requests
import subprocess
from datetime import datetime
from cosmos_db_manager import get_db_manager
import time

class SystemHealth:
    """Monitor system health without bloat"""
    
    def __init__(self):
        self.checks = []
        
    def check_cosmos_db(self):
        """Check Cosmos DB connectivity"""
        start = time.time()
        try:
            db = get_db_manager()
            containers = list(db.database.list_containers())
            return {
                'component': 'Cosmos DB',
                'status': 'healthy',
                'response_time': f"{(time.time() - start)*1000:.0f}ms",
                'containers': len(containers)
            }
        except Exception as e:
            return {
                'component': 'Cosmos DB',
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_dashboard(self):
        """Check dashboard availability"""
        try:
            response = requests.get('http://localhost:5001/api/containers', timeout=5)
            return {
                'component': 'Dashboard',
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_code': response.status_code
            }
        except:
            return {
                'component': 'Dashboard',
                'status': 'offline'
            }
    
    def check_disk_space(self):
        """Check available disk space"""
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                return {
                    'component': 'Disk Space',
                    'status': 'healthy',
                    'used': parts[2],
                    'available': parts[3],
                    'usage': parts[4]
                }
        except:
            return {
                'component': 'Disk Space',
                'status': 'unknown'
            }
    
    def check_python_env(self):
        """Check Python environment"""
        try:
            result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
            return {
                'component': 'Python',
                'status': 'healthy',
                'version': result.stdout.strip()
            }
        except:
            return {
                'component': 'Python',
                'status': 'unhealthy'
            }
    
    def run_all_checks(self):
        """Run all health checks"""
        self.checks = [
            self.check_cosmos_db(),
            self.check_dashboard(),
            self.check_disk_space(),
            self.check_python_env()
        ]
        
        # Calculate overall health
        unhealthy = sum(1 for check in self.checks if check['status'] != 'healthy')
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy' if unhealthy == 0 else f'{len(self.checks) - unhealthy}/{len(self.checks)} healthy',
            'checks': self.checks
        }
    
    def log_health(self):
        """Log health status to Cosmos DB"""
        health_data = self.run_all_checks()
        
        try:
            db = get_db_manager()
            logs = db.database.get_container_client('logs')
            
            health_data.update({
                'id': f"health_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'type': 'SYSTEM_HEALTH',
                'logType': 'HEALTH_CHECK',
                'partitionKey': 'system_health'
            })
            
            logs.create_item(body=health_data)
            return True
        except:
            return False

# CLI interface
if __name__ == "__main__":
    import sys
    
    health = SystemHealth()
    
    if len(sys.argv) > 1 and sys.argv[1] == "log":
        # Log to database
        if health.log_health():
            print("✅ Health check logged to database")
        else:
            print("❌ Failed to log health check")
    else:
        # Display health status
        status = health.run_all_checks()
        
        print(f"🏥 SYSTEM HEALTH CHECK - {status['timestamp']}")
        print(f"Overall: {status['overall_status']}")
        print("-" * 50)
        
        for check in status['checks']:
            icon = "✅" if check['status'] == 'healthy' else "❌"
            print(f"{icon} {check['component']}: {check['status']}")
            
            # Show additional details
            for key, value in check.items():
                if key not in ['component', 'status']:
                    print(f"   {key}: {value}")