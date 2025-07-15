#!/usr/bin/env python3
"""
Advanced Debug Processor - Log Capture & Analysis System
Independent debugging with advanced log capture and systematic analysis
"""

import os
import json
import re
import traceback
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path
import subprocess

class DebugProcessor:
    """Advanced debugging system with log capture and pattern analysis"""
    
    def __init__(self, workspace_name=None, debug_dir=None):
        self.workspace_name = workspace_name or "azure_debug"
        self.debug_dir = Path(debug_dir or "./debug_logs")
        self.debug_dir.mkdir(exist_ok=True)
        
        # Debug session tracking
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = self.debug_dir / f"debug_session_{self.session_id}.json"
        
        # Initialize session
        self.session_data = {
            'session_id': self.session_id,
            'start_time': datetime.now().isoformat(),
            'workspace_name': self.workspace_name,
            'operations': [],
            'errors': [],
            'patterns': {}
        }
    
    def capture_operation(self, operation_name, func, *args, **kwargs):
        """Capture operation execution with full debugging"""
        operation_id = f"{operation_name}_{len(self.session_data['operations'])}"
        
        operation_data = {
            'operation_id': operation_id,
            'operation_name': operation_name,
            'start_time': datetime.now().isoformat(),
            'args': str(args)[:500],  # Truncate long args
            'kwargs': str(kwargs)[:500],
            'status': 'started'
        }
        
        print(f"[DEBUG] Starting operation: {operation_name}")
        
        try:
            # Execute operation
            start_time = datetime.now()
            result = func(*args, **kwargs)
            end_time = datetime.now()
            
            # Capture success
            operation_data.update({
                'status': 'success',
                'end_time': end_time.isoformat(),
                'duration_ms': int((end_time - start_time).total_seconds() * 1000),
                'result_type': type(result).__name__,
                'result_summary': str(result)[:1000] if result else 'None'
            })
            
            print(f"[DEBUG] ✅ Operation {operation_name} completed in {operation_data['duration_ms']}ms")
            
        except Exception as e:
            # Capture error with full details
            error_data = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }
            
            operation_data.update({
                'status': 'failed',
                'end_time': datetime.now().isoformat(),
                'error': error_data
            })
            
            self.session_data['errors'].append(error_data)
            
            print(f"[DEBUG] ❌ Operation {operation_name} failed: {e}")
            
            # Re-raise for caller handling
            raise
        
        finally:
            self.session_data['operations'].append(operation_data)
            self.save_session()
        
        return result
    
    def analyze_azure_logs(self, log_content):
        """Analyze Azure operation logs for patterns and issues"""
        print(f"[DEBUG] Analyzing Azure logs ({len(log_content)} chars)...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'log_size': len(log_content),
            'patterns': {},
            'errors': [],
            'warnings': [],
            'performance': {}
        }
        
        lines = log_content.split('\n')
        
        # Extract error patterns
        error_patterns = [
            (r'Error: (.+)', 'General Errors'),
            (r'Exception: (.+)', 'Exceptions'),
            (r'Failed to (.+)', 'Operation Failures'),
            (r'Timeout (.+)', 'Timeout Issues'),
            (r'Unauthorized (.+)', 'Authentication Issues'),
            (r'ResourceNotFound (.+)', 'Resource Issues')
        ]
        
        for pattern, category in error_patterns:
            matches = []
            for line in lines:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    matches.append({
                        'line': line.strip(),
                        'match': match.group(1),
                        'timestamp': self.extract_timestamp(line)
                    })
            
            if matches:
                analysis['patterns'][category] = matches
        
        # Extract performance metrics
        perf_patterns = [
            (r'Duration: (\d+)ms', 'Duration'),
            (r'Response time: (\d+)ms', 'Response Time'),
            (r'Elapsed: (\d+\.?\d*)s', 'Elapsed Time')
        ]
        
        for pattern, metric in perf_patterns:
            values = []
            for line in lines:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    try:
                        value = float(match.group(1))
                        values.append(value)
                    except ValueError:
                        continue
            
            if values:
                analysis['performance'][metric] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values)
                }
        
        return analysis
    
    def extract_timestamp(self, log_line):
        """Extract timestamp from log line"""
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
            r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}'
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, log_line)
            if match:
                return match.group(0)
        
        return None
    
    def capture_azure_cli_debug(self, command):
        """Capture Azure CLI command with debug output"""
        print(f"[DEBUG] Executing Azure CLI: {command}")
        
        # Add debug flags to Azure CLI
        debug_command = f"az {command} --debug --output json"
        
        try:
            start_time = datetime.now()
            result = subprocess.run(
                debug_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            end_time = datetime.now()
            
            debug_data = {
                'command': command,
                'exit_code': result.returncode,
                'duration_ms': int((end_time - start_time).total_seconds() * 1000),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'timestamp': start_time.isoformat()
            }
            
            # Analyze the debug output
            if result.stderr:
                debug_data['log_analysis'] = self.analyze_azure_logs(result.stderr)
            
            # Save to file
            debug_file = self.debug_dir / f"cli_debug_{self.session_id}_{len(self.session_data['operations'])}.json"
            with open(debug_file, 'w') as f:
                json.dump(debug_data, f, indent=2)
            
            print(f"[DEBUG] CLI command completed in {debug_data['duration_ms']}ms, exit code: {result.returncode}")
            
            return debug_data
            
        except subprocess.TimeoutExpired:
            print(f"[DEBUG] ❌ CLI command timed out: {command}")
            return {'error': 'timeout', 'command': command}
        except Exception as e:
            print(f"[DEBUG] ❌ CLI command failed: {e}")
            return {'error': str(e), 'command': command}
    
    def system_diagnostics(self):
        """Run comprehensive system diagnostics"""
        print(f"[DEBUG] Running system diagnostics...")
        
        diagnostics = {
            'timestamp': datetime.now().isoformat(),
            'system': {},
            'azure': {},
            'python': {}
        }
        
        # System info
        try:
            import platform
            diagnostics['system'] = {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'architecture': platform.architecture(),
                'processor': platform.processor()
            }
        except Exception as e:
            diagnostics['system'] = {'error': str(e)}
        
        # Azure CLI version
        try:
            az_version = subprocess.run(
                'az version',
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            if az_version.returncode == 0:
                diagnostics['azure']['cli_version'] = json.loads(az_version.stdout)
            else:
                diagnostics['azure']['cli_error'] = az_version.stderr
        except Exception as e:
            diagnostics['azure']['cli_error'] = str(e)
        
        # Python packages
        try:
            import pkg_resources
            azure_packages = [
                pkg for pkg in pkg_resources.working_set 
                if 'azure' in pkg.project_name.lower()
            ]
            diagnostics['python']['azure_packages'] = [
                {'name': pkg.project_name, 'version': pkg.version}
                for pkg in azure_packages
            ]
        except Exception as e:
            diagnostics['python']['error'] = str(e)
        
        # Save diagnostics
        diag_file = self.debug_dir / f"diagnostics_{self.session_id}.json"
        with open(diag_file, 'w') as f:
            json.dump(diagnostics, f, indent=2)
        
        return diagnostics
    
    def generate_debug_report(self):
        """Generate comprehensive debug report"""
        print(f"[DEBUG] Generating debug report...")
        
        # Update session end time
        self.session_data['end_time'] = datetime.now().isoformat()
        
        # Calculate statistics
        operations = self.session_data['operations']
        successful_ops = [op for op in operations if op['status'] == 'success']
        failed_ops = [op for op in operations if op['status'] == 'failed']
        
        # Performance analysis
        if successful_ops:
            durations = [op.get('duration_ms', 0) for op in successful_ops if 'duration_ms' in op]
            if durations:
                self.session_data['patterns']['performance'] = {
                    'avg_duration_ms': sum(durations) / len(durations),
                    'min_duration_ms': min(durations),
                    'max_duration_ms': max(durations),
                    'total_operations': len(successful_ops)
                }
        
        # Error analysis
        if self.session_data['errors']:
            error_types = Counter(error['error_type'] for error in self.session_data['errors'])
            self.session_data['patterns']['error_frequency'] = dict(error_types)
        
        # Generate summary
        summary = {
            'session_summary': {
                'total_operations': len(operations),
                'successful_operations': len(successful_ops),
                'failed_operations': len(failed_ops),
                'success_rate': len(successful_ops) / len(operations) if operations else 0,
                'total_errors': len(self.session_data['errors'])
            },
            'recommendations': self.generate_recommendations()
        }
        
        self.session_data['summary'] = summary
        
        # Save final session
        self.save_session()
        
        # Create human-readable report
        report_file = self.debug_dir / f"debug_report_{self.session_id}.md"
        with open(report_file, 'w') as f:
            f.write(self.format_debug_report())
        
        print(f"[DEBUG] Debug report saved to {report_file}")
        return self.session_data
    
    def generate_recommendations(self):
        """Generate recommendations based on debugging data"""
        recommendations = []
        
        # Check error patterns
        if self.session_data['errors']:
            error_types = Counter(error['error_type'] for error in self.session_data['errors'])
            
            if 'TimeoutError' in error_types:
                recommendations.append("Consider increasing timeout values for operations")
            
            if 'AuthenticationError' in error_types:
                recommendations.append("Check Azure authentication configuration")
            
            if 'ResourceNotFoundError' in error_types:
                recommendations.append("Verify resource names and subscription access")
        
        # Check performance
        operations = self.session_data['operations']
        if operations:
            slow_ops = [op for op in operations if op.get('duration_ms', 0) > 30000]  # > 30 seconds
            if slow_ops:
                recommendations.append(f"Optimize {len(slow_ops)} slow operations (>30s)")
        
        return recommendations
    
    def format_debug_report(self):
        """Format debug report as markdown"""
        data = self.session_data
        
        report = f"""# Azure Debug Report
        
## Session: {data['session_id']}
**Workspace**: {data['workspace_name']}  
**Start Time**: {data['start_time']}  
**End Time**: {data.get('end_time', 'In Progress')}

## Summary
- **Total Operations**: {data['summary']['session_summary']['total_operations']}
- **Success Rate**: {data['summary']['session_summary']['success_rate']:.1%}
- **Total Errors**: {data['summary']['session_summary']['total_errors']}

## Operations
"""
        
        for op in data['operations']:
            status_icon = "✅" if op['status'] == 'success' else "❌"
            duration = f" ({op.get('duration_ms', 0)}ms)" if 'duration_ms' in op else ""
            report += f"- {status_icon} **{op['operation_name']}**{duration}\n"
        
        if data['errors']:
            report += "\n## Errors\n"
            for error in data['errors']:
                report += f"- **{error['error_type']}**: {error['error_message']}\n"
        
        if data['summary']['recommendations']:
            report += "\n## Recommendations\n"
            for rec in data['summary']['recommendations']:
                report += f"- {rec}\n"
        
        return report
    
    def save_session(self):
        """Save current session data"""
        with open(self.session_file, 'w') as f:
            json.dump(self.session_data, f, indent=2)

def test_debug_processor():
    """Test debug processor functionality"""
    print("=" * 60)
    print("ADVANCED DEBUG PROCESSOR TEST")
    print("=" * 60)
    
    debug = DebugProcessor("test_workspace")
    
    # Test operation capture
    def test_operation():
        time.sleep(0.1)  # Simulate work
        return {"result": "success", "value": 42}
    
    def failing_operation():
        raise ValueError("Test error for debugging")
    
    # Capture successful operation
    try:
        result = debug.capture_operation("test_success", test_operation)
        print(f"Success operation result: {result}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    # Capture failing operation
    try:
        debug.capture_operation("test_failure", failing_operation)
    except ValueError:
        print("Expected error captured successfully")
    
    # Run diagnostics
    diagnostics = debug.system_diagnostics()
    print(f"System diagnostics: {len(diagnostics)} categories")
    
    # Generate report
    report = debug.generate_debug_report()
    print(f"Debug report generated with {report['summary']['session_summary']['total_operations']} operations")
    
    return debug

if __name__ == "__main__":
    import time
    test_debug_processor()