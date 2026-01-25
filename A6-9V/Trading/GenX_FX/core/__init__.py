"""
GenX-FX Autonomous Trading System Core
Advanced self-managing trading system with AI/ML capabilities

Device: NUNA 💻 | User: @mouyleng 🧑‍💻 | Org: @A6-9V 🏙️
Supports: BTCXAU, BTCUSD, XAUUSD + 10 Forex pairs (24/7 Trading)
"""

__version__ = "2.0.0"
__author__ = "A6-9V"

from .autonomous_agent import AutonomousAgent
from .self_manager import SelfManager
from .decision_engine import DecisionEngine
from .risk_manager import RiskManager
from .forex_indicators import ForexIndicators, IndicatorConfig, calculate_forex_indicators
from .trading_scheduler import TradingScheduler, TradingSession, trading_scheduler, initialize_scheduler
from .crypto_gold_trader import CryptoGoldTrader, CryptoGoldPair, crypto_gold_trader, analyze_all_crypto_gold_pairs

__all__ = [
    # Core agents
    "AutonomousAgent",
    "SelfManager", 
    "DecisionEngine",
    "RiskManager",
    # Forex indicators
    "ForexIndicators",
    "IndicatorConfig",
    "calculate_forex_indicators",
    # Trading scheduler (24/7)
    "TradingScheduler",
    "TradingSession",
    "trading_scheduler",
    "initialize_scheduler",
    # Crypto/Gold trader
    "CryptoGoldTrader",
    "CryptoGoldPair",
    "crypto_gold_trader",
    "analyze_all_crypto_gold_pairs",
]
