"""
Python Startup Manager
Comprehensive system for managing Python application startup, monitoring, and lifecycle management
Designed for A6-9V organization projects with focus on autonomous trading systems
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import threading
import signal
import shutil


class ProcessState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    CRASHED = "crashed"


@dataclass
class PythonProject:
    name: str
    path: str
    main_file: str
    requirements_file: Optional[str] = None
    venv_path: Optional[str] = None
    python_version: str = "3.11"
    dependencies: List[str] = None
    environment_vars: Dict[str, str] = None
    startup_delay: int = 0
    auto_restart: bool = True
    max_restarts: int = 5
    health_check_url: Optional[str] = None
    priority: int = 1  # Lower number = higher priority
    enabled: bool = True


@dataclass
class ProcessInfo:
    project: PythonProject
    process: Optional[subprocess.Popen] = None
    pid: Optional[int] = None
    state: ProcessState = ProcessState.STOPPED
    start_time: Optional[datetime] = None
    restart_count: int = 0
    last_restart: Optional[datetime] = None
    logs: List[str] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0


class PythonStartupManager:
    """
    Comprehensive Python Startup Manager
    Handles multiple Python projects with virtual environments, dependencies, and monitoring
    """
    
    def __init__(self, config_path: str = "python_startup_config.yaml"):
        self.config_path = config_path
        self.projects: Dict[str, PythonProject] = {}
        self.processes: Dict[str, ProcessInfo] = {}
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitor_event = threading.Event()  # Non-blocking event for responsive monitoring
        
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.load_configuration()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def setup_logging(self):
        """Setup comprehensive logging system"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"python_startup_manager_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def load_configuration(self):
        """Load project configurations from YAML file"""
        if not Path(self.config_path).exists():
            self.logger.info(f"Configuration file {self.config_path} not found. Creating default configuration.")
            self.create_default_configuration()
            return
        
        try:
            with open(self.config_path, 'r') as file:
                config_data = yaml.safe_load(file)
            
            for project_config in config_data.get('projects', []):
                project = PythonProject(**project_config)
                self.projects[project.name] = project
                self.processes[project.name] = ProcessInfo(project=project, logs=[])
            
            self.logger.info(f"Loaded {len(self.projects)} projects from configuration")
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self.create_default_configuration()
    
    def create_default_configuration(self):
        """Create default configuration with detected projects"""
        # Auto-detect GenX-FX project
        genx_fx_path = Path("A6-9V/Trading/GenX_FX")
        if genx_fx_path.exists():
            genx_fx_project = PythonProject(
                name="GenX_FX_Trading",
                path=str(genx_fx_path.absolute()),
                main_file="main.py",
                requirements_file="requirements.txt",
                venv_path=str(genx_fx_path / "venv"),
                python_version="3.11",
                dependencies=[],
                environment_vars={
                    "PYTHONPATH": str(genx_fx_path.absolute()),
                    "GENX_ENV": "production"
                },
                startup_delay=5,
                auto_restart=True,
                max_restarts=3,
                priority=1,
                enabled=True
            )
            self.projects["GenX_FX_Trading"] = genx_fx_project
            self.processes["GenX_FX_Trading"] = ProcessInfo(project=genx_fx_project, logs=[])
        
        # Save default configuration
        self.save_configuration()
    
    def save_configuration(self):
        """Save current configuration to file"""
        try:
            config_data = {
                'projects': [asdict(project) for project in self.projects.values()]
            }
            
            with open(self.config_path, 'w') as file:
                yaml.dump(config_data, file, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def add_project(self, project: PythonProject):
        """Add a new project to the manager"""
        self.projects[project.name] = project
        self.processes[project.name] = ProcessInfo(project=project, logs=[])
        self.save_configuration()
        self.logger.info(f"Added project: {project.name}")
    
    def remove_project(self, project_name: str):
        """Remove a project from the manager"""
        if project_name in self.projects:
            # Stop the process if running
            if self.processes[project_name].state == ProcessState.RUNNING:
                self.stop_project(project_name)
            
            del self.projects[project_name]
            del self.processes[project_name]
            self.save_configuration()
            self.logger.info(f"Removed project: {project_name}")
    
    def setup_virtual_environment(self, project_name: str) -> bool:
        """Setup virtual environment for a project"""
        if project_name not in self.projects:
            self.logger.error(f"Project {project_name} not found")
            return False
        
        project = self.projects[project_name]
        venv_path = Path(project.venv_path) if project.venv_path else Path(project.path) / "venv"
        
        try:
            self.logger.info(f"Setting up virtual environment for {project_name} at {venv_path}")
            
            # Create virtual environment
            if not venv_path.exists():
                subprocess.run([
                    sys.executable, "-m", "venv", str(venv_path)
                ], check=True)
                self.logger.info(f"Created virtual environment: {venv_path}")
            
            # Get Python executable path
            if os.name == 'nt':  # Windows
                python_exe = venv_path / "Scripts" / "python.exe"
                pip_exe = venv_path / "Scripts" / "pip.exe"
            else:  # Unix/Linux
                python_exe = venv_path / "bin" / "python"
                pip_exe = venv_path / "bin" / "pip"
            
            # Upgrade pip
            subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
            
            # Install requirements if available
            requirements_path = Path(project.path) / (project.requirements_file or "requirements.txt")
            if requirements_path.exists():
                self.logger.info(f"Installing requirements from {requirements_path}")
                subprocess.run([
                    str(pip_exe), "install", "-r", str(requirements_path)
                ], check=True)
            
            # Install additional dependencies
            if project.dependencies:
                self.logger.info(f"Installing additional dependencies: {project.dependencies}")
                subprocess.run([
                    str(pip_exe), "install"
                ] + project.dependencies, check=True)
            
            # Update project configuration with venv path
            project.venv_path = str(venv_path)
            self.save_configuration()
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error setting up virtual environment for {project_name}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error setting up virtual environment for {project_name}: {e}")
            return False
    
    def start_project(self, project_name: str) -> bool:
        """Start a specific project"""
        if project_name not in self.projects:
            self.logger.error(f"Project {project_name} not found")
            return False
        
        project = self.projects[project_name]
        process_info = self.processes[project_name]
        
        if not project.enabled:
            self.logger.info(f"Project {project_name} is disabled")
            return False
        
        if process_info.state == ProcessState.RUNNING:
            self.logger.info(f"Project {project_name} is already running")
            return True
        
        try:
            self.logger.info(f"Starting project: {project_name}")
            process_info.state = ProcessState.STARTING
            
            # Setup virtual environment if needed
            if project.venv_path and not Path(project.venv_path).exists():
                if not self.setup_virtual_environment(project_name):
                    process_info.state = ProcessState.ERROR
                    return False
            
            # Prepare environment variables
            env = os.environ.copy()
            if project.environment_vars:
                env.update(project.environment_vars)
            
            # Determine Python executable
            if project.venv_path:
                venv_path = Path(project.venv_path)
                if os.name == 'nt':  # Windows
                    python_exe = str(venv_path / "Scripts" / "python.exe")
                else:  # Unix/Linux
                    python_exe = str(venv_path / "bin" / "python")
            else:
                python_exe = sys.executable
            
            # Prepare command
            main_file_path = Path(project.path) / project.main_file
            cmd = [python_exe, str(main_file_path)]
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                cwd=project.path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Update process info
            process_info.process = process
            process_info.pid = process.pid
            process_info.state = ProcessState.RUNNING
            process_info.start_time = datetime.now()
            
            # Add startup delay
            if project.startup_delay > 0:
                self.logger.info(f"Applying startup delay of {project.startup_delay} seconds for {project_name}")
                time.sleep(project.startup_delay)
            
            self.logger.info(f"Started project {project_name} with PID {process.pid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting project {project_name}: {e}")
            process_info.state = ProcessState.ERROR
            return False
    
    def stop_project(self, project_name: str) -> bool:
        """Stop a specific project"""
        if project_name not in self.processes:
            self.logger.error(f"Project {project_name} not found")
            return False
        
        process_info = self.processes[project_name]
        
        if process_info.state != ProcessState.RUNNING:
            self.logger.info(f"Project {project_name} is not running")
            return True
        
        try:
            self.logger.info(f"Stopping project: {project_name}")
            process_info.state = ProcessState.STOPPING
            
            if process_info.process:
                # Graceful shutdown
                process_info.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process_info.process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"Force killing project {project_name}")
                    process_info.process.kill()
                    process_info.process.wait()
                
                process_info.process = None
                process_info.pid = None
            
            process_info.state = ProcessState.STOPPED
            self.logger.info(f"Stopped project: {project_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping project {project_name}: {e}")
            return False
    
    def restart_project(self, project_name: str) -> bool:
        """Restart a specific project"""
        self.logger.info(f"Restarting project: {project_name}")
        
        if not self.stop_project(project_name):
            return False
        
        # Wait a moment before restart
        time.sleep(2)
        
        process_info = self.processes[project_name]
        process_info.restart_count += 1
        process_info.last_restart = datetime.now()
        
        return self.start_project(project_name)
    
    def start_all_projects(self):
        """Start all enabled projects in priority order"""
        self.logger.info("Starting all projects...")
        
        # Sort projects by priority
        sorted_projects = sorted(
            [(name, project) for name, project in self.projects.items() if project.enabled],
            key=lambda x: x[1].priority
        )
        
        for project_name, project in sorted_projects:
            self.start_project(project_name)
            
            # Apply inter-project startup delay
            if project.startup_delay > 0:
                time.sleep(1)
    
    def stop_all_projects(self):
        """Stop all running projects"""
        self.logger.info("Stopping all projects...")
        
        for project_name in self.projects.keys():
            self.stop_project(project_name)
    
    def get_project_status(self, project_name: str) -> Dict[str, Any]:
        """Get detailed status of a project"""
        if project_name not in self.processes:
            return {"error": "Project not found"}
        
        process_info = self.processes[project_name]
        project = self.projects[project_name]
        
        status = {
            "name": project_name,
            "state": process_info.state.value,
            "pid": process_info.pid,
            "start_time": process_info.start_time.isoformat() if process_info.start_time else None,
            "restart_count": process_info.restart_count,
            "last_restart": process_info.last_restart.isoformat() if process_info.last_restart else None,
            "cpu_usage": process_info.cpu_usage,
            "memory_usage": process_info.memory_usage,
            "enabled": project.enabled,
            "auto_restart": project.auto_restart,
            "max_restarts": project.max_restarts,
            "priority": project.priority
        }
        
        # Add uptime if running
        if process_info.start_time and process_info.state == ProcessState.RUNNING:
            uptime = datetime.now() - process_info.start_time
            status["uptime"] = str(uptime)
        
        return status
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all projects"""
        return {
            "manager": {
                "running": self.running,
                "total_projects": len(self.projects),
                "running_projects": len([p for p in self.processes.values() if p.state == ProcessState.RUNNING]),
                "timestamp": datetime.now().isoformat()
            },
            "projects": {name: self.get_project_status(name) for name in self.projects.keys()}
        }
    
    def monitor_processes(self):
        """Monitor running processes and handle restarts"""
        while self.running:
            try:
                for project_name, process_info in self.processes.items():
                    if process_info.state == ProcessState.RUNNING:
                        # Check if process is still alive
                        if process_info.process and process_info.process.poll() is not None:
                            # Process has terminated
                            self.logger.warning(f"Process {project_name} (PID: {process_info.pid}) has terminated")
                            process_info.state = ProcessState.CRASHED
                            
                            # Auto-restart if enabled and within limits
                            project = self.projects[project_name]
                            if (project.auto_restart and 
                                process_info.restart_count < project.max_restarts):
                                self.logger.info(f"Auto-restarting {project_name} (attempt {process_info.restart_count + 1})")
                                self.restart_project(project_name)
                        
                        # Update resource usage
                        if process_info.pid:
                            try:
                                proc = psutil.Process(process_info.pid)
                                process_info.cpu_usage = proc.cpu_percent()
                                process_info.memory_usage = proc.memory_percent()
                            except psutil.NoSuchProcess:
                                pass
                
                # Use event-based waiting instead of blocking sleep for responsive shutdown
                self.monitor_event.wait(timeout=10)  # Check every 10 seconds, but responsive to stop signals
                
            except Exception as e:
                self.logger.error(f"Error in process monitoring: {e}")
                self.monitor_event.wait(timeout=5)  # Non-blocking wait on error
    
    def start_manager(self):
        """Start the Python startup manager"""
        self.logger.info("Starting Python Startup Manager...")
        self.running = True
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        self.monitor_thread.start()
        
        # Start all projects
        self.start_all_projects()
        
        self.logger.info("Python Startup Manager started successfully")
    
    def stop_manager(self):
        """Stop the Python startup manager"""
        self.logger.info("Stopping Python Startup Manager...")
        self.running = False
        
        # Signal the monitor thread to wake up immediately for responsive shutdown
        self.monitor_event.set()
        
        # Stop all projects
        self.stop_all_projects()
        
        # Wait for monitor thread to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Python Startup Manager stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop_manager()
        sys.exit(0)


def main():
    """Main entry point"""
    # Create and start the manager
    manager = PythonStartupManager()
    
    try:
        manager.start_manager()
        
        # Keep the manager running
        while manager.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        manager.logger.info("Received keyboard interrupt")
        manager.stop_manager()
    except Exception as e:
        manager.logger.error(f"Unexpected error: {e}")
        manager.stop_manager()


if __name__ == "__main__":
    main()