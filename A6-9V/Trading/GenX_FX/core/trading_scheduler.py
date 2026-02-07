"""
Trading Scheduler - 24/7 Trading Schedule Management
Handles forex sessions, crypto continuous trading, and scheduled analysis
Device: NUNA 💻 | User: @mouyleng 🧑‍💻 | Org: @A6-9V 🏙️
"""

import asyncio
import logging
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import pytz
from zoneinfo import ZoneInfo
import json


class TradingSession(Enum):
    """Trading sessions"""
    SYDNEY = "sydney"
    TOKYO = "tokyo"
    LONDON = "london"
    NEW_YORK = "new_york"
    OVERLAP_LONDON_NY = "overlap_london_ny"
    CRYPTO_CONTINUOUS = "crypto_continuous"


class MarketType(Enum):
    """Market types"""
    FOREX = "forex"
    CRYPTO = "crypto"
    COMMODITIES = "commodities"
    INDICES = "indices"


@dataclass
class SessionConfig:
    """Configuration for a trading session"""
    name: str
    open_time: time
    close_time: time
    timezone: str
    preferred_pairs: List[str]
    strategies: List[str]
    is_high_volatility: bool = False
    active_days: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])  # Mon-Fri


@dataclass
class ScheduledTask:
    """Configuration for a scheduled task"""
    name: str
    schedule: str  # cron-like or interval
    callback: Callable
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class TradingScheduler:
    """
    Advanced 24/7 Trading Scheduler
    
    Features:
    - Forex session management (Sydney, Tokyo, London, New York)
    - Crypto/Gold 24/7 continuous trading
    - News event scheduling
    - Automated task scheduling
    - Gemini AI integration scheduling
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Session configurations
        self.sessions: Dict[TradingSession, SessionConfig] = {}
        self._initialize_sessions()
        
        # Scheduled tasks
        self.scheduled_tasks: List[ScheduledTask] = []
        
        # Trading state
        self.is_running = False
        self.current_session: Optional[TradingSession] = None
        self.active_pairs: List[str] = []
        
        # Callback handlers
        self.on_session_change: Optional[Callable] = None
        self.on_market_open: Optional[Callable] = None
        self.on_market_close: Optional[Callable] = None
        self.on_high_impact_event: Optional[Callable] = None
        
        # Timezone for Singapore VPS
        self.vps_timezone = pytz.timezone('Asia/Singapore')
        
    def _initialize_sessions(self):
        """Initialize trading sessions"""
        # Sydney Session (Asian open)
        self.sessions[TradingSession.SYDNEY] = SessionConfig(
            name="Sydney",
            open_time=time(22, 0),  # 22:00 UTC
            close_time=time(7, 0),   # 07:00 UTC
            timezone="Australia/Sydney",
            preferred_pairs=["AUDUSD", "NZDUSD", "AUDJPY", "NZDJPY"],
            strategies=["mean_reversion", "range_trading"],
            is_high_volatility=False,
            active_days=[0, 1, 2, 3, 4]  # Sun night to Fri
        )
        
        # Tokyo Session
        self.sessions[TradingSession.TOKYO] = SessionConfig(
            name="Tokyo",
            open_time=time(0, 0),   # 00:00 UTC
            close_time=time(9, 0),  # 09:00 UTC
            timezone="Asia/Tokyo",
            preferred_pairs=["USDJPY", "EURJPY", "GBPJPY", "AUDJPY"],
            strategies=["mean_reversion", "range_trading", "breakout"],
            is_high_volatility=False,
            active_days=[0, 1, 2, 3, 4]
        )
        
        # London Session (Most volatile)
        self.sessions[TradingSession.LONDON] = SessionConfig(
            name="London",
            open_time=time(8, 0),   # 08:00 UTC
            close_time=time(17, 0), # 17:00 UTC
            timezone="Europe/London",
            preferred_pairs=["EURUSD", "GBPUSD", "EURGBP", "EURJPY", "GBPJPY"],
            strategies=["momentum", "breakout", "trend_following"],
            is_high_volatility=True,
            active_days=[0, 1, 2, 3, 4]
        )
        
        # New York Session
        self.sessions[TradingSession.NEW_YORK] = SessionConfig(
            name="New York",
            open_time=time(13, 0),  # 13:00 UTC
            close_time=time(22, 0), # 22:00 UTC
            timezone="America/New_York",
            preferred_pairs=["EURUSD", "GBPUSD", "USDJPY", "USDCAD", "USDCHF"],
            strategies=["momentum", "trend_following", "news_trading"],
            is_high_volatility=True,
            active_days=[0, 1, 2, 3, 4]
        )
        
        # London-NY Overlap (Highest volatility)
        self.sessions[TradingSession.OVERLAP_LONDON_NY] = SessionConfig(
            name="London-NY Overlap",
            open_time=time(13, 0),  # 13:00 UTC
            close_time=time(17, 0), # 17:00 UTC
            timezone="UTC",
            preferred_pairs=["EURUSD", "GBPUSD", "USDJPY"],
            strategies=["breakout", "momentum", "scalping"],
            is_high_volatility=True,
            active_days=[0, 1, 2, 3, 4]
        )
        
        # Crypto Continuous (24/7)
        self.sessions[TradingSession.CRYPTO_CONTINUOUS] = SessionConfig(
            name="Crypto 24/7",
            open_time=time(0, 0),
            close_time=time(23, 59),
            timezone="UTC",
            preferred_pairs=["BTCUSD", "XAUUSD", "BTCXAU"],
            strategies=["momentum", "mean_reversion", "ml_prediction"],
            is_high_volatility=True,
            active_days=[0, 1, 2, 3, 4, 5, 6]  # All days
        )
    
    async def start(self):
        """Start the trading scheduler"""
        self.is_running = True
        self.logger.info("Starting trading scheduler...")
        
        # Start main scheduler loop
        asyncio.create_task(self._scheduler_loop())
        
        # Start session monitoring
        asyncio.create_task(self._session_monitor_loop())
        
        # Start task executor
        asyncio.create_task(self._task_executor_loop())
        
        self.logger.info("Trading scheduler started")
    
    async def stop(self):
        """Stop the trading scheduler"""
        self.is_running = False
        self.logger.info("Trading scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                # Get current time in UTC
                now_utc = datetime.now(pytz.UTC)
                
                # Check for session changes
                await self._check_session_changes(now_utc)
                
                # Update active pairs based on current sessions
                await self._update_active_pairs(now_utc)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)
    
    async def _session_monitor_loop(self):
        """Monitor trading sessions"""
        while self.is_running:
            try:
                now_utc = datetime.now(pytz.UTC)
                active_sessions = self.get_active_sessions(now_utc)
                
                self.logger.debug(f"Active sessions: {[s.value for s in active_sessions]}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in session monitor: {e}")
                await asyncio.sleep(300)
    
    async def _task_executor_loop(self):
        """Execute scheduled tasks"""
        while self.is_running:
            try:
                now = datetime.now(pytz.UTC)
                
                for task in self.scheduled_tasks:
                    if task.enabled and task.next_run and now >= task.next_run:
                        try:
                            await task.callback()
                            task.last_run = now
                            task.next_run = self._calculate_next_run(task)
                            self.logger.info(f"Executed task: {task.name}")
                        except Exception as e:
                            self.logger.error(f"Error executing task {task.name}: {e}")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in task executor: {e}")
                await asyncio.sleep(1)
    
    def get_active_sessions(self, dt: datetime = None) -> List[TradingSession]:
        """Get currently active trading sessions"""
        if dt is None:
            dt = datetime.now(pytz.UTC)
        
        active = []
        current_time = dt.time()
        current_day = dt.weekday()
        
        for session_type, session in self.sessions.items():
            # Check if trading day
            if current_day not in session.active_days:
                continue
            
            # Check session hours
            if self._is_session_active(session, current_time):
                active.append(session_type)
        
        return active
    
    def _is_session_active(self, session: SessionConfig, current_time: time) -> bool:
        """Check if a session is currently active"""
        open_time = session.open_time
        close_time = session.close_time
        
        # Handle overnight sessions (e.g., Sydney)
        if open_time > close_time:
            return current_time >= open_time or current_time <= close_time
        else:
            return open_time <= current_time <= close_time
    
    async def _check_session_changes(self, now_utc: datetime):
        """Check for session changes and trigger callbacks"""
        active_sessions = self.get_active_sessions(now_utc)
        
        if active_sessions and self.current_session not in active_sessions:
            # Session changed
            new_session = active_sessions[0]  # Primary session
            
            if self.current_session is not None:
                # Trigger session close callback
                if self.on_market_close:
                    await self.on_market_close(self.current_session)
            
            self.current_session = new_session
            
            # Trigger session open callback
            if self.on_market_open:
                await self.on_market_open(new_session)
            
            # Trigger session change callback
            if self.on_session_change:
                await self.on_session_change(new_session, active_sessions)
            
            self.logger.info(f"Session changed to: {new_session.value}")
    
    async def _update_active_pairs(self, now_utc: datetime):
        """Update list of active trading pairs"""
        active_sessions = self.get_active_sessions(now_utc)
        
        # Always include crypto pairs (24/7)
        new_active_pairs = set(["BTCUSD", "XAUUSD", "BTCXAU"])
        
        # Add pairs from active sessions
        for session_type in active_sessions:
            session = self.sessions[session_type]
            new_active_pairs.update(session.preferred_pairs)
        
        self.active_pairs = list(new_active_pairs)
    
    def get_session_info(self, session_type: TradingSession) -> Dict[str, Any]:
        """Get information about a trading session"""
        session = self.sessions.get(session_type)
        if not session:
            return {}
        
        now_utc = datetime.now(pytz.UTC)
        is_active = session_type in self.get_active_sessions(now_utc)
        
        return {
            'name': session.name,
            'is_active': is_active,
            'open_time': session.open_time.isoformat(),
            'close_time': session.close_time.isoformat(),
            'timezone': session.timezone,
            'preferred_pairs': session.preferred_pairs,
            'strategies': session.strategies,
            'is_high_volatility': session.is_high_volatility
        }
    
    def get_all_sessions_status(self) -> Dict[str, Any]:
        """Get status of all trading sessions"""
        now_utc = datetime.now(pytz.UTC)
        active_sessions = self.get_active_sessions(now_utc)
        
        status = {
            'timestamp': now_utc.isoformat(),
            'active_sessions': [s.value for s in active_sessions],
            'active_pairs': self.active_pairs,
            'sessions': {}
        }
        
        for session_type in TradingSession:
            status['sessions'][session_type.value] = self.get_session_info(session_type)
        
        return status
    
    def get_best_pairs_now(self) -> List[str]:
        """Get the best trading pairs for current time with optimized set-based lookups"""
        now_utc = datetime.now(pytz.UTC)
        active_sessions = self.get_active_sessions(now_utc)
        
        # Use set for O(1) membership checks instead of O(n) list checks
        best_pairs_set = set()
        
        # Priority: High volatility sessions first
        for session_type in active_sessions:
            session = self.sessions[session_type]
            if session.is_high_volatility:
                best_pairs_set.update(session.preferred_pairs)
        
        # Add regular session pairs
        for session_type in active_sessions:
            session = self.sessions[session_type]
            best_pairs_set.update(session.preferred_pairs)
        
        # Always include crypto pairs
        best_pairs_set.update(["BTCUSD", "XAUUSD", "BTCXAU"])
        
        return list(best_pairs_set)
    
    def get_strategies_for_session(self, session_type: TradingSession) -> List[str]:
        """Get recommended strategies for a session"""
        session = self.sessions.get(session_type)
        if session:
            return session.strategies
        return []
    
    def add_scheduled_task(self, name: str, schedule: str, 
                          callback: Callable, enabled: bool = True):
        """Add a scheduled task"""
        task = ScheduledTask(
            name=name,
            schedule=schedule,
            callback=callback,
            enabled=enabled,
            next_run=self._calculate_next_run_from_schedule(schedule)
        )
        self.scheduled_tasks.append(task)
        self.logger.info(f"Added scheduled task: {name}")
    
    def _calculate_next_run(self, task: ScheduledTask) -> datetime:
        """Calculate next run time for a task"""
        return self._calculate_next_run_from_schedule(task.schedule)
    
    def _calculate_next_run_from_schedule(self, schedule: str) -> datetime:
        """Calculate next run time from schedule string"""
        now = datetime.now(pytz.UTC)
        
        # Simple interval parsing (e.g., "1h", "30m", "1d")
        if schedule.endswith('h'):
            hours = int(schedule[:-1])
            return now + timedelta(hours=hours)
        elif schedule.endswith('m'):
            minutes = int(schedule[:-1])
            return now + timedelta(minutes=minutes)
        elif schedule.endswith('d'):
            days = int(schedule[:-1])
            return now + timedelta(days=days)
        
        # Default to 1 hour
        return now + timedelta(hours=1)
    
    def is_forex_market_open(self) -> bool:
        """Check if forex market is open"""
        now_utc = datetime.now(pytz.UTC)
        weekday = now_utc.weekday()
        
        # Forex closed from Friday 22:00 UTC to Sunday 22:00 UTC
        if weekday == 5:  # Saturday
            return False
        elif weekday == 6:  # Sunday
            return now_utc.hour >= 22  # Opens at 22:00 UTC
        elif weekday == 4:  # Friday
            return now_utc.hour < 22  # Closes at 22:00 UTC
        
        return True
    
    def is_crypto_market_open(self) -> bool:
        """Crypto market is always open"""
        return True
    
    def get_time_until_next_session(self, session_type: TradingSession) -> timedelta:
        """Get time until next session open"""
        session = self.sessions.get(session_type)
        if not session:
            return timedelta(0)
        
        now_utc = datetime.now(pytz.UTC)
        
        # Calculate next session open
        today_open = datetime.combine(now_utc.date(), session.open_time)
        today_open = pytz.UTC.localize(today_open)
        
        if now_utc < today_open:
            return today_open - now_utc
        else:
            # Next day
            tomorrow_open = today_open + timedelta(days=1)
            return tomorrow_open - now_utc
    
    def get_session_overlap_info(self) -> Dict[str, Any]:
        """Get information about session overlaps"""
        overlaps = {
            'sydney_tokyo': {
                'start': '00:00 UTC',
                'end': '07:00 UTC',
                'pairs': ['AUDJPY', 'NZDJPY', 'AUDUSD']
            },
            'tokyo_london': {
                'start': '08:00 UTC',
                'end': '09:00 UTC',
                'pairs': ['EURJPY', 'GBPJPY']
            },
            'london_new_york': {
                'start': '13:00 UTC',
                'end': '17:00 UTC',
                'pairs': ['EURUSD', 'GBPUSD', 'USDJPY'],
                'note': 'Highest volatility period'
            }
        }
        return overlaps


class TradingCalendar:
    """
    Trading calendar for scheduling around market events
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.high_impact_events: List[Dict[str, Any]] = []
    
    def add_event(self, event_time: datetime, event_name: str,
                  currency: str, impact: str, expected: str = None):
        """Add a high-impact event"""
        self.high_impact_events.append({
            'time': event_time,
            'name': event_name,
            'currency': currency,
            'impact': impact,
            'expected': expected
        })
    
    def get_upcoming_events(self, hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """Get upcoming high-impact events"""
        now_utc = datetime.now(pytz.UTC)
        cutoff = now_utc + timedelta(hours=hours_ahead)
        
        return [
            event for event in self.high_impact_events
            if now_utc <= event['time'] <= cutoff
        ]
    
    def should_pause_trading(self, pair: str, 
                             minutes_before: int = 15,
                             minutes_after: int = 5) -> bool:
        """Check if trading should be paused for upcoming events"""
        now_utc = datetime.now(pytz.UTC)
        
        for event in self.high_impact_events:
            event_time = event['time']
            pause_start = event_time - timedelta(minutes=minutes_before)
            pause_end = event_time + timedelta(minutes=minutes_after)
            
            if pause_start <= now_utc <= pause_end:
                # Check if event affects this pair
                currency = event['currency']
                if currency in pair:
                    return True
        
        return False


# Global scheduler instance
trading_scheduler = TradingScheduler()
trading_calendar = TradingCalendar()


async def initialize_scheduler():
    """Initialize and start the trading scheduler"""
    await trading_scheduler.start()
    
    # Add default scheduled tasks
    async def hourly_analysis():
        """Hourly market analysis"""
        pass  # Implement Gemini AI analysis
    
    async def daily_model_retrain():
        """Daily model retraining"""
        pass  # Implement model retraining
    
    async def health_check():
        """System health check"""
        pass  # Implement health check
    
    trading_scheduler.add_scheduled_task("hourly_analysis", "1h", hourly_analysis)
    trading_scheduler.add_scheduled_task("daily_model_retrain", "1d", daily_model_retrain)
    trading_scheduler.add_scheduled_task("health_check", "5m", health_check)
    
    return trading_scheduler
