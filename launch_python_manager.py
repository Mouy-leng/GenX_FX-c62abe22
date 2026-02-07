"""
Master Python Manager Launcher
Unified launcher for all Python management components
Provides easy startup, installation, and management for A6-9V Python applications
"""

import sys
import os
import subprocess
import logging
import argparse
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class PythonManagerLauncher:
    """
    Master launcher for Python management system
    Coordinates startup manager, dashboard, and Windows service integration
    """
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Component paths
        self.startup_manager_path = self.script_dir / "python_startup_manager.py"
        self.dashboard_path = self.script_dir / "process_monitor_dashboard.py"
        self.service_manager_path = self.script_dir / "windows_service_manager.py"
        self.env_setup_path = self.script_dir / "setup_python_environment.py"
        self.config_path = self.script_dir / "python_startup_config.yaml"
        
    def setup_logging(self):
        """Setup logging system"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"launcher_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if all required dependencies are available"""
        self.logger.info("Checking dependencies...")
        
        dependencies = {}
        
        # Check Python packages
        packages = ['psutil', 'yaml', 'matplotlib', 'requests', 'tkinter']
        for package in packages:
            try:
                __import__(package)
                dependencies[package] = True
                self.logger.info(f"+ {package} available")
            except ImportError:
                dependencies[package] = False
                self.logger.warning(f"- {package} not available")
        
        # Check component files
        components = [
            ('startup_manager', self.startup_manager_path),
            ('dashboard', self.dashboard_path),
            ('service_manager', self.service_manager_path),
            ('env_setup', self.env_setup_path),
            ('config', self.config_path)
        ]
        
        for name, path in components:
            if path.exists():
                dependencies[name] = True
                self.logger.info(f"+ {name} component available")
            else:
                dependencies[name] = False
                self.logger.warning(f"- {name} component missing")
        
        return dependencies
    
    def install_dependencies(self) -> bool:
        """Install missing dependencies"""
        self.logger.info("Installing missing dependencies...")
        
        dependencies = self.check_dependencies()
        missing_packages = [pkg for pkg, available in dependencies.items() 
                           if not available and pkg in ['psutil', 'yaml', 'matplotlib', 'requests']]
        
        if not missing_packages:
            self.logger.info("All dependencies are available")
            return True
        
        try:
            # Batch install all missing packages in a single pip command for better performance
            self.logger.info(f"Installing packages: {', '.join(missing_packages)}")
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
            self.logger.info(f"+ All packages installed successfully")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def create_startup_script(self) -> bool:
        """Create master startup script"""
        startup_script = self.script_dir / "start_all.bat"
        
        script_content = f'''@echo off
title A6-9V Python Manager Launcher
echo Starting A6-9V Python Management System...
echo.

cd /d "{self.script_dir}"

echo [%time%] Checking dependencies...
"{sys.executable}" "{__file__}" --check-deps
if errorlevel 1 (
    echo Error: Dependencies check failed
    pause
    exit /b 1
)

echo [%time%] Starting Python Startup Manager...
start "Python Manager" "{sys.executable}" "{self.startup_manager_path}"

timeout /t 5 /nobreak >nul

echo [%time%] Starting Dashboard...
start "Dashboard" "{sys.executable}" "{self.dashboard_path}"

echo.
echo [SUCCESS] A6-9V Python Management System started successfully
echo.
echo Components running:
echo - Python Startup Manager (manages your Python applications)
echo - Process Monitor Dashboard (monitoring and control interface)
echo.
echo Check the dashboard window for real-time monitoring and control.
echo.
pause
'''
        
        try:
            with open(startup_script, 'w') as f:
                f.write(script_content)
            
            self.logger.info(f"Startup script created: {startup_script}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create startup script: {e}")
            return False
    
    def start_startup_manager(self) -> bool:
        """Start the Python startup manager"""
        try:
            self.logger.info("Starting Python Startup Manager...")
            
            if not self.startup_manager_path.exists():
                self.logger.error("Startup manager script not found")
                return False
            
            # Start in separate process
            subprocess.Popen([
                sys.executable, str(self.startup_manager_path)
            ], cwd=self.script_dir)
            
            self.logger.info("Python Startup Manager started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start startup manager: {e}")
            return False
    
    def start_dashboard(self) -> bool:
        """Start the monitoring dashboard"""
        try:
            self.logger.info("Starting Process Monitor Dashboard...")
            
            if not self.dashboard_path.exists():
                self.logger.error("Dashboard script not found")
                return False
            
            # Start in separate process
            subprocess.Popen([
                sys.executable, str(self.dashboard_path)
            ], cwd=self.script_dir)
            
            self.logger.info("Process Monitor Dashboard started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start dashboard: {e}")
            return False
    
    def start_all(self) -> bool:
        """Start all components"""
        self.logger.info("=" * 60)
        self.logger.info("Starting A6-9V Python Management System")
        self.logger.info("=" * 60)
        
        success = True
        
        # Check dependencies first
        if not self.check_all_ready():
            self.logger.error("System not ready - run setup first")
            return False
        
        # Start startup manager
        if not self.start_startup_manager():
            success = False
        
        # Wait a moment for startup manager to initialize
        time.sleep(3)
        
        # Start dashboard
        if not self.start_dashboard():
            success = False
        
        if success:
            self.logger.info("=" * 60)
            self.logger.info("✓ A6-9V Python Management System started successfully")
            self.logger.info("✓ Python applications are now being managed")
            self.logger.info("✓ Dashboard is available for monitoring and control")
            self.logger.info("=" * 60)
            
            print("\\n🚀 A6-9V Python Management System is now running!")
            print("📊 Check the dashboard window for real-time monitoring")
            print("🔧 Use the dashboard to start, stop, and monitor your Python applications")
            print("📋 Log files are available in the 'logs' directory")
        else:
            self.logger.error("Some components failed to start")
        
        return success
    
    def setup_system(self) -> bool:
        """Setup the entire system"""
        self.logger.info("Setting up A6-9V Python Management System...")
        
        print("🔧 Setting up A6-9V Python Management System...")
        print("=" * 60)
        
        steps = [
            ("Checking dependencies", self.install_dependencies),
            ("Creating startup script", self.create_startup_script),
            ("Setting up directories", self.setup_directories),
            ("Validating configuration", self.validate_config)
        ]
        
        success = True
        for step_name, step_func in steps:
            print(f"📋 {step_name}...")
            try:
                if not step_func():
                    print(f"❌ {step_name} failed")
                    success = False
                else:
                    print(f"✅ {step_name} completed")
            except Exception as e:
                print(f"❌ {step_name} failed: {e}")
                success = False
        
        if success:
            print("=" * 60)
            print("🎉 Setup completed successfully!")
            print("📋 Next steps:")
            print("  1. Run 'python launch_python_manager.py --start' to start the system")
            print("  2. Or run 'start_all.bat' for easy Windows startup")
            print("  3. Use 'python windows_service_manager.py install-all' for auto-startup")
        else:
            print("=" * 60)
            print("❌ Setup failed. Check the logs for details.")
        
        return success
    
    def setup_directories(self) -> bool:
        """Setup required directories"""
        try:
            directories = ['logs', 'backups', 'data']
            
            for directory in directories:
                dir_path = self.script_dir / directory
                dir_path.mkdir(exist_ok=True)
                self.logger.info(f"Directory created/verified: {directory}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup directories: {e}")
            return False
    
    def validate_config(self) -> bool:
        """Validate configuration file"""
        try:
            if not self.config_path.exists():
                self.logger.warning("Configuration file not found - will be created on first run")
                return True
            
            # Try to load and validate YAML
            import yaml
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Basic validation
            if 'projects' not in config:
                self.logger.warning("No projects section in config")
            
            self.logger.info("Configuration file validated")
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def check_all_ready(self) -> bool:
        """Check if system is ready to start"""
        dependencies = self.check_dependencies()
        
        # Check critical components
        critical = ['psutil', 'yaml', 'startup_manager', 'dashboard']
        missing_critical = [dep for dep in critical if not dependencies.get(dep, False)]
        
        if missing_critical:
            self.logger.error(f"Critical components missing: {missing_critical}")
            print(f"❌ Critical components missing: {', '.join(missing_critical)}")
            print("🔧 Run 'python launch_python_manager.py --setup' to fix this")
            return False
        
        return True
    
    def install_windows_service(self) -> bool:
        """Install Windows service for auto-startup"""
        try:
            if not self.service_manager_path.exists():
                self.logger.error("Windows service manager not found")
                return False
            
            # Run service installation
            result = subprocess.run([
                sys.executable, str(self.service_manager_path), "install-all"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Windows service installed successfully")
                print("✅ Windows service installed - system will start automatically on boot")
                return True
            else:
                self.logger.error(f"Service installation failed: {result.stderr}")
                print(f"❌ Service installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to install Windows service: {e}")
            return False
    
    def uninstall_windows_service(self) -> bool:
        """Uninstall Windows service"""
        try:
            if not self.service_manager_path.exists():
                self.logger.error("Windows service manager not found")
                return False
            
            # Run service uninstallation
            result = subprocess.run([
                sys.executable, str(self.service_manager_path), "uninstall-all"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Windows service uninstalled successfully")
                print("✅ Windows service uninstalled")
                return True
            else:
                self.logger.error(f"Service uninstallation failed: {result.stderr}")
                print(f"❌ Service uninstallation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to uninstall Windows service: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        dependencies = self.check_dependencies()
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'system_ready': self.check_all_ready(),
            'dependencies': dependencies,
            'components': {
                'startup_manager': self.startup_manager_path.exists(),
                'dashboard': self.dashboard_path.exists(),
                'service_manager': self.service_manager_path.exists(),
                'config': self.config_path.exists()
            }
        }
        
        # Check Windows service status if available
        if self.service_manager_path.exists():
            try:
                result = subprocess.run([
                    sys.executable, str(self.service_manager_path), "status"
                ], capture_output=True, text=True)
                status['service_status'] = result.stdout if result.returncode == 0 else "error"
            except:
                status['service_status'] = "unavailable"
        
        return status
    
    def print_status(self):
        """Print system status"""
        status = self.get_system_status()
        
        print("\\n📊 A6-9V Python Management System Status")
        print("=" * 60)
        print(f"⏰ Timestamp: {status['timestamp']}")
        print(f"🚦 System Ready: {'✅ Yes' if status['system_ready'] else '❌ No'}")
        
        print("\\n📦 Dependencies:")
        for dep, available in status['dependencies'].items():
            if dep in ['psutil', 'yaml', 'matplotlib', 'requests']:
                status_icon = "✅" if available else "❌"
                print(f"  {status_icon} {dep}")
        
        print("\\n🔧 Components:")
        for comp, available in status['components'].items():
            status_icon = "✅" if available else "❌"
            print(f"  {status_icon} {comp}")
        
        if 'service_status' in status and status['service_status'] != "unavailable":
            print("\\n🖥️  Windows Service Status:")
            if status['service_status'] != "error":
                print(f"  {status['service_status']}")
            else:
                print("  ❌ Error checking service status")
        
        print("=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="A6-9V Python Management System Launcher",
        epilog="""
Examples:
  python launch_python_manager.py --setup         # Setup the system
  python launch_python_manager.py --start         # Start all components
  python launch_python_manager.py --status        # Show system status
  python launch_python_manager.py --install       # Install Windows service
        """
    )
    
    parser.add_argument('--setup', action='store_true', 
                       help='Setup the Python management system')
    parser.add_argument('--start', action='store_true', 
                       help='Start all management components')
    parser.add_argument('--status', action='store_true', 
                       help='Show system status')
    parser.add_argument('--check-deps', action='store_true', 
                       help='Check dependencies')
    parser.add_argument('--install', action='store_true', 
                       help='Install Windows service for auto-startup')
    parser.add_argument('--uninstall', action='store_true', 
                       help='Uninstall Windows service')
    
    args = parser.parse_args()
    
    launcher = PythonManagerLauncher()
    
    # Show banner
    print("🐍 A6-9V Python Management System Launcher")
    print("=" * 60)
    
    if args.setup:
        success = launcher.setup_system()
        sys.exit(0 if success else 1)
    
    elif args.start:
        success = launcher.start_all()
        if success:
            print("\\n💡 Tip: The dashboard window provides full control over your Python applications")
            print("🔄 Applications will auto-restart if they crash (configurable)")
            input("\\nPress Enter to exit launcher (components will continue running)...")
        sys.exit(0 if success else 1)
    
    elif args.status:
        launcher.print_status()
    
    elif args.check_deps:
        dependencies = launcher.check_dependencies()
        missing = [dep for dep, available in dependencies.items() if not available]
        if missing:
            print(f"❌ Missing dependencies: {', '.join(missing)}")
            sys.exit(1)
        else:
            print("✅ All dependencies available")
            sys.exit(0)
    
    elif args.install:
        success = launcher.install_windows_service()
        sys.exit(0 if success else 1)
    
    elif args.uninstall:
        success = launcher.uninstall_windows_service()
        sys.exit(0 if success else 1)
    
    else:
        # Interactive mode
        print("🔧 Interactive Setup and Launch")
        print("\\nWhat would you like to do?")
        print("1. 🔧 Setup system (first time)")
        print("2. 🚀 Start management system")
        print("3. 📊 Show system status")
        print("4. 🖥️  Install Windows service (auto-startup)")
        print("5. ❌ Exit")
        
        while True:
            try:
                choice = input("\\nEnter your choice (1-5): ").strip()
                
                if choice == '1':
                    launcher.setup_system()
                    break
                elif choice == '2':
                    launcher.start_all()
                    input("\\nPress Enter to exit...")
                    break
                elif choice == '3':
                    launcher.print_status()
                    input("\\nPress Enter to continue...")
                elif choice == '4':
                    launcher.install_windows_service()
                    input("\\nPress Enter to continue...")
                elif choice == '5':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-5.")
                    
            except KeyboardInterrupt:
                print("\\n👋 Goodbye!")
                break


if __name__ == "__main__":
    main()