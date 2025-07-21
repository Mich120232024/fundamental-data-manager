# Azure VM Control Endpoints for Bloomberg FastAPI Server
# Deploy this to enable Azure VM start/stop functionality

import subprocess
import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

class VMControlResponse(BaseModel):
    success: bool
    message: str
    vm_status: str
    vm_info: Dict[str, Any] = {}

class AzureVMController:
    """Azure VM control using Azure CLI"""
    
    def __init__(self):
        self.resource_group = "bloomberg-terminal-rg"
        self.vm_name = "bloomberg-vm-02"
    
    async def get_vm_status(self) -> Dict[str, Any]:
        """Get current VM status using Azure CLI"""
        try:
            # Check if Azure CLI is available
            result = await self._run_azure_command([
                "az", "vm", "show", 
                "--resource-group", self.resource_group,
                "--name", self.vm_name,
                "--show-details",
                "--output", "json"
            ])
            
            if result["success"]:
                vm_data = json.loads(result["output"])
                return {
                    "success": True,
                    "vm_status": vm_data.get("powerState", "unknown"),
                    "vm_size": vm_data.get("hardwareProfile", {}).get("vmSize"),
                    "location": vm_data.get("location"),
                    "public_ip": vm_data.get("publicIps"),
                    "private_ip": vm_data.get("privateIps"),
                    "provisioning_state": vm_data.get("provisioningState"),
                    "resource_group": self.resource_group,
                    "vm_name": self.vm_name
                }
            else:
                return {
                    "success": False,
                    "error": result["error"],
                    "vm_status": "unknown"
                }
                
        except Exception as e:
            logger.error(f"Error getting VM status: {e}")
            return {
                "success": False,
                "error": str(e),
                "vm_status": "unknown"
            }
    
    async def start_vm(self) -> Dict[str, Any]:
        """Start the Azure VM"""
        try:
            logger.info(f"Starting Azure VM: {self.vm_name}")
            
            result = await self._run_azure_command([
                "az", "vm", "start",
                "--resource-group", self.resource_group,
                "--name", self.vm_name,
                "--output", "json"
            ], timeout=300)  # 5 minutes timeout for VM start
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"VM {self.vm_name} started successfully",
                    "vm_status": "running"
                }
            else:
                return {
                    "success": False,
                    "error": result["error"],
                    "message": f"Failed to start VM {self.vm_name}"
                }
                
        except Exception as e:
            logger.error(f"Error starting VM: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to start VM {self.vm_name}"
            }
    
    async def stop_vm(self) -> Dict[str, Any]:
        """Stop the Azure VM"""
        try:
            logger.info(f"Stopping Azure VM: {self.vm_name}")
            
            result = await self._run_azure_command([
                "az", "vm", "deallocate",
                "--resource-group", self.resource_group,
                "--name", self.vm_name,
                "--output", "json"
            ], timeout=300)  # 5 minutes timeout for VM stop
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"VM {self.vm_name} stopped successfully",
                    "vm_status": "deallocated"
                }
            else:
                return {
                    "success": False,
                    "error": result["error"],
                    "message": f"Failed to stop VM {self.vm_name}"
                }
                
        except Exception as e:
            logger.error(f"Error stopping VM: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to stop VM {self.vm_name}"
            }
    
    async def restart_vm(self) -> Dict[str, Any]:
        """Restart the Azure VM"""
        try:
            logger.info(f"Restarting Azure VM: {self.vm_name}")
            
            result = await self._run_azure_command([
                "az", "vm", "restart",
                "--resource-group", self.resource_group,
                "--name", self.vm_name,
                "--output", "json"
            ], timeout=300)  # 5 minutes timeout for VM restart
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"VM {self.vm_name} restarted successfully",
                    "vm_status": "running"
                }
            else:
                return {
                    "success": False,
                    "error": result["error"],
                    "message": f"Failed to restart VM {self.vm_name}"
                }
                
        except Exception as e:
            logger.error(f"Error restarting VM: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to restart VM {self.vm_name}"
            }
    
    async def _run_azure_command(self, command: list, timeout: int = 60) -> Dict[str, Any]:
        """Run Azure CLI command with timeout"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            if process.returncode == 0:
                return {
                    "success": True,
                    "output": stdout.decode().strip(),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "output": None,
                    "error": stderr.decode().strip()
                }
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "output": None,
                "error": f"Command timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e)
            }

def add_azure_vm_control_endpoints(app: FastAPI):
    """Add Azure VM control endpoints to existing FastAPI app"""
    
    vm_controller = AzureVMController()
    
    @app.get("/api/azure/vm/status")
    async def get_azure_vm_status():
        """Get Azure VM status"""
        try:
            result = await vm_controller.get_vm_status()
            return result
        except Exception as e:
            logger.error(f"Error getting Azure VM status: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get Azure VM status: {str(e)}"
            )
    
    @app.post("/api/azure/vm/start")
    async def start_azure_vm():
        """Start the Azure VM"""
        try:
            # First check if VM is already running
            status = await vm_controller.get_vm_status()
            if status.get("vm_status") == "VM running":
                return VMControlResponse(
                    success=True,
                    message="Azure VM is already running",
                    vm_status="running",
                    vm_info=status
                )
            
            result = await vm_controller.start_vm()
            
            return VMControlResponse(
                success=result["success"],
                message=result["message"],
                vm_status=result.get("vm_status", "unknown"),
                vm_info=result
            )
            
        except Exception as e:
            logger.error(f"Error starting Azure VM: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start Azure VM: {str(e)}"
            )
    
    @app.post("/api/azure/vm/stop")
    async def stop_azure_vm():
        """Stop the Azure VM"""
        try:
            # First check if VM is already stopped
            status = await vm_controller.get_vm_status()
            if status.get("vm_status") in ["VM deallocated", "VM stopped"]:
                return VMControlResponse(
                    success=True,
                    message="Azure VM is already stopped",
                    vm_status="deallocated",
                    vm_info=status
                )
            
            result = await vm_controller.stop_vm()
            
            return VMControlResponse(
                success=result["success"],
                message=result["message"],
                vm_status=result.get("vm_status", "unknown"),
                vm_info=result
            )
            
        except Exception as e:
            logger.error(f"Error stopping Azure VM: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to stop Azure VM: {str(e)}"
            )
    
    @app.post("/api/azure/vm/restart")
    async def restart_azure_vm():
        """Restart the Azure VM"""
        try:
            result = await vm_controller.restart_vm()
            
            return VMControlResponse(
                success=result["success"],
                message=result["message"],
                vm_status=result.get("vm_status", "unknown"),
                vm_info=result
            )
            
        except Exception as e:
            logger.error(f"Error restarting Azure VM: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to restart Azure VM: {str(e)}"
            )

# Example usage in main.py:
# from azure_vm_control_endpoints import add_azure_vm_control_endpoints
# add_azure_vm_control_endpoints(app)