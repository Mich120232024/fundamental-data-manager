#!/usr/bin/env python3
"""
Azure Infrastructure Agent - Test Runner
Runs all tools and validates functionality before deployment
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from azure_auth import AzureAuthenticator, test_authentication
    from synapse_control import SynapseController, test_synapse_control
    from debug_processor import DebugProcessor, test_debug_processor
    from azure_mcp_tools import AzureMCPTools, test_azure_mcp_tools
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required modules are in the same directory")
    sys.exit(1)

class AzureToolsTestRunner:
    """Comprehensive test runner for all Azure tools"""
    
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'test_session': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'tests': {},
            'summary': {}
        }
        
        self.results_dir = Path("./test_results")
        self.results_dir.mkdir(exist_ok=True)
    
    def check_prerequisites(self):
        """Check if Azure CLI and Python packages are available"""
        print("🔍 Checking prerequisites...")
        
        prereq_results = {
            'azure_cli': False,
            'python_packages': {},
            'environment_vars': {}
        }
        
        # Check Azure CLI
        try:
            result = subprocess.run(['az', 'version'], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                prereq_results['azure_cli'] = True
                print("✅ Azure CLI is available")
            else:
                print("❌ Azure CLI not working properly")
        except Exception as e:
            print(f"❌ Azure CLI not found: {e}")
        
        # Check Python packages
        required_packages = [
            'azure-identity',
            'azure-mgmt-resource',
            'azure-mgmt-storage',
            'azure-synapse-artifacts',
            'azure-cosmos'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '.'))
                prereq_results['python_packages'][package] = True
                print(f"✅ {package} available")
            except ImportError:
                prereq_results['python_packages'][package] = False
                print(f"❌ {package} not found")
        
        # Check environment variables
        env_vars = ['AZURE_SUBSCRIPTION_ID', 'AZURE_TENANT_ID']
        for var in env_vars:
            if os.getenv(var):
                prereq_results['environment_vars'][var] = True
                print(f"✅ {var} is set")
            else:
                prereq_results['environment_vars'][var] = False
                print(f"⚠️ {var} not set")
        
        return prereq_results
    
    def test_azure_authentication(self):
        """Test Azure authentication module"""
        print("\n" + "="*50)
        print("🔐 TESTING AZURE AUTHENTICATION")
        print("="*50)
        
        try:
            # Run authentication test
            auth_success = test_authentication()
            
            self.test_results['tests']['azure_authentication'] = {
                'status': 'success' if auth_success else 'failed',
                'module': 'azure_auth.py',
                'test_function': 'test_authentication()'
            }
            
            return auth_success
            
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            self.test_results['tests']['azure_authentication'] = {
                'status': 'failed',
                'error': str(e),
                'module': 'azure_auth.py'
            }
            return False
    
    def test_synapse_control(self):
        """Test Synapse control module"""
        print("\n" + "="*50)
        print("🏗️ TESTING SYNAPSE CONTROL")
        print("="*50)
        
        try:
            # Get workspace name from environment or use default
            workspace_name = os.getenv('SYNAPSE_WORKSPACE_NAME', 'MTWS_Synapse')
            
            # Run Synapse test
            synapse_status = test_synapse_control(workspace_name)
            
            self.test_results['tests']['synapse_control'] = {
                'status': 'success' if synapse_status else 'failed',
                'module': 'synapse_control.py',
                'workspace_name': workspace_name,
                'test_function': 'test_synapse_control()'
            }
            
            return bool(synapse_status)
            
        except Exception as e:
            print(f"❌ Synapse control test failed: {e}")
            self.test_results['tests']['synapse_control'] = {
                'status': 'failed',
                'error': str(e),
                'module': 'synapse_control.py'
            }
            return False
    
    def test_debug_processor(self):
        """Test debug processor module"""
        print("\n" + "="*50)
        print("🐛 TESTING DEBUG PROCESSOR")
        print("="*50)
        
        try:
            # Run debug processor test
            debug_instance = test_debug_processor()
            
            self.test_results['tests']['debug_processor'] = {
                'status': 'success' if debug_instance else 'failed',
                'module': 'debug_processor.py',
                'test_function': 'test_debug_processor()'
            }
            
            return bool(debug_instance)
            
        except Exception as e:
            print(f"❌ Debug processor test failed: {e}")
            self.test_results['tests']['debug_processor'] = {
                'status': 'failed',
                'error': str(e),
                'module': 'debug_processor.py'
            }
            return False
    
    def test_azure_mcp_tools(self):
        """Test Azure MCP tools module"""
        print("\n" + "="*50)
        print("🛠️ TESTING AZURE MCP TOOLS")
        print("="*50)
        
        try:
            # Run MCP tools test
            mcp_results = test_azure_mcp_tools()
            
            # Count successful tools
            successful_tools = sum(1 for result in mcp_results.values() if 'error' not in result)
            total_tools = len(mcp_results)
            
            self.test_results['tests']['azure_mcp_tools'] = {
                'status': 'success' if successful_tools == total_tools else 'partial',
                'module': 'azure_mcp_tools.py',
                'successful_tools': successful_tools,
                'total_tools': total_tools,
                'success_rate': successful_tools / total_tools if total_tools > 0 else 0,
                'test_function': 'test_azure_mcp_tools()'
            }
            
            return successful_tools > 0
            
        except Exception as e:
            print(f"❌ Azure MCP tools test failed: {e}")
            self.test_results['tests']['azure_mcp_tools'] = {
                'status': 'failed',
                'error': str(e),
                'module': 'azure_mcp_tools.py'
            }
            return False
    
    def run_integration_test(self):
        """Run integration test using multiple tools together"""
        print("\n" + "="*50)
        print("🔗 TESTING INTEGRATION")
        print("="*50)
        
        try:
            # Test 1: Authentication + MCP Tools
            print("Testing Authentication + MCP Tools integration...")
            
            auth = AzureAuthenticator()
            if not auth.authenticate():
                raise Exception("Authentication failed")
            
            tools = AzureMCPTools()
            access_result = tools.verify_access()
            
            if access_result.get('overall_status') != 'success':
                raise Exception("Access verification failed")
            
            # Test 2: MCP Tools + Debug Processor
            print("Testing MCP Tools + Debug Processor integration...")
            
            debug = DebugProcessor("integration_test")
            
            # Capture MCP tool execution in debug processor
            def test_mcp_operation():
                return tools.execute_tool('list_resources')
            
            result = debug.capture_operation("mcp_list_resources", test_mcp_operation)
            
            if not result:
                raise Exception("MCP operation capture failed")
            
            self.test_results['tests']['integration'] = {
                'status': 'success',
                'tests_completed': ['auth_mcp', 'mcp_debug'],
                'description': 'Multi-module integration test'
            }
            
            print("✅ Integration tests passed")
            return True
            
        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            self.test_results['tests']['integration'] = {
                'status': 'failed',
                'error': str(e),
                'description': 'Multi-module integration test'
            }
            return False
    
    def generate_summary(self):
        """Generate test summary and recommendations"""
        tests = self.test_results['tests']
        
        successful_tests = sum(1 for test in tests.values() if test.get('status') == 'success')
        partial_tests = sum(1 for test in tests.values() if test.get('status') == 'partial')
        failed_tests = sum(1 for test in tests.values() if test.get('status') == 'failed')
        total_tests = len(tests)
        
        self.test_results['summary'] = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'partial_tests': partial_tests,
            'failed_tests': failed_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0,
            'overall_status': 'success' if failed_tests == 0 else 'partial' if successful_tests > 0 else 'failed'
        }
        
        # Generate recommendations
        recommendations = []
        
        if failed_tests > 0:
            recommendations.append("Review failed tests and check Azure credentials/permissions")
        
        if partial_tests > 0:
            recommendations.append("Some tools have limited functionality - check specific requirements")
        
        if successful_tests == total_tests:
            recommendations.append("All tests passed - tooling ready for deployment")
        
        self.test_results['recommendations'] = recommendations
    
    def save_results(self):
        """Save test results to file"""
        results_file = self.results_dir / f"test_results_{self.test_results['test_session']}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Test results saved to: {results_file}")
        return results_file
    
    def print_summary(self):
        """Print test summary to console"""
        summary = self.test_results['summary']
        
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        print(f"Total Tests: {summary['total_tests']}")
        print(f"✅ Successful: {summary['successful_tests']}")
        print(f"⚠️ Partial: {summary['partial_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Overall Status: {summary['overall_status'].upper()}")
        
        if self.test_results.get('recommendations'):
            print("\n🎯 RECOMMENDATIONS:")
            for rec in self.test_results['recommendations']:
                print(f"- {rec}")
        
        print("\n📋 DETAILED RESULTS:")
        for test_name, test_result in self.test_results['tests'].items():
            status_icon = "✅" if test_result['status'] == 'success' else "⚠️" if test_result['status'] == 'partial' else "❌"
            print(f"{status_icon} {test_name}: {test_result['status']}")
            if 'error' in test_result:
                print(f"   Error: {test_result['error']}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Azure Infrastructure Agent Tool Tests")
        print(f"Session: {self.test_results['test_session']}")
        
        # Prerequisites
        prereq_results = self.check_prerequisites()
        self.test_results['prerequisites'] = prereq_results
        
        # Run individual tests
        test_sequence = [
            ('Azure Authentication', self.test_azure_authentication),
            ('Debug Processor', self.test_debug_processor),
            ('Azure MCP Tools', self.test_azure_mcp_tools),
            ('Synapse Control', self.test_synapse_control),
            ('Integration Test', self.run_integration_test)
        ]
        
        for test_name, test_func in test_sequence:
            try:
                print(f"\n🔄 Running {test_name}...")
                test_func()
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                self.test_results['tests'][test_name.lower().replace(' ', '_')] = {
                    'status': 'failed',
                    'error': f"Test crashed: {e}"
                }
        
        # Generate summary and save results
        self.generate_summary()
        self.save_results()
        self.print_summary()
        
        return self.test_results

def main():
    """Main test execution"""
    runner = AzureToolsTestRunner()
    results = runner.run_all_tests()
    
    # Exit with appropriate code
    if results['summary']['overall_status'] == 'success':
        print("\n🎉 All tests passed! Tools are ready for use.")
        sys.exit(0)
    elif results['summary']['overall_status'] == 'partial':
        print("\n⚠️ Some tests passed. Review partial functionality.")
        sys.exit(1)
    else:
        print("\n💥 Tests failed. Check configuration and credentials.")
        sys.exit(2)

if __name__ == "__main__":
    main()