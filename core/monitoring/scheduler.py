#!/usr/bin/env python3
"""
AMP Scheduler Module
Handles automated job scheduling and execution
"""

import asyncio
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging
from typing import Optional, Dict, Any

from .auth import check_auth, get_user_info
from amp_job_runner import AMPJobRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/amp_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AMPScheduler:
    def __init__(self):
        self.scheduler_config = Path("amp_scheduler_config.json")
        self.job_runner = AMPJobRunner()
        self.is_running = False
        
        # Default schedule
        self.default_schedule = {
            "market_open": "09:00",
            "market_close": "17:00",
            "interval_minutes": 30,
            "timezone": "UTC",
            "enabled": True
        }
        
        self.load_config()
    
    def load_config(self):
        """Load scheduler configuration"""
        if self.scheduler_config.exists():
            try:
                with open(self.scheduler_config, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"Error loading scheduler config: {e}")
                self.config = self.default_schedule
        else:
            self.config = self.default_schedule
            self.save_config()
    
    def save_config(self):
        """Save scheduler configuration"""
        try:
            with open(self.scheduler_config, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving scheduler config: {e}")
    
    async def run_scheduled_job(self):
        """Execute a scheduled job"""
        try:
            # Check authentication
            if not check_auth():
                logger.warning("User not authenticated. Skipping scheduled job.")
                return
            
            user_info = get_user_info()
            logger.info(f"Running scheduled job for user: {user_info['user_id']}")
            
            # Run the job
            await self.job_runner.run_next_job()
            
            logger.info("Scheduled job completed successfully")
            
        except Exception as e:
            logger.error(f"Error in scheduled job: {e}")
    
    def setup_schedule(self):
        """Set up the job schedule"""
        # Clear existing schedule
        schedule.clear()
        
        if not self.config.get("enabled", True):
            logger.info("Scheduler is disabled")
            return
        
        interval = self.config.get("interval_minutes", 30)
        
        # Schedule jobs every X minutes during market hours
        schedule.every(interval).minutes.do(
            lambda: asyncio.run(self.run_scheduled_job())
        )
        
        logger.info(f"Scheduler set up: jobs every {interval} minutes")
    
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        logger.info("Starting AMP Scheduler...")
        self.is_running = True
        
        # Set up the schedule
        self.setup_schedule()
        
        # Run the scheduler
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)
    
    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping AMP Scheduler...")
        self.is_running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "is_running": self.is_running,
            "config": self.config,
            "next_jobs": [str(job) for job in schedule.jobs],
            "last_run": self.get_last_run_time()
        }
    
    def get_last_run_time(self) -> Optional[str]:
        """Get the last job run time"""
        log_file = Path("logs/amp_scheduler.log")
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in reversed(lines):
                        if "Running scheduled job" in line:
                            return line.split(" - ")[0]
            except Exception:
                pass
        return None
    
    def update_config(self, **kwargs):
        """Update scheduler configuration"""
        self.config.update(kwargs)
        self.save_config()
        logger.info("Scheduler configuration updated")
        
        # Restart scheduler if running
        if self.is_running:
            self.stop()
            self.start()

# Global scheduler instance
amp_scheduler = AMPScheduler()

def start_scheduler():
    """Start the AMP scheduler"""
    amp_scheduler.start()

def stop_scheduler():
    """Stop the AMP scheduler"""
    amp_scheduler.stop()

def get_scheduler_status() -> Dict[str, Any]:
    """Get scheduler status"""
    return amp_scheduler.get_status()

def update_scheduler_config(**kwargs):
    """Update scheduler configuration"""
    amp_scheduler.update_config(**kwargs)