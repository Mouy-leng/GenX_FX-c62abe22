"""
Process Monitor Dashboard
Advanced monitoring and management system for Python applications
Provides real-time monitoring, logging, alerting, and control interface
Designed for A6-9V organization projects
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import subprocess
import logging
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from collections import deque
import queue


class MetricsCollector:
    """Collect and store system and process metrics"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history = {
            'timestamp': deque(maxlen=max_history),
            'cpu_usage': deque(maxlen=max_history),
            'memory_usage': deque(maxlen=max_history),
            'processes': {}
        }
        self.lock = threading.Lock()
    
    def add_metric(self, timestamp: datetime, cpu_usage: float, memory_usage: float, 
                   process_metrics: Dict[str, Dict[str, float]]):
        """Add metrics to history"""
        with self.lock:
            self.metrics_history['timestamp'].append(timestamp)
            self.metrics_history['cpu_usage'].append(cpu_usage)
            self.metrics_history['memory_usage'].append(memory_usage)
            
            for process_name, metrics in process_metrics.items():
                if process_name not in self.metrics_history['processes']:
                    self.metrics_history['processes'][process_name] = {
                        'cpu': deque(maxlen=self.max_history),
                        'memory': deque(maxlen=self.max_history),
                        'status': deque(maxlen=self.max_history)
                    }
                
                self.metrics_history['processes'][process_name]['cpu'].append(metrics.get('cpu', 0))
                self.metrics_history['processes'][process_name]['memory'].append(metrics.get('memory', 0))
                self.metrics_history['processes'][process_name]['status'].append(metrics.get('status', 'unknown'))
    
    def get_recent_metrics(self, minutes: int = 60) -> Dict[str, Any]:
        """Get metrics from the last N minutes with optimized timestamp filtering"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            recent_data = {
                'timestamp': [],
                'cpu_usage': [],
                'memory_usage': [],
                'processes': {}
            }
            
            timestamps = list(self.metrics_history['timestamp'])
            
            # Handle empty timestamps
            if not timestamps:
                return recent_data
            
            # Find the first index where timestamp >= cutoff_time
            # Using linear search since deque doesn't support binary search efficiently
            # Future optimization: Use bisect on a sorted list if performance becomes critical
            start_idx = None
            for i, ts in enumerate(timestamps):
                if ts >= cutoff_time:
                    start_idx = i
                    break
            
            # No data within the time range
            if start_idx is None:
                return recent_data
            
            # Extract data from start_idx onwards (much faster than filtering entire history)
            recent_data['timestamp'] = timestamps[start_idx:]
            recent_data['cpu_usage'] = list(self.metrics_history['cpu_usage'])[start_idx:]
            recent_data['memory_usage'] = list(self.metrics_history['memory_usage'])[start_idx:]
            
            for process_name, process_data in self.metrics_history['processes'].items():
                recent_data['processes'][process_name] = {
                    'cpu': list(process_data['cpu'])[start_idx:],
                    'memory': list(process_data['memory'])[start_idx:],
                    'status': list(process_data['status'])[start_idx:]
                }
            
            return recent_data


class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_history = deque(maxlen=1000)
        self.active_alerts = {}
        self.lock = threading.Lock()
        
        # Setup logging for alerts
        self.logger = logging.getLogger('AlertManager')
        
    def check_alerts(self, metrics: Dict[str, Any]):
        """Check for alert conditions"""
        current_time = datetime.now()
        new_alerts = []
        
        # System resource alerts
        if metrics.get('cpu_usage', 0) > self.config.get('alert_threshold_cpu', 90):
            alert_id = 'system_cpu_high'
            if alert_id not in self.active_alerts:
                alert = {
                    'id': alert_id,
                    'type': 'system',
                    'severity': 'high',
                    'message': f"High CPU usage: {metrics['cpu_usage']:.1f}%",
                    'timestamp': current_time,
                    'value': metrics['cpu_usage']
                }
                new_alerts.append(alert)
                self.active_alerts[alert_id] = alert
        
        if metrics.get('memory_usage', 0) > self.config.get('alert_threshold_memory', 90):
            alert_id = 'system_memory_high'
            if alert_id not in self.active_alerts:
                alert = {
                    'id': alert_id,
                    'type': 'system',
                    'severity': 'high',
                    'message': f"High memory usage: {metrics['memory_usage']:.1f}%",
                    'timestamp': current_time,
                    'value': metrics['memory_usage']
                }
                new_alerts.append(alert)
                self.active_alerts[alert_id] = alert
        
        # Process-specific alerts
        for process_name, process_data in metrics.get('processes', {}).items():
            status = process_data.get('status', 'unknown')
            if status in ['crashed', 'error']:
                alert_id = f'process_{process_name}_failed'
                if alert_id not in self.active_alerts:
                    alert = {
                        'id': alert_id,
                        'type': 'process',
                        'severity': 'critical',
                        'message': f"Process {process_name} has {status}",
                        'timestamp': current_time,
                        'process': process_name,
                        'status': status
                    }
                    new_alerts.append(alert)
                    self.active_alerts[alert_id] = alert
        
        # Add new alerts to history
        with self.lock:
            for alert in new_alerts:
                self.alert_history.append(alert)
                self.logger.warning(f"Alert triggered: {alert['message']}")
        
        return new_alerts
    
    def clear_alert(self, alert_id: str):
        """Clear an active alert"""
        with self.lock:
            if alert_id in self.active_alerts:
                del self.active_alerts[alert_id]
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of active alerts"""
        with self.lock:
            return list(self.active_alerts.values())


