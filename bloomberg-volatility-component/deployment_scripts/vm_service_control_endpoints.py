# VM Service Control Endpoints for Bloomberg FastAPI Server
# Deploy this to the Bloomberg VM to add service control functionality

import subprocess
import psutil
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ServiceControlResponse(BaseModel):
    success: bool
    message: str
    service_status: str
    process_info: Dict[str, Any] = {}

# Add these endpoints to your existing FastAPI application

def add_service_control_endpoints(app: FastAPI):
    """Add VM service control endpoints to existing FastAPI app"""
    
    @app.get("/api/vm/service/status")
    async def get_service_status():
        """Check if the Bloomberg API service is currently running"""
        try:
            # Check for Python processes running the Bloomberg API
            bloomberg_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
                try:
                    if proc.info['name'] == 'python.exe':
                        cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                        if 'BloombergAPI' in cmdline or 'main.py' in cmdline:
                            bloomberg_processes.append({
                                'pid': proc.info['pid'],
                                'status': proc.info['status'],
                                'cmdline': cmdline
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            service_running = len(bloomberg_processes) > 0
            
            return {
                "success": True,
                "service_running": service_running,
                "process_count": len(bloomberg_processes),
                "processes": bloomberg_processes,
                "timestamp": str(datetime.now()),
                "vm_status": "running"
            }
            
        except Exception as e:
            logger.error(f"Error checking service status: {e}")
            return {
                "success": False,
                "service_running": False,
                "error": str(e),
                "timestamp": str(datetime.now())
            }

    @app.post("/api/vm/service/start")
    async def start_service():
        """Start the Bloomberg API service if not running"""
        try:
            # First check if already running
            status = await get_service_status()
            if status["service_running"]:
                return ServiceControlResponse(
                    success=True,
                    message="Bloomberg API service is already running",
                    service_status="running",
                    process_info=status["processes"][0] if status["processes"] else {}
                )
            
            # Start the service using Windows Service Manager or direct process
            api_path = "C:\\BloombergAPI\\main.py"
            python_path = "C:\\Python311\\python.exe"
            
            if os.path.exists(api_path) and os.path.exists(python_path):
                # Try to start as Windows service first
                try:
                    result = subprocess.run([
                        "net", "start", "BloombergAPI"
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        logger.info("Bloomberg API Windows service started successfully")
                        service_method = "windows_service"
                    else:
                        raise subprocess.CalledProcessError(result.returncode, "net start")
                        
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    # Fallback to direct process start
                    logger.info("Windows service start failed, trying direct process start")
                    result = subprocess.Popen([
                        python_path, api_path
                    ], cwd="C:\\BloombergAPI")
                    service_method = "direct_process"
                    logger.info(f"Bloomberg API started as direct process with PID: {result.pid}")
                
                # Wait a moment and verify service started
                import time
                time.sleep(3)
                verification = await get_service_status()
                
                if verification["service_running"]:
                    return ServiceControlResponse(
                        success=True,
                        message=f"Bloomberg API service started successfully via {service_method}",
                        service_status="running",
                        process_info=verification["processes"][0] if verification["processes"] else {}
                    )
                else:
                    raise Exception("Service start verification failed")
                    
            else:
                raise FileNotFoundError(f"Bloomberg API files not found: {api_path} or {python_path}")
                
        except Exception as e:
            logger.error(f"Error starting Bloomberg API service: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start Bloomberg API service: {str(e)}"
            )

    @app.post("/api/vm/service/stop")
    async def stop_service():
        """Stop the Bloomberg API service"""
        try:
            # First check if running
            status = await get_service_status()
            if not status["service_running"]:
                return ServiceControlResponse(
                    success=True,
                    message="Bloomberg API service is already stopped",
                    service_status="stopped"
                )
            
            stopped_processes = []
            
            # Try to stop Windows service first
            try:
                result = subprocess.run([
                    "net", "stop", "BloombergAPI"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    logger.info("Bloomberg API Windows service stopped successfully")
                    service_method = "windows_service"
                else:
                    raise subprocess.CalledProcessError(result.returncode, "net stop")
                    
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                # Fallback to direct process termination
                logger.info("Windows service stop failed, trying direct process termination")
                
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] == 'python.exe':
                            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                            if 'BloombergAPI' in cmdline or 'main.py' in cmdline:
                                proc.terminate()
                                stopped_processes.append({
                                    'pid': proc.info['pid'],
                                    'cmdline': cmdline
                                })
                                logger.info(f"Terminated Bloomberg API process PID: {proc.info['pid']}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                service_method = "direct_process_termination"
            
            # Wait a moment and verify service stopped
            import time
            time.sleep(2)
            verification = await get_service_status()
            
            if not verification["service_running"]:
                return ServiceControlResponse(
                    success=True,
                    message=f"Bloomberg API service stopped successfully via {service_method}",
                    service_status="stopped",
                    process_info={"stopped_processes": stopped_processes}
                )
            else:
                raise Exception("Service stop verification failed")
                
        except Exception as e:
            logger.error(f"Error stopping Bloomberg API service: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to stop Bloomberg API service: {str(e)}"
            )

    @app.post("/api/vm/service/restart")
    async def restart_service():
        """Restart the Bloomberg API service"""
        try:
            # Stop first
            stop_result = await stop_service()
            if not stop_result.success:
                raise Exception(f"Failed to stop service: {stop_result.message}")
            
            # Wait a moment
            import time
            time.sleep(2)
            
            # Start again
            start_result = await start_service()
            if not start_result.success:
                raise Exception(f"Failed to start service: {start_result.message}")
            
            return ServiceControlResponse(
                success=True,
                message="Bloomberg API service restarted successfully",
                service_status="running",
                process_info=start_result.process_info
            )
            
        except Exception as e:
            logger.error(f"Error restarting Bloomberg API service: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to restart Bloomberg API service: {str(e)}"
            )

# Example usage in main.py:
# from vm_service_control_endpoints import add_service_control_endpoints
# add_service_control_endpoints(app)