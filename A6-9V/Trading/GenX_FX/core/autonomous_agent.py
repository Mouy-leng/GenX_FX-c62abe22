"""
Autonomous Agent - Core self-managing trading agent
Handles decision making, learning, and self-improvement
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum

from collections import deque


class AgentState(Enum):
    """Agent operational states"""
    INITIALIZING = "initializing"
    LEARNING = "learning"
    TRADING = "trading"
    PAUSED = "paused"
    ERROR = "error"
    UPDATING = "updating"


@dataclass
class AgentConfig:
    """Configuration for autonomous agent"""
    max_risk_per_trade: float = 0.02
    max_daily_loss: float = 0.05
    learning_rate: float = 0.001
    update_frequency: int = 300  # seconds
    self_improvement_threshold: float = 0.1
    emergency_stop_loss: float = 0.1
    auto_update_enabled: bool = True
    human_approval_required: bool = True


class AutonomousAgent:
    """
    Advanced autonomous trading agent with self-management capabilities
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.state = AgentState.INITIALIZING
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.decision_engine = None
        self.self_manager = None
        self.risk_manager = None
        self.model_registry = None
        self.market_data = None
        self.broker = None
        self.metrics = None
        
        # Performance tracking - Use deque with maxlen to prevent memory leaks
        self.performance_history = deque(maxlen=1000)
        self.learning_metrics = {}
        self.last_update = datetime.now()
        
        # Self-improvement tracking
        self.improvement_suggestions = []
        self.auto_updates_applied = 0
        
    async def initialize(self, market_data=None, broker=None, model_registry=None, decision_engine=None, self_manager=None, metrics=None) -> bool:
        """Initialize the autonomous agent"""
        try:
            self.logger.info("Initializing autonomous agent...")
            self.state = AgentState.INITIALIZING
            
            # Set components if provided
            if market_data:
                self.market_data = market_data
            if broker:
                self.broker = broker
            if model_registry:
                self.model_registry = model_registry
            if decision_engine:
                self.decision_engine = decision_engine
            if self_manager:
                self.self_manager = self_manager
            if metrics:
                self.metrics = metrics
            
            # Initialize all components
            if self.market_data:
                await self.market_data.initialize()
            if self.broker:
                await self.broker.initialize()
            if self.model_registry:
                await self.model_registry.initialize()
            if self.decision_engine:
                await self.decision_engine.initialize()
            if self.self_manager:
                await self.self_manager.initialize()
            
            # Load latest models
            await self._load_latest_models()
            
            # Start monitoring
            asyncio.create_task(self._monitor_performance())
            asyncio.create_task(self._self_improvement_loop())
            
            self.state = AgentState.LEARNING
            self.logger.info("Autonomous agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agent: {e}")
            self.state = AgentState.ERROR
            return False
    
    async def start_trading(self) -> None:
        """Start autonomous trading"""
        if self.state != AgentState.LEARNING:
            raise RuntimeError("Agent must be in learning state to start trading")
        
        self.state = AgentState.TRADING
        self.logger.info("Starting autonomous trading...")
        
        # Main trading loop
        while self.state == AgentState.TRADING:
            try:
                await self._trading_cycle()
                await asyncio.sleep(1)  # 1 second cycle
            except Exception as e:
                self.logger.error(f"Error in trading cycle: {e}")
                await self._handle_error(e)
    
    async def _trading_cycle(self) -> None:
        """Single trading cycle"""
        # Get market data
        market_data = await self.market_data.get_latest_data()
        
        # Generate signals
        signals = await self.decision_engine.generate_signals(market_data)
        
        # Apply risk management
        filtered_signals = await self.risk_manager.filter_signals(signals)
        
        # Execute trades
        if filtered_signals:
            await self._execute_trades(filtered_signals)
        
        # Update performance metrics
        await self._update_performance_metrics()
    
    async def _execute_trades(self, signals: List[Dict]) -> None:
        """Execute trading signals"""
        for signal in signals:
            try:
                # Check risk limits
                if not await self.risk_manager.check_risk_limits(signal):
                    continue
                
                # Execute trade
                result = await self.broker.execute_trade(signal)
                
                if result['success']:
                    self.logger.info(f"Trade executed: {signal}")
                    await self.metrics.record_trade(result)
                else:
                    self.logger.warning(f"Trade failed: {result['error']}")
                    
            except Exception as e:
                self.logger.error(f"Error executing trade: {e}")
    
    async def _load_latest_models(self) -> None:
        """Load the latest trained models"""
        try:
            latest_models = await self.model_registry.get_latest_models()
            await self.decision_engine.load_models(latest_models)
            self.logger.info("Latest models loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load models: {e}")
    
    async def _monitor_performance(self) -> None:
        """Monitor agent performance and trigger improvements"""
        while True:
            try:
                # Collect performance metrics
                performance = await self.metrics.get_performance_summary()
                self.performance_history.append(performance)
                
                # Check for improvement opportunities
                if len(self.performance_history) > 10:
                    improvement_opportunity = await self._analyze_performance()
                    if improvement_opportunity:
                        await self._trigger_self_improvement(improvement_opportunity)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _self_improvement_loop(self) -> None:
        """Continuous self-improvement loop"""
        while True:
            try:
                if self.config.auto_update_enabled:
                    # Check for available improvements
                    improvements = await self.self_manager.get_available_improvements()
                    
                    for improvement in improvements:
                        if await self._should_apply_improvement(improvement):
                            await self._apply_improvement(improvement)
                
                await asyncio.sleep(self.config.update_frequency)
                
            except Exception as e:
                self.logger.error(f"Error in self-improvement loop: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_performance(self) -> Optional[Dict]:
        """Analyze performance for improvement opportunities"""
        recent_performance = self.performance_history[-10:]
        
        # Calculate performance metrics
        avg_return = np.mean([p['return'] for p in recent_performance])
        avg_sharpe = np.mean([p['sharpe_ratio'] for p in recent_performance])
        max_drawdown = max([p['max_drawdown'] for p in recent_performance])
        
        # Check for improvement opportunities
        if avg_return < 0.01 or avg_sharpe < 1.0 or max_drawdown > 0.05:
            return {
                'type': 'performance_degradation',
                'metrics': {
                    'avg_return': avg_return,
                    'avg_sharpe': avg_sharpe,
                    'max_drawdown': max_drawdown
                },
                'suggested_actions': [
                    'retrain_models',
                    'adjust_risk_parameters',
                    'update_strategy_parameters'
                ]
            }
        
        return None
    
    async def _trigger_self_improvement(self, opportunity: Dict) -> None:
        """Trigger self-improvement based on opportunity"""
        self.logger.info(f"Triggering self-improvement: {opportunity['type']}")
        
        for action in opportunity['suggested_actions']:
            if action == 'retrain_models':
                await self._retrain_models()
            elif action == 'adjust_risk_parameters':
                await self._adjust_risk_parameters()
            elif action == 'update_strategy_parameters':
                await self._update_strategy_parameters()
    
    async def _should_apply_improvement(self, improvement: Dict) -> bool:
        """Determine if improvement should be applied"""
        # Check if human approval is required
        if self.config.human_approval_required and improvement['risk_level'] == 'high':
            return False
        
        # Check improvement threshold
        if improvement['confidence'] < self.config.self_improvement_threshold:
            return False
        
        return True
    
    async def _apply_improvement(self, improvement: Dict) -> None:
        """Apply self-improvement"""
        try:
            self.state = AgentState.UPDATING
            self.logger.info(f"Applying improvement: {improvement['type']}")
            
            # Apply the improvement
            result = await self.self_manager.apply_improvement(improvement)
            
            if result['success']:
                self.auto_updates_applied += 1
                self.logger.info(f"Improvement applied successfully: {improvement['type']}")
                
                # Validate the improvement
                await self._validate_improvement(improvement)
            else:
                self.logger.error(f"Failed to apply improvement: {result['error']}")
                
        except Exception as e:
            self.logger.error(f"Error applying improvement: {e}")
        finally:
            self.state = AgentState.TRADING
    
    async def _retrain_models(self) -> None:
        """Retrain models with latest data"""
        self.logger.info("Retraining models...")
        
        # Get latest training data
        training_data = await self.market_data.get_training_data()
        
        # Retrain models
        new_models = await self.decision_engine.retrain_models(training_data)
        
        # Register new models
        await self.model_registry.register_models(new_models)
        
        # Load new models
        await self._load_latest_models()
    
    async def _adjust_risk_parameters(self) -> None:
        """Adjust risk management parameters"""
        self.logger.info("Adjusting risk parameters...")
        
        # Analyze recent performance
        recent_trades = await self.metrics.get_recent_trades()
        
        # Calculate optimal risk parameters
        optimal_params = await self.risk_manager.calculate_optimal_parameters(recent_trades)
        
        # Update risk parameters
        await self.risk_manager.update_parameters(optimal_params)
    
    async def _update_strategy_parameters(self) -> None:
        """Update strategy parameters"""
        self.logger.info("Updating strategy parameters...")
        
        # Get current market conditions
        market_conditions = await self.market_data.get_market_conditions()
        
        # Calculate optimal strategy parameters
        optimal_params = await self.decision_engine.calculate_optimal_parameters(market_conditions)
        
        # Update strategy parameters
        await self.decision_engine.update_parameters(optimal_params)
    
    async def _validate_improvement(self, improvement: Dict) -> None:
        """Validate that improvement is working correctly"""
        # Run validation tests
        validation_results = await self.self_manager.validate_improvement(improvement)
        
        if not validation_results['passed']:
            self.logger.warning(f"Improvement validation failed: {validation_results['issues']}")
            # Rollback if necessary
            await self._rollback_improvement(improvement)
    
    async def _rollback_improvement(self, improvement: Dict) -> None:
        """Rollback failed improvement"""
        self.logger.info(f"Rolling back improvement: {improvement['type']}")
        
        try:
            await self.self_manager.rollback_improvement(improvement)
            self.logger.info("Improvement rolled back successfully")
        except Exception as e:
            self.logger.error(f"Failed to rollback improvement: {e}")
    
    async def _update_performance_metrics(self) -> None:
        """Update performance metrics"""
        current_performance = {
            'timestamp': datetime.now(),
            'return': await self.metrics.get_current_return(),
            'sharpe_ratio': await self.metrics.get_sharpe_ratio(),
            'max_drawdown': await self.metrics.get_max_drawdown(),
            'win_rate': await self.metrics.get_win_rate(),
            'total_trades': await self.metrics.get_total_trades()
        }
        
        # deque automatically handles maxlen, no need for manual trimming
        self.performance_history.append(current_performance)
    
    async def _handle_error(self, error: Exception) -> None:
        """Handle errors gracefully"""
        self.logger.error(f"Handling error: {error}")
        
        # Check if error is critical
        if isinstance(error, (ConnectionError, TimeoutError)):
            self.state = AgentState.ERROR
            await self._emergency_stop()
        else:
            # Try to recover
            await asyncio.sleep(5)
            if self.state == AgentState.ERROR:
                self.state = AgentState.TRADING
    
    async def _emergency_stop(self) -> None:
        """Emergency stop all trading"""
        self.logger.critical("Emergency stop triggered!")
        
        # Close all positions
        await self.broker.close_all_positions()
        
        # Stop trading
        self.state = AgentState.PAUSED
        
        # Notify administrators
        await self.metrics.send_alert("EMERGENCY_STOP", "Trading stopped due to critical error")
    
    async def pause_trading(self) -> None:
        """Pause trading"""
        self.state = AgentState.PAUSED
        self.logger.info("Trading paused")
    
    async def resume_trading(self) -> None:
        """Resume trading"""
        if self.state == AgentState.PAUSED:
            self.state = AgentState.TRADING
            self.logger.info("Trading resumed")
    
    async def shutdown(self) -> None:
        """Graceful shutdown"""
        self.logger.info("Shutting down autonomous agent...")
        
        # Stop trading
        self.state = AgentState.PAUSED
        
        # Close all positions
        await self.broker.close_all_positions()
        
        # Save state
        await self._save_state()
        
        self.logger.info("Autonomous agent shutdown complete")
    
    async def _save_state(self) -> None:
        """Save agent state"""
        state = {
            'performance_history': self.performance_history,
            'learning_metrics': self.learning_metrics,
            'auto_updates_applied': self.auto_updates_applied,
            'last_update': self.last_update.isoformat()
        }
        
        # Save to persistent storage
        await self.self_manager.save_state(state)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            'state': self.state.value,
            'performance_history_count': len(self.performance_history),
            'auto_updates_applied': self.auto_updates_applied,
            'last_update': self.last_update.isoformat(),
            'config': self.config.__dict__
        }
