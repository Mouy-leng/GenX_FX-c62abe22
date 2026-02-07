"""
Windows Service Manager
Provides Windows service and task scheduler integration for Python startup management
Enables automatic startup on boot and system service installation for A6-9V projects
"""

import os
import sys
import subprocess
import time
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET


class WindowsServiceManager:
    """
    Windows Service and Task Scheduler Manager
    Handles installation and management of Windows services and scheduled tasks
    """
    
    def __init__(self, config_path: str = "python_startup_config.yaml"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.service_name = "A6-9V-Python-Manager"
        self.service_display_name = "A6-9V Python Application Manager"
        self.service_description = "Manages Python applications for A6-9V organization"
        
        # Get current script directory
        self.script_dir = Path(__file__).parent.absolute()
        self.startup_manager_path = self.script_dir / "python_startup_manager.py"
        
        # Performance: Cache service status to avoid repeated subprocess calls
        self._service_status_cache = None
        self._service_status_cache_time = None
        self._cache_ttl = 5  # Cache for 5 seconds
        
    def check_admin_privileges(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def run_as_admin(self, command: List[str]) -> bool:
        """Run command with administrator privileges"""
        try:
            import ctypes
            # Convert command list to string
            cmd_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in command)
            
            # Run with elevated privileges
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", command[0], ' '.join(command[1:]), None, 1
            )
            return result > 32
        except Exception as e:
            self.logger.error(f"Failed to run as admin: {e}")
            return False
    
    def create_service_script(self) -> str:
        """Create Windows service script"""
        service_script_content = f'''"""
Windows Service for A6-9V Python Startup Manager
Auto-generated service script
"""

import sys
import os
import time
import logging
import servicemanager
import socket
import win32event
import win32service
import win32serviceutil
from pathlib import Path

# Add the script directory to path
script_dir = Path(r"{self.script_dir}")
sys.path.insert(0, str(script_dir))

from python_startup_manager import PythonStartupManager


class A69VPythonManagerService(win32serviceutil.ServiceFramework):
    _svc_name_ = "{self.service_name}"
    _svc_display_name_ = "{self.service_display_name}"
    _svc_description_ = "{self.service_description}"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.startup_manager = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(script_dir / 'logs' / 'service.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('A69VService')
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.logger.info("Service stop requested")
        
        if self.startup_manager:
            self.startup_manager.stop_manager()
        
        win32event.SetEvent(self.hWaitStop)
    
    def SvcDoRun(self):
        try:
            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                servicemanager.PYS_SERVICE_STARTED,
                                (self._svc_name_, ''))
            
            self.logger.info("A6-9V Python Manager Service starting...")
            
            # Create and start the startup manager
            self.startup_manager = PythonStartupManager(r"{self.script_dir / self.config_path}")
            self.startup_manager.start_manager()
            
            self.logger.info("A6-9V Python Manager Service started successfully")
            
            # Wait for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            self.logger.error(f"Service error: {{e}}")
            servicemanager.LogErrorMsg(f"Service error: {{e}}")


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(A69VPythonManagerService)
'''
        
        service_script_path = self.script_dir / "a69v_service.py"
        with open(service_script_path, 'w') as f:
            f.write(service_script_content)
        
        return str(service_script_path)
    
    def install_service(self) -> bool:
        """Install Windows service"""
        if not self.check_admin_privileges():
            self.logger.error("Administrator privileges required to install service")
            print("Please run as Administrator to install the service.")
            return False
        
        try:
            self.logger.info("Installing Windows service...")
            
            # Create service script
            service_script_path = self.create_service_script()
            
            # Install pywin32 if not available
            self.ensure_pywin32_installed()
            
            # Install service
            cmd = [
                sys.executable, service_script_path, "install"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Service installed successfully")
                
                # Configure service to start automatically
                self.configure_service_startup()
                return True
            else:
                self.logger.error(f"Service installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error installing service: {e}")
            return False
    
    def uninstall_service(self) -> bool:
        """Uninstall Windows service"""
        if not self.check_admin_privileges():
            self.logger.error("Administrator privileges required to uninstall service")
            print("Please run as Administrator to uninstall the service.")
            return False
        
        try:
            self.logger.info("Uninstalling Windows service...")
            
            # Stop service first
            self.stop_service()
            
            service_script_path = self.script_dir / "a69v_service.py"
            if service_script_path.exists():
                cmd = [sys.executable, str(service_script_path), "remove"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info("Service uninstalled successfully")
                    
                    # Clean up service script
                    service_script_path.unlink()
                    return True
                else:
                    self.logger.error(f"Service uninstallation failed: {result.stderr}")
                    return False
            else:
                self.logger.warning("Service script not found, attempting direct removal")
                return self.remove_service_direct()
                
        except Exception as e:
            self.logger.error(f"Error uninstalling service: {e}")
            return False
    
    def remove_service_direct(self) -> bool:
        """Remove service directly using sc command"""
        try:
            cmd = ["sc", "delete", self.service_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Service removed successfully")
                return True
            else:
                self.logger.error(f"Direct service removal failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing service directly: {e}")
            return False
    
    def start_service(self) -> bool:
        """Start the Windows service"""
        try:
            cmd = ["sc", "start", self.service_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Invalidate cache after service state change
            self._service_status_cache = None
            
            if result.returncode == 0:
                self.logger.info("Service started successfully")
                return True
            else:
                self.logger.error(f"Failed to start service: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting service: {e}")
            return False
    
    def stop_service(self) -> bool:
        """Stop the Windows service"""
        try:
            cmd = ["sc", "stop", self.service_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Invalidate cache after service state change
            self._service_status_cache = None
            
            if result.returncode == 0:
                self.logger.info("Service stopped successfully")
                return True
            else:
                self.logger.warning(f"Service stop command result: {result.stderr}")
                # Service might not be running, which is okay
                return True
                
        except Exception as e:
            self.logger.error(f"Error stopping service: {e}")
            return False
    
    def get_service_status(self, use_cache: bool = True) -> str:
        """Get Windows service status with optional caching to reduce subprocess overhead"""
        # Check cache first if enabled
        if use_cache and self._service_status_cache is not None:
            if self._service_status_cache_time:
                cache_age = time.time() - self._service_status_cache_time
                if cache_age < self._cache_ttl:
                    return self._service_status_cache
        
        try:
            cmd = ["sc", "query", self.service_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            status = "error"
            if result.returncode == 0:
                output = result.stdout
                if "RUNNING" in output:
                    status = "running"
                elif "STOPPED" in output:
                    status = "stopped"
                elif "START_PENDING" in output:
                    status = "starting"
                elif "STOP_PENDING" in output:
                    status = "stopping"
                else:
                    status = "unknown"
            else:
                status = "not_installed"
            
            # Update cache
            self._service_status_cache = status
            self._service_status_cache_time = time.time()
            return status
                
        except Exception as e:
            self.logger.error(f"Error getting service status: {e}")
            return "error"
    
    def configure_service_startup(self) -> bool:
        """Configure service to start automatically"""
        try:
            cmd = ["sc", "config", self.service_name, "start=", "auto"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Service configured for automatic startup")
                return True
            else:
                self.logger.error(f"Failed to configure service startup: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error configuring service startup: {e}")
            return False
    
    def ensure_pywin32_installed(self) -> bool:
        """Ensure pywin32 is installed"""
        try:
            import win32service
            import win32serviceutil
            return True
        except ImportError:
            self.logger.info("Installing pywin32...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "pywin32"], check=True)
                
                # Run post-install script
                subprocess.run([sys.executable, "-m", "pywin32_postinstall"], check=True)
                
                self.logger.info("pywin32 installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to install pywin32: {e}")
                return False
    
    def create_task_scheduler_task(self) -> bool:
        """Create Windows Task Scheduler task"""
        if not self.check_admin_privileges():
            self.logger.error("Administrator privileges required to create scheduled task")
            print("Please run as Administrator to create the scheduled task.")
            return False
        
        try:
            self.logger.info("Creating Windows Task Scheduler task...")
            
            # Create task XML
            task_xml = self.generate_task_xml()
            
            # Write task XML to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                f.write(task_xml)
                temp_xml_path = f.name
            
            try:
                # Create task using schtasks command
                cmd = [
                    "schtasks", "/Create",
                    "/TN", f"A6-9V\\{self.service_name}",
                    "/XML", temp_xml_path,
                    "/F"  # Force creation, overwrite if exists
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info("Task Scheduler task created successfully")
                    return True
                else:
                    self.logger.error(f"Failed to create scheduled task: {result.stderr}")
                    return False
                    
            finally:
                # Clean up temporary file
                os.unlink(temp_xml_path)
                
        except Exception as e:
            self.logger.error(f"Error creating scheduled task: {e}")
            return False
    
    def delete_task_scheduler_task(self) -> bool:
        """Delete Windows Task Scheduler task"""
        if not self.check_admin_privileges():
            self.logger.error("Administrator privileges required to delete scheduled task")
            print("Please run as Administrator to delete the scheduled task.")
            return False
        
        try:
            cmd = [
                "schtasks", "/Delete",
                "/TN", f"A6-9V\\{self.service_name}",
                "/F"  # Force deletion
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Task Scheduler task deleted successfully")
                return True
            else:
                self.logger.warning(f"Task deletion result: {result.stderr}")
                return True  # Task might not exist, which is okay
                
        except Exception as e:
            self.logger.error(f"Error deleting scheduled task: {e}")
            return False
    
    def generate_task_xml(self) -> str:
        """Generate Task Scheduler XML configuration"""
        return f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().isoformat()}</Date>
    <Author>A6-9V</Author>
    <Description>{self.service_description}</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>PT30S</Delay>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{sys.executable}</Command>
      <Arguments>"{self.startup_manager_path}"</Arguments>
      <WorkingDirectory>{self.script_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
    
    def get_task_status(self) -> str:
        """Get Task Scheduler task status"""
        try:
            cmd = ["schtasks", "/Query", "/TN", f"A6-9V\\{self.service_name}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout
                if "Running" in output:
                    return "running"
                elif "Ready" in output:
                    return "ready"
                elif "Disabled" in output:
                    return "disabled"
                else:
                    return "unknown"
            else:
                return "not_found"
                
        except Exception as e:
            self.logger.error(f"Error getting task status: {e}")
            return "error"
    
    def create_startup_batch_file(self) -> bool:
        """Create batch file for startup"""
        try:
            batch_content = f'''@echo off
cd /d "{self.script_dir}"
"{sys.executable}" "{self.startup_manager_path}"
pause
'''
            
            batch_path = self.script_dir / "start_python_manager.bat"
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            self.logger.info(f"Startup batch file created: {batch_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating batch file: {e}")
            return False
    
    def add_to_startup_folder(self) -> bool:
        """Add shortcut to Windows startup folder"""
        try:
            import win32com.client
            
            # Get startup folder path
            startup_folder = Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
            shortcut_path = startup_folder / f"{self.service_display_name}.lnk"
            
            # Create shortcut
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{self.startup_manager_path}"'
            shortcut.WorkingDirectory = str(self.script_dir)
            shortcut.IconLocation = sys.executable
            shortcut.Description = self.service_description
            shortcut.save()
            
            self.logger.info(f"Startup shortcut created: {shortcut_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding to startup folder: {e}")
            return False
    
    def remove_from_startup_folder(self) -> bool:
        """Remove shortcut from Windows startup folder"""
        try:
            startup_folder = Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
            shortcut_path = startup_folder / f"{self.service_display_name}.lnk"
            
            if shortcut_path.exists():
                shortcut_path.unlink()
                self.logger.info("Startup shortcut removed")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing from startup folder: {e}")
            return False
    
    def setup_auto_startup(self, method: str = "service") -> bool:
        """Setup automatic startup using specified method"""
        self.logger.info(f"Setting up auto startup using method: {method}")
        
        if method == "service":
            return self.install_service()
        elif method == "task_scheduler":
            return self.create_task_scheduler_task()
        elif method == "startup_folder":
            self.create_startup_batch_file()
            return self.add_to_startup_folder()
        else:
            self.logger.error(f"Unknown startup method: {method}")
            return False
    
    def remove_auto_startup(self, method: str = "all") -> bool:
        """Remove automatic startup"""
        success = True
        
        if method in ["all", "service"]:
            if not self.uninstall_service():
                success = False
        
        if method in ["all", "task_scheduler"]:
            if not self.delete_task_scheduler_task():
                success = False
        
        if method in ["all", "startup_folder"]:
            if not self.remove_from_startup_folder():
                success = False
        
        return success
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'service': {
                'status': self.get_service_status(),
                'installed': self.get_service_status() != "not_installed"
            },
            'task_scheduler': {
                'status': self.get_task_status(),
                'installed': self.get_task_status() != "not_found"
            },
            'startup_folder': {
                'installed': self.check_startup_folder_shortcut()
            },
            'admin_privileges': self.check_admin_privileges()
        }
        
        return report
    
    def check_startup_folder_shortcut(self) -> bool:
        """Check if startup folder shortcut exists"""
        try:
            startup_folder = Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
            shortcut_path = startup_folder / f"{self.service_display_name}.lnk"
            return shortcut_path.exists()
        except:
            return False


def main():
    """Main entry point for Windows service management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Windows Service Manager for A6-9V Python Applications")
    parser.add_argument('action', choices=[
        'install-service', 'uninstall-service', 'start-service', 'stop-service',
        'install-task', 'uninstall-task', 'install-startup', 'uninstall-startup',
        'status', 'install-all', 'uninstall-all'
    ], help="Action to perform")
    parser.add_argument('--config', default="python_startup_config.yaml", help="Configuration file path")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    manager = WindowsServiceManager(args.config)
    
    if args.action == 'install-service':
        success = manager.install_service()
        if success:
            print("✓ Windows service installed successfully")
            print("  Use 'start-service' to start the service")
        else:
            print("✗ Failed to install Windows service")
            sys.exit(1)
    
    elif args.action == 'uninstall-service':
        success = manager.uninstall_service()
        if success:
            print("✓ Windows service uninstalled successfully")
        else:
            print("✗ Failed to uninstall Windows service")
            sys.exit(1)
    
    elif args.action == 'start-service':
        success = manager.start_service()
        if success:
            print("✓ Windows service started successfully")
        else:
            print("✗ Failed to start Windows service")
            sys.exit(1)
    
    elif args.action == 'stop-service':
        success = manager.stop_service()
        if success:
            print("✓ Windows service stopped successfully")
        else:
            print("✗ Failed to stop Windows service")
            sys.exit(1)
    
    elif args.action == 'install-task':
        success = manager.create_task_scheduler_task()
        if success:
            print("✓ Task Scheduler task created successfully")
        else:
            print("✗ Failed to create Task Scheduler task")
            sys.exit(1)
    
    elif args.action == 'uninstall-task':
        success = manager.delete_task_scheduler_task()
        if success:
            print("✓ Task Scheduler task deleted successfully")
        else:
            print("✗ Failed to delete Task Scheduler task")
            sys.exit(1)
    
    elif args.action == 'install-startup':
        manager.create_startup_batch_file()
        success = manager.add_to_startup_folder()
        if success:
            print("✓ Startup folder shortcut created successfully")
        else:
            print("✗ Failed to create startup folder shortcut")
            sys.exit(1)
    
    elif args.action == 'uninstall-startup':
        success = manager.remove_from_startup_folder()
        if success:
            print("✓ Startup folder shortcut removed successfully")
        else:
            print("✗ Failed to remove startup folder shortcut")
            sys.exit(1)
    
    elif args.action == 'status':
        report = manager.get_status_report()
        print("\\n=== A6-9V Python Manager Status ===")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Admin Privileges: {'Yes' if report['admin_privileges'] else 'No'}")
        print("\\nWindows Service:")
        print(f"  Status: {report['service']['status']}")
        print(f"  Installed: {'Yes' if report['service']['installed'] else 'No'}")
        print("\\nTask Scheduler:")
        print(f"  Status: {report['task_scheduler']['status']}")
        print(f"  Installed: {'Yes' if report['task_scheduler']['installed'] else 'No'}")
        print("\\nStartup Folder:")
        print(f"  Shortcut exists: {'Yes' if report['startup_folder']['installed'] else 'No'}")
    
    elif args.action == 'install-all':
        print("Installing all startup methods...")
        success = True
        
        # Install service
        if manager.install_service():
            print("✓ Windows service installed")
        else:
            print("✗ Windows service installation failed")
            success = False
        
        # Install task scheduler task
        if manager.create_task_scheduler_task():
            print("✓ Task Scheduler task created")
        else:
            print("✗ Task Scheduler task creation failed")
            success = False
        
        # Install startup folder shortcut
        manager.create_startup_batch_file()
        if manager.add_to_startup_folder():
            print("✓ Startup folder shortcut created")
        else:
            print("✗ Startup folder shortcut creation failed")
            success = False
        
        if success:
            print("\\n✓ All startup methods installed successfully")
        else:
            print("\\n⚠ Some startup methods failed to install")
            sys.exit(1)
    
    elif args.action == 'uninstall-all':
        print("Uninstalling all startup methods...")
        success = manager.remove_auto_startup("all")
        
        if success:
            print("✓ All startup methods uninstalled successfully")
        else:
            print("⚠ Some startup methods failed to uninstall")
            sys.exit(1)


if __name__ == "__main__":
    main()