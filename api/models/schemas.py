from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class OrderType(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class SignalType(str, Enum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"

# Market Data Schemas
class MarketData(BaseModel):
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    high: float
    low: float
    open: float
    close: float

class PredictionRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"
    use_ensemble: bool = True

class PredictionResponse(BaseModel):
    symbol: str
    prediction: SignalType
    confidence: float
    timestamp: datetime
    features_used: List[str]
    model_version: str

# Trading Schemas
class TradeSignal(BaseModel):
    symbol: str
    signal_type: SignalType
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    risk_reward_ratio: float
    timestamp: datetime

class OrderRequest(BaseModel):
    symbol: str
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class OrderResponse(BaseModel):
    order_id: str
    symbol: str
    order_type: OrderType
    quantity: float
    price: float
    status: OrderStatus
    timestamp: datetime

# Portfolio Schemas
class PortfolioStatus(BaseModel):
    total_balance: float
    available_balance: float
    unrealized_pnl: float
    realized_pnl: float
    positions: List[Dict[str, Any]]
    open_orders: List[Dict[str, Any]]

# AI Model Schemas
class ModelMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    last_updated: datetime

class ModelRetraining(BaseModel):
    model_name: str
    data_start_date: datetime
    data_end_date: datetime
    symbols: List[str]
    features: List[str]

# System Status
class SystemStatus(BaseModel):
    api_status: str
    database_status: str
    model_status: str
    trading_enabled: bool
    last_update: datetime
    active_strategies: List[str]

# Agent Schemas
class AgentStatus(BaseModel):
    agent_id: str = Field(..., description="The unique identifier for the agent.")
    status: str = Field(..., description="The current status of the agent (e.g., 'running', 'idle', 'error').")
    current_task: Optional[str] = Field(None, description="The task the agent is currently working on.")
    last_seen: datetime = Field(..., description="The last time the agent reported its status.")
    device_id: Optional[str] = Field(None, description="The device ID associated with this agent, if any.")