class ProcessMonitorDashboard:
    """Main dashboard for process monitoring and management"""
    
    def __init__(self, startup_manager):
        self.startup_manager = startup_manager
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager(startup_manager.projects)
        
        # Threading and update controls
        self.monitoring_active = False
        self.update_queue = queue.Queue()
        
        # Performance optimization: Track if chart data has changed to avoid unnecessary redraws
        self.last_chart_update_time = None
        self.chart_update_interval = 2.0  # Only update charts every 2 seconds
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("A6-9V Python Process Monitor Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # Setup UI
        self.setup_ui()
        
        # Start monitoring thread
        self.start_monitoring()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        # Title
        title_label = ttk.Label(main_frame, text="A6-9V Python Process Monitor", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_overview_tab()
        self.create_processes_tab()
        self.create_metrics_tab()
        self.create_logs_tab()
        self.create_alerts_tab()
        self.create_control_tab()
    
    def create_overview_tab(self):
        """Create overview tab with system summary"""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="Overview")
        
        # System info frame
        sys_frame = ttk.LabelFrame(overview_frame, text="System Information", padding="10")
        sys_frame.pack(fill=tk.X, pady=(0, 10))
        
        # System metrics
        metrics_frame = ttk.Frame(sys_frame)
        metrics_frame.pack(fill=tk.X)
        
        # CPU Usage
        ttk.Label(metrics_frame, text="CPU Usage:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.cpu_label = ttk.Label(metrics_frame, text="0.0%")
        self.cpu_label.grid(row=0, column=1, sticky=tk.W)
        
        self.cpu_progress = ttk.Progressbar(metrics_frame, length=200, mode='determinate')
        self.cpu_progress.grid(row=0, column=2, padx=(10, 0))
        
        # Memory Usage
        ttk.Label(metrics_frame, text="Memory Usage:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.memory_label = ttk.Label(metrics_frame, text="0.0%")
        self.memory_label.grid(row=1, column=1, sticky=tk.W)
        
        self.memory_progress = ttk.Progressbar(metrics_frame, length=200, mode='determinate')
        self.memory_progress.grid(row=1, column=2, padx=(10, 0))
        
        # Process summary
        process_frame = ttk.LabelFrame(overview_frame, text="Process Summary", padding="10")
        process_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Process list
        columns = ('Name', 'Status', 'PID', 'CPU%', 'Memory%', 'Uptime')
        self.process_tree = ttk.Treeview(process_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=120)
        
        process_scrollbar = ttk.Scrollbar(process_frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=process_scrollbar.set)
        
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        process_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_processes_tab(self):
        """Create processes management tab"""
        processes_frame = ttk.Frame(self.notebook)
        self.notebook.add(processes_frame, text="Processes")
        
        # Control buttons frame
        control_frame = ttk.Frame(processes_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="Start All", command=self.start_all_processes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Stop All", command=self.stop_all_processes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Restart All", command=self.restart_all_processes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Refresh", command=self.refresh_processes).pack(side=tk.LEFT, padx=(0, 5))
        
        # Process details
        details_frame = ttk.LabelFrame(processes_frame, text="Process Details", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Detailed process list with controls
        columns = ('Name', 'Status', 'PID', 'Path', 'Actions')
        self.detailed_process_tree = ttk.Treeview(details_frame, columns=columns, show='headings')
        
        for col in columns:
            self.detailed_process_tree.heading(col, text=col)
            if col == 'Path':
                self.detailed_process_tree.column(col, width=300)
            else:
                self.detailed_process_tree.column(col, width=120)
        
        detailed_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.detailed_process_tree.yview)
        self.detailed_process_tree.configure(yscrollcommand=detailed_scrollbar.set)
        
        self.detailed_process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detailed_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.detailed_process_tree.bind('<Double-1>', self.on_process_double_click)
    
    def create_metrics_tab(self):
        """Create metrics visualization tab"""
        metrics_frame = ttk.Frame(self.notebook)
        self.notebook.add(metrics_frame, text="Metrics")
        
        # Create matplotlib figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        self.fig.patch.set_facecolor('#2b2b2b')
        
        # Setup plots
        self.ax1.set_title('CPU Usage Over Time', color='white')
        self.ax1.set_ylabel('CPU %', color='white')
        self.ax1.tick_params(colors='white')
        self.ax1.set_facecolor('#3b3b3b')
        
        self.ax2.set_title('Memory Usage Over Time', color='white')
        self.ax2.set_ylabel('Memory %', color='white')
        self.ax2.set_xlabel('Time', color='white')
        self.ax2.tick_params(colors='white')
        self.ax2.set_facecolor('#3b3b3b')
        
        # Embed plot in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, metrics_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_logs_tab(self):
        """Create logs viewing tab"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        
        # Log controls
        log_controls = ttk.Frame(logs_frame)
        log_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(log_controls, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))
        self.log_filter = ttk.Combobox(log_controls, values=['All', 'Info', 'Warning', 'Error', 'Critical'])
        self.log_filter.set('All')
        self.log_filter.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(log_controls, text="Clear Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_controls, text="Export Logs", command=self.export_logs).pack(side=tk.LEFT, padx=(0, 5))
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(logs_frame, wrap=tk.WORD, height=25, bg='#1e1e1e', fg='white')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different log levels
        self.log_text.tag_config('INFO', foreground='lightgreen')
        self.log_text.tag_config('WARNING', foreground='yellow')
        self.log_text.tag_config('ERROR', foreground='red')
        self.log_text.tag_config('CRITICAL', foreground='red', background='darkred')
    
    def create_alerts_tab(self):
        """Create alerts management tab"""
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text="Alerts")
        
        # Alert controls
        alert_controls = ttk.Frame(alerts_frame)
        alert_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(alert_controls, text="Clear All Alerts", command=self.clear_all_alerts).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(alert_controls, text="Refresh Alerts", command=self.refresh_alerts).pack(side=tk.LEFT, padx=(0, 5))
        
        # Active alerts
        active_frame = ttk.LabelFrame(alerts_frame, text="Active Alerts", padding="10")
        active_frame.pack(fill=tk.X, pady=(0, 10))
        
        alert_columns = ('Severity', 'Type', 'Message', 'Time')
        self.alert_tree = ttk.Treeview(active_frame, columns=alert_columns, show='headings', height=6)
        
        for col in alert_columns:
            self.alert_tree.heading(col, text=col)
            if col == 'Message':
                self.alert_tree.column(col, width=400)
            else:
                self.alert_tree.column(col, width=120)
        
        alert_scrollbar = ttk.Scrollbar(active_frame, orient=tk.VERTICAL, command=self.alert_tree.yview)
        self.alert_tree.configure(yscrollcommand=alert_scrollbar.set)
        
        self.alert_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        alert_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Alert history
        history_frame = ttk.LabelFrame(alerts_frame, text="Alert History", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        self.alert_history_text = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, height=15, bg='#1e1e1e', fg='white')
        self.alert_history_text.pack(fill=tk.BOTH, expand=True)
    
    def create_control_tab(self):
        """Create control and configuration tab"""
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="Control")
        
        # Configuration section
        config_frame = ttk.LabelFrame(control_frame, text="Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Monitoring controls
        ttk.Label(config_frame, text="Monitor Interval (seconds):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.monitor_interval = tk.StringVar(value="10")
        ttk.Entry(config_frame, textvariable=self.monitor_interval, width=10).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(config_frame, text="Alert CPU Threshold (%):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.cpu_threshold = tk.StringVar(value="80")
        ttk.Entry(config_frame, textvariable=self.cpu_threshold, width=10).grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(config_frame, text="Alert Memory Threshold (%):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.memory_threshold = tk.StringVar(value="80")
        ttk.Entry(config_frame, textvariable=self.memory_threshold, width=10).grid(row=2, column=1, sticky=tk.W)
        
        # Action buttons
        action_frame = ttk.LabelFrame(control_frame, text="Actions", padding="10")
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(action_frame, text="Save Configuration", command=self.save_configuration).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Load Configuration", command=self.load_configuration).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Export Report", command=self.export_report).pack(side=tk.LEFT, padx=(0, 5))
        
        # Status section
        status_frame = ttk.LabelFrame(control_frame, text="System Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, wrap=tk.WORD, height=15, bg='#1e1e1e', fg='white')
        self.status_text.pack(fill=tk.BOTH, expand=True)
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Start UI update timer
        self.schedule_ui_update()
    
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # Collect process metrics
                process_metrics = {}
                for project_name, process_info in self.startup_manager.processes.items():
                    if process_info.pid:
                        try:
                            proc = psutil.Process(process_info.pid)
                            process_metrics[project_name] = {
                                'cpu': proc.cpu_percent(),
                                'memory': proc.memory_percent(),
                                'status': process_info.state.value
                            }
                        except psutil.NoSuchProcess:
                            process_metrics[project_name] = {
                                'cpu': 0,
                                'memory': 0,
                                'status': 'not_found'
                            }
                
                # Store metrics
                self.metrics_collector.add_metric(
                    datetime.now(),
                    cpu_percent,
                    memory.percent,
                    process_metrics
                )
                
                # Check alerts
                metrics = {
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory.percent,
                    'processes': process_metrics
                }
                
                new_alerts = self.alert_manager.check_alerts(metrics)
                
                # Queue update for UI thread
                self.update_queue.put({
                    'type': 'metrics_update',
                    'data': metrics,
                    'alerts': new_alerts
                })
                
                time.sleep(int(self.monitor_interval.get()) if hasattr(self, 'monitor_interval') else 10)
                
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def schedule_ui_update(self):
        """Schedule UI update"""
        self.update_ui()
        self.root.after(1000, self.schedule_ui_update)  # Update UI every second
    
    def update_ui(self):
        """Update UI with latest data"""
        try:
            # Process all queued updates
            while not self.update_queue.empty():
                try:
                    update = self.update_queue.get_nowait()
                    
                    if update['type'] == 'metrics_update':
                        self.update_metrics_display(update['data'])
                        self.update_process_display()
                        self.update_charts()
                        
                        # Handle new alerts
                        for alert in update['alerts']:
                            self.add_alert_to_display(alert)
                
                except queue.Empty:
                    break
                    
        except Exception as e:
            logging.error(f"Error updating UI: {e}")
    
    def update_metrics_display(self, metrics: Dict[str, Any]):
        """Update system metrics display"""
        cpu_usage = metrics.get('cpu_usage', 0)
        memory_usage = metrics.get('memory_usage', 0)
        
        # Update labels and progress bars
        self.cpu_label.config(text=f"{cpu_usage:.1f}%")
        self.cpu_progress['value'] = cpu_usage
        
        self.memory_label.config(text=f"{memory_usage:.1f}%")
        self.memory_progress['value'] = memory_usage
        
        # Color coding for high usage
        if cpu_usage > 80:
            self.cpu_progress.config(style='Danger.Horizontal.TProgressbar')
        elif cpu_usage > 60:
            self.cpu_progress.config(style='Warning.Horizontal.TProgressbar')
        else:
            self.cpu_progress.config(style='TProgressbar')
        
        if memory_usage > 80:
            self.memory_progress.config(style='Danger.Horizontal.TProgressbar')
        elif memory_usage > 60:
            self.memory_progress.config(style='Warning.Horizontal.TProgressbar')
        else:
            self.memory_progress.config(style='TProgressbar')
    
    def update_process_display(self):
        """Update process display"""
        # Efficiently clear all items in one operation instead of looping
        self.process_tree.delete(*self.process_tree.get_children())
        self.detailed_process_tree.delete(*self.detailed_process_tree.get_children())
        
        # Add current processes
        for project_name, process_info in self.startup_manager.processes.items():
            status = process_info.state.value
            pid = process_info.pid or "N/A"
            
            # Calculate uptime
            uptime = "N/A"
            if process_info.start_time:
                delta = datetime.now() - process_info.start_time
                uptime = str(delta).split('.')[0]  # Remove microseconds
            
            # Get resource usage
            cpu_usage = process_info.cpu_usage
            memory_usage = process_info.memory_usage
            
            # Add to overview tree
            self.process_tree.insert('', 'end', values=(
                project_name, status, pid, f"{cpu_usage:.1f}%", f"{memory_usage:.1f}%", uptime
            ))
            
            # Add to detailed tree
            project_path = process_info.project.path
            actions = "Start/Stop/Restart"
            self.detailed_process_tree.insert('', 'end', values=(
                project_name, status, pid, project_path, actions
            ))
    
    def update_charts(self):
        """Update metrics charts with performance optimization"""
        try:
            # Throttle chart updates to avoid expensive matplotlib redraws
            current_time = time.time()
            if self.last_chart_update_time and (current_time - self.last_chart_update_time < self.chart_update_interval):
                return  # Skip update if less than 2 seconds since last update
            
            self.last_chart_update_time = current_time
            
            recent_metrics = self.metrics_collector.get_recent_metrics(60)  # Last 60 minutes
            
            if not recent_metrics['timestamp']:
                return
            
            # Clear previous plots
            self.ax1.clear()
            self.ax2.clear()
            
            # Plot system metrics
            timestamps = recent_metrics['timestamp']
            cpu_data = recent_metrics['cpu_usage']
            memory_data = recent_metrics['memory_usage']
            
            self.ax1.plot(timestamps, cpu_data, 'g-', label='System CPU', linewidth=2)
            self.ax1.set_title('CPU Usage Over Time', color='white')
            self.ax1.set_ylabel('CPU %', color='white')
            self.ax1.tick_params(colors='white')
            self.ax1.set_facecolor('#3b3b3b')
            self.ax1.grid(True, alpha=0.3)
            self.ax1.set_ylim(0, 100)
            
            self.ax2.plot(timestamps, memory_data, 'b-', label='System Memory', linewidth=2)
            
            # Plot process metrics
            colors = ['red', 'orange', 'purple', 'cyan', 'yellow']
            color_idx = 0
            
            for process_name, process_data in recent_metrics['processes'].items():
                if len(process_data['cpu']) == len(timestamps):
                    self.ax1.plot(timestamps, process_data['cpu'], 
                                color=colors[color_idx % len(colors)], 
                                label=f'{process_name} CPU', 
                                linestyle='--', alpha=0.7)
                    self.ax2.plot(timestamps, process_data['memory'], 
                                color=colors[color_idx % len(colors)], 
                                label=f'{process_name} Memory', 
                                linestyle='--', alpha=0.7)
                    color_idx += 1
            
            self.ax2.set_title('Memory Usage Over Time', color='white')
            self.ax2.set_ylabel('Memory %', color='white')
            self.ax2.set_xlabel('Time', color='white')
            self.ax2.tick_params(colors='white')
            self.ax2.set_facecolor('#3b3b3b')
            self.ax2.grid(True, alpha=0.3)
            self.ax2.set_ylim(0, 100)
            
            # Format x-axis
            self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            
            # Add legends
            self.ax1.legend(loc='upper right', facecolor='#3b3b3b', edgecolor='white')
            self.ax2.legend(loc='upper right', facecolor='#3b3b3b', edgecolor='white')
            
            # Redraw canvas (expensive operation, now throttled)
            self.canvas.draw()
            
        except Exception as e:
            logging.error(f"Error updating charts: {e}")
    
    def add_alert_to_display(self, alert: Dict[str, Any]):
        """Add alert to display"""
        # Add to alert tree
        self.alert_tree.insert('', 0, values=(
            alert['severity'].upper(),
            alert['type'].upper(),
            alert['message'],
            alert['timestamp'].strftime('%H:%M:%S')
        ))
        
        # Add to alert history
        alert_text = f"[{alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] {alert['severity'].upper()}: {alert['message']}\\n"
        self.alert_history_text.insert(tk.END, alert_text)
        self.alert_history_text.see(tk.END)
        
        # Add to logs
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ALERT - {alert['message']}\\n"
        self.log_text.insert(tk.END, log_entry, 'ERROR')
        self.log_text.see(tk.END)
    
    # Control methods
    def start_all_processes(self):
        """Start all processes"""
        self.startup_manager.start_all_projects()
        self.add_status_message("Starting all processes...")
    
    def stop_all_processes(self):
        """Stop all processes"""
        self.startup_manager.stop_all_projects()
        self.add_status_message("Stopping all processes...")
    
    def restart_all_processes(self):
        """Restart all processes"""
        self.stop_all_processes()
        time.sleep(2)
        self.start_all_processes()
        self.add_status_message("Restarting all processes...")
    
    def refresh_processes(self):
        """Refresh process display"""
        self.add_status_message("Refreshing process display...")
    
    def on_process_double_click(self, event):
        """Handle double-click on process"""
        selection = self.detailed_process_tree.selection()
        if selection:
            item = self.detailed_process_tree.item(selection[0])
            process_name = item['values'][0]
            
            # Show process control dialog
            self.show_process_control_dialog(process_name)
    
    def show_process_control_dialog(self, process_name: str):
        """Show process control dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Control - {process_name}")
        dialog.geometry("300x200")
        dialog.configure(bg='#2b2b2b')
        
        # Process info
        info_frame = ttk.LabelFrame(dialog, text="Process Information", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        process_info = self.startup_manager.processes.get(process_name)
        if process_info:
            ttk.Label(info_frame, text=f"Status: {process_info.state.value}").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"PID: {process_info.pid or 'N/A'}").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"CPU: {process_info.cpu_usage:.1f}%").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Memory: {process_info.memory_usage:.1f}%").pack(anchor=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Start", 
                  command=lambda: self.startup_manager.start_project(process_name)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Stop", 
                  command=lambda: self.startup_manager.stop_project(process_name)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Restart", 
                  command=lambda: self.startup_manager.restart_project(process_name)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def clear_logs(self):
        """Clear log display"""
        self.log_text.delete(1.0, tk.END)
    
    def export_logs(self):
        """Export logs to file"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'w') as f:
                f.write(self.log_text.get(1.0, tk.END))
            messagebox.showinfo("Export", f"Logs exported to {filename}")
    
    def clear_all_alerts(self):
        """Clear all alerts"""
        # Clear active alerts
        for item in self.alert_tree.get_children():
            self.alert_tree.delete(item)
        
        # Clear alert history display
        self.alert_history_text.delete(1.0, tk.END)
        
        # Clear from alert manager
        self.alert_manager.active_alerts.clear()
    
    def refresh_alerts(self):
        """Refresh alerts display"""
        active_alerts = self.alert_manager.get_active_alerts()
        
        # Clear and repopulate
        for item in self.alert_tree.get_children():
            self.alert_tree.delete(item)
        
        for alert in active_alerts:
            self.alert_tree.insert('', 0, values=(
                alert['severity'].upper(),
                alert['type'].upper(),
                alert['message'],
                alert['timestamp'].strftime('%H:%M:%S')
            ))
    
    def save_configuration(self):
        """Save current configuration"""
        self.startup_manager.save_configuration()
        self.add_status_message("Configuration saved successfully")
    
    def load_configuration(self):
        """Load configuration"""
        self.startup_manager.load_configuration()
        self.add_status_message("Configuration loaded successfully")
    
    def export_report(self):
        """Export monitoring report"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'system_status': self.startup_manager.get_all_status(),
                'metrics': self.metrics_collector.get_recent_metrics(1440),  # 24 hours
                'active_alerts': self.alert_manager.get_active_alerts()
            }
            
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            messagebox.showinfo("Export", f"Report exported to {filename}")
    
    def add_status_message(self, message: str):
        """Add message to status display"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status_entry = f"[{timestamp}] {message}\\n"
        self.status_text.insert(tk.END, status_entry)
        self.status_text.see(tk.END)
        
        # Also add to logs
        self.log_text.insert(tk.END, status_entry, 'INFO')
        self.log_text.see(tk.END)
    
    def run(self):
        """Run the dashboard"""
        try:
            self.root.mainloop()
        finally:
            self.monitoring_active = False


def main():
    """Main entry point"""
    # Import the startup manager
    from python_startup_manager import PythonStartupManager
    
    # Create startup manager instance
    startup_manager = PythonStartupManager()
    
    # Create and run dashboard
    dashboard = ProcessMonitorDashboard(startup_manager)
    dashboard.run()


if __name__ == "__main__":
    main()