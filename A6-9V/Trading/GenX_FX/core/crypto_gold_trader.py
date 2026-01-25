"""
Crypto Gold Trader - Specialized trading for BTCXAU, BTCUSD, XAUUSD
24/7 Trading for cryptocurrency and gold pairs
Device: NUNA 💻 | User: @mouyleng 🧑‍💻 | Org: @A6-9V 🏙️
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from .forex_indicators import ForexIndicators, IndicatorConfig


class CryptoGoldPair(Enum):
    """Supported crypto/gold pairs for 24/7 trading"""
    BTCUSD = "BTCUSD"      # Bitcoin / US Dollar
    XAUUSD = "XAUUSD"      # Gold / US Dollar
    BTCXAU = "BTCXAU"      # Bitcoin / Gold (Cross-pair)


@dataclass
class PairConfig:
    """Configuration for a trading pair"""
    symbol: str
    pip_value: float
    lot_size: float
    min_lot: float
    leverage: int
    spread_tolerance: float
    max_position_pct: float
    stop_loss_pct: float
    take_profit_pct: float
    is_24_7: bool = True


@dataclass
class TradingSignal:
    """Trading signal for crypto/gold pairs"""
    symbol: str
    signal_type: str  # BUY, SELL, HOLD, CLOSE
    confidence: float
    strength: float
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    indicators: Dict[str, float]
    timestamp: datetime
    reasoning: str = ""


class CryptoGoldTrader:
    """
    Specialized trader for BTCXAU, BTCUSD, XAUUSD
    
    Features:
    - 24/7 continuous trading
    - Cross-pair arbitrage detection (BTC vs Gold)
    - Advanced indicator analysis
    - Risk-adjusted position sizing
    - ML-enhanced signal generation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize indicator calculator
        self.indicators = ForexIndicators()
        
        # Pair configurations
        self.pair_configs: Dict[str, PairConfig] = self._initialize_pair_configs()
        
        # Trading state
        self.is_active = False
        self.current_positions: Dict[str, Dict] = {}
        self.signal_history: List[TradingSignal] = []
        
        # Performance tracking
        self.performance: Dict[str, Dict] = {}
        for pair in CryptoGoldPair:
            self.performance[pair.value] = {
                'total_trades': 0,
                'winning_trades': 0,
                'total_pnl': 0.0,
                'max_drawdown': 0.0
            }
        
        # Market data cache
        self.market_data_cache: Dict[str, pd.DataFrame] = {}
        self.last_update: Dict[str, datetime] = {}
    
    def _initialize_pair_configs(self) -> Dict[str, PairConfig]:
        """Initialize pair-specific configurations"""
        return {
            CryptoGoldPair.BTCUSD.value: PairConfig(
                symbol="BTCUSD",
                pip_value=0.01,
                lot_size=1,
                min_lot=0.001,
                leverage=10,
                spread_tolerance=50.0,  # $50 spread tolerance
                max_position_pct=0.5,   # 50% max allocation
                stop_loss_pct=0.03,     # 3% stop loss
                take_profit_pct=0.05,   # 5% take profit
                is_24_7=True
            ),
            CryptoGoldPair.XAUUSD.value: PairConfig(
                symbol="XAUUSD",
                pip_value=0.01,
                lot_size=100,
                min_lot=0.01,
                leverage=50,
                spread_tolerance=0.50,   # $0.50 spread tolerance
                max_position_pct=0.3,    # 30% max allocation
                stop_loss_pct=0.02,      # 2% stop loss
                take_profit_pct=0.04,    # 4% take profit
                is_24_7=True
            ),
            CryptoGoldPair.BTCXAU.value: PairConfig(
                symbol="BTCXAU",
                pip_value=0.0001,
                lot_size=1,
                min_lot=0.001,
                leverage=5,
                spread_tolerance=0.01,    # 1% spread tolerance
                max_position_pct=0.2,     # 20% max allocation
                stop_loss_pct=0.04,       # 4% stop loss
                take_profit_pct=0.06,     # 6% take profit
                is_24_7=True
            )
        }
    
    async def analyze_pair(self, symbol: str, 
                          ohlcv_data: pd.DataFrame) -> TradingSignal:
        """
        Analyze a crypto/gold pair and generate trading signal
        
        Args:
            symbol: Trading pair symbol
            ohlcv_data: OHLCV data with columns: open, high, low, close, volume
        
        Returns:
            TradingSignal with recommendation
        """
        try:
            config = self.pair_configs.get(symbol)
            if not config:
                raise ValueError(f"Unknown symbol: {symbol}")
            
            # Extract price data
            high = ohlcv_data['high'].values
            low = ohlcv_data['low'].values
            close = ohlcv_data['close'].values
            volume = ohlcv_data['volume'].values if 'volume' in ohlcv_data else None
            
            current_price = close[-1]
            
            # Calculate all indicators
            all_indicators = self.indicators.calculate_all_indicators(
                high, low, close, volume
            )
            
            # Analyze signals from different indicator groups
            trend_signal = self._analyze_trend(all_indicators, close)
            momentum_signal = self._analyze_momentum(all_indicators)
            volatility_signal = self._analyze_volatility(all_indicators, symbol)
            
            # Combine signals with weights
            combined_signal = (
                trend_signal * 0.35 +
                momentum_signal * 0.40 +
                volatility_signal * 0.25
            )
            
            # Determine signal type
            if combined_signal > 0.3:
                signal_type = "BUY"
            elif combined_signal < -0.3:
                signal_type = "SELL"
            else:
                signal_type = "HOLD"
            
            # Calculate confidence
            confidence = min(abs(combined_signal), 1.0)
            
            # Calculate position parameters
            stop_loss = self._calculate_stop_loss(
                current_price, signal_type, all_indicators, config
            )
            take_profit = self._calculate_take_profit(
                current_price, signal_type, all_indicators, config
            )
            position_size = self._calculate_position_size(confidence, config)
            
            # Build indicator summary
            indicator_summary = {
                'rsi': float(all_indicators['rsi'][-1]) if not np.isnan(all_indicators['rsi'][-1]) else 50,
                'macd': float(all_indicators['macd'][-1]) if not np.isnan(all_indicators['macd'][-1]) else 0,
                'bb_position': self._get_bb_position(current_price, all_indicators),
                'atr': float(all_indicators['atr'][-1]) if not np.isnan(all_indicators['atr'][-1]) else 0,
                'adx': float(all_indicators['adx'][-1]) if not np.isnan(all_indicators['adx'][-1]) else 0,
                'trend_signal': trend_signal,
                'momentum_signal': momentum_signal,
                'volatility_signal': volatility_signal
            }
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                symbol, signal_type, indicator_summary, combined_signal
            )
            
            signal = TradingSignal(
                symbol=symbol,
                signal_type=signal_type,
                confidence=confidence,
                strength=abs(combined_signal),
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                position_size=position_size,
                indicators=indicator_summary,
                timestamp=datetime.now(),
                reasoning=reasoning
            )
            
            # Store in history
            self.signal_history.append(signal)
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            raise
    
    def _analyze_trend(self, indicators: Dict[str, np.ndarray], 
                       close: np.ndarray) -> float:
        """Analyze trend indicators"""
        signals = []
        
        # EMA crossover signals
        if 'ema_9' in indicators and 'ema_21' in indicators:
            ema_9 = indicators['ema_9'][-1]
            ema_21 = indicators['ema_21'][-1]
            if not np.isnan(ema_9) and not np.isnan(ema_21):
                if ema_9 > ema_21:
                    signals.append(0.5)
                else:
                    signals.append(-0.5)
        
        # ADX trend strength
        if 'adx' in indicators and 'plus_di' in indicators and 'minus_di' in indicators:
            adx = indicators['adx'][-1]
            plus_di = indicators['plus_di'][-1]
            minus_di = indicators['minus_di'][-1]
            
            if not np.isnan(adx) and adx > 25:  # Strong trend
                if plus_di > minus_di:
                    signals.append(min(adx / 50, 1.0))
                else:
                    signals.append(-min(adx / 50, 1.0))
        
        # SuperTrend
        if 'supertrend_direction' in indicators:
            direction = indicators['supertrend_direction'][-1]
            signals.append(direction * 0.5)
        
        # Ichimoku Cloud
        if 'ichimoku_tenkan_sen' in indicators and 'ichimoku_kijun_sen' in indicators:
            tenkan = indicators['ichimoku_tenkan_sen'][-1]
            kijun = indicators['ichimoku_kijun_sen'][-1]
            if not np.isnan(tenkan) and not np.isnan(kijun):
                if tenkan > kijun:
                    signals.append(0.3)
                else:
                    signals.append(-0.3)
        
        return np.mean(signals) if signals else 0.0
    
    def _analyze_momentum(self, indicators: Dict[str, np.ndarray]) -> float:
        """Analyze momentum indicators"""
        signals = []
        
        # RSI
        if 'rsi' in indicators:
            rsi = indicators['rsi'][-1]
            if not np.isnan(rsi):
                if rsi < 30:
                    signals.append(1.0)  # Oversold
                elif rsi > 70:
                    signals.append(-1.0)  # Overbought
                else:
                    signals.append((50 - rsi) / 50)
        
        # MACD
        if 'macd' in indicators and 'macd_signal' in indicators:
            macd = indicators['macd'][-1]
            signal = indicators['macd_signal'][-1]
            if not np.isnan(macd) and not np.isnan(signal):
                if macd > signal:
                    signals.append(0.5)
                else:
                    signals.append(-0.5)
        
        # Stochastic
        if 'stoch_k' in indicators and 'stoch_d' in indicators:
            stoch_k = indicators['stoch_k'][-1]
            stoch_d = indicators['stoch_d'][-1]
            if not np.isnan(stoch_k):
                if stoch_k < 20:
                    signals.append(0.8)
                elif stoch_k > 80:
                    signals.append(-0.8)
                elif stoch_k > stoch_d:
                    signals.append(0.3)
                else:
                    signals.append(-0.3)
        
        # Williams %R
        if 'williams_r' in indicators:
            wr = indicators['williams_r'][-1]
            if not np.isnan(wr):
                if wr < -80:
                    signals.append(0.7)
                elif wr > -20:
                    signals.append(-0.7)
        
        # CCI
        if 'cci' in indicators:
            cci = indicators['cci'][-1]
            if not np.isnan(cci):
                if cci < -100:
                    signals.append(0.6)
                elif cci > 100:
                    signals.append(-0.6)
        
        return np.mean(signals) if signals else 0.0
    
    def _analyze_volatility(self, indicators: Dict[str, np.ndarray],
                           symbol: str) -> float:
        """Analyze volatility for trading suitability"""
        signals = []
        
        # Bollinger Band position
        if 'bb_upper' in indicators and 'bb_lower' in indicators and 'bb_middle' in indicators:
            bb_upper = indicators['bb_upper'][-1]
            bb_lower = indicators['bb_lower'][-1]
            bb_middle = indicators['bb_middle'][-1]
            
            # Check for squeeze (low volatility = potential breakout)
            bb_width = (bb_upper - bb_lower) / bb_middle if bb_middle != 0 else 0
            if bb_width < 0.02:  # Squeeze
                signals.append(0.3)  # Neutral but prepared
        
        # ATR-based volatility
        if 'atr' in indicators:
            atr = indicators['atr'][-1]
            # Higher ATR = higher volatility = larger potential moves
            if not np.isnan(atr) and atr > 0:
                # Normalize by symbol
                config = self.pair_configs.get(symbol)
                if config:
                    relative_atr = atr / config.spread_tolerance
                    if relative_atr > 2:  # High volatility
                        signals.append(0.2)  # Slightly bullish on volatility
        
        return np.mean(signals) if signals else 0.0
    
    def _get_bb_position(self, price: float, indicators: Dict[str, np.ndarray]) -> float:
        """Get price position within Bollinger Bands (0-1)"""
        if 'bb_upper' in indicators and 'bb_lower' in indicators:
            upper = indicators['bb_upper'][-1]
            lower = indicators['bb_lower'][-1]
            if not np.isnan(upper) and not np.isnan(lower) and upper != lower:
                return (price - lower) / (upper - lower)
        return 0.5
    
    def _calculate_stop_loss(self, price: float, signal_type: str,
                            indicators: Dict[str, np.ndarray],
                            config: PairConfig) -> float:
        """Calculate stop loss price"""
        # Use ATR-based stop loss
        atr = indicators['atr'][-1] if not np.isnan(indicators['atr'][-1]) else price * 0.02
        atr_multiplier = 2.0
        
        if signal_type == "BUY":
            return max(price - (atr * atr_multiplier), price * (1 - config.stop_loss_pct))
        elif signal_type == "SELL":
            return min(price + (atr * atr_multiplier), price * (1 + config.stop_loss_pct))
        return price
    
    def _calculate_take_profit(self, price: float, signal_type: str,
                              indicators: Dict[str, np.ndarray],
                              config: PairConfig) -> float:
        """Calculate take profit price"""
        # Use ATR-based take profit (2:1 reward-risk ratio)
        atr = indicators['atr'][-1] if not np.isnan(indicators['atr'][-1]) else price * 0.02
        atr_multiplier = 4.0
        
        if signal_type == "BUY":
            return min(price + (atr * atr_multiplier), price * (1 + config.take_profit_pct))
        elif signal_type == "SELL":
            return max(price - (atr * atr_multiplier), price * (1 - config.take_profit_pct))
        return price
    
    def _calculate_position_size(self, confidence: float, 
                                config: PairConfig) -> float:
        """Calculate position size based on confidence and limits"""
        base_size = config.min_lot * 10  # Base position
        confidence_multiplier = confidence  # Scale by confidence
        
        position_size = base_size * confidence_multiplier
        max_size = config.lot_size * config.max_position_pct
        
        return min(position_size, max_size)
    
    def _generate_reasoning(self, symbol: str, signal_type: str,
                           indicators: Dict[str, float],
                           combined_signal: float) -> str:
        """Generate human-readable reasoning for the signal"""
        reasons = []
        
        # RSI reasoning
        rsi = indicators.get('rsi', 50)
        if rsi < 30:
            reasons.append(f"RSI ({rsi:.1f}) indicates oversold conditions")
        elif rsi > 70:
            reasons.append(f"RSI ({rsi:.1f}) indicates overbought conditions")
        
        # MACD reasoning
        macd = indicators.get('macd', 0)
        if macd > 0:
            reasons.append(f"MACD ({macd:.4f}) shows bullish momentum")
        elif macd < 0:
            reasons.append(f"MACD ({macd:.4f}) shows bearish momentum")
        
        # Trend reasoning
        adx = indicators.get('adx', 0)
        if adx > 25:
            reasons.append(f"ADX ({adx:.1f}) indicates strong trend")
        else:
            reasons.append(f"ADX ({adx:.1f}) indicates ranging market")
        
        # BB position
        bb_pos = indicators.get('bb_position', 0.5)
        if bb_pos < 0.2:
            reasons.append("Price near lower Bollinger Band")
        elif bb_pos > 0.8:
            reasons.append("Price near upper Bollinger Band")
        
        reasoning = f"{signal_type} signal for {symbol} (confidence: {abs(combined_signal):.2f}). "
        reasoning += " ".join(reasons)
        
        return reasoning
    
    async def analyze_btc_gold_correlation(self, 
                                          btc_data: pd.DataFrame,
                                          gold_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze BTC/Gold correlation for BTCXAU trading
        
        Returns correlation analysis and potential arbitrage opportunities
        """
        try:
            # Calculate returns
            btc_returns = btc_data['close'].pct_change().dropna()
            gold_returns = gold_data['close'].pct_change().dropna()
            
            # Align data
            min_len = min(len(btc_returns), len(gold_returns))
            btc_returns = btc_returns[-min_len:]
            gold_returns = gold_returns[-min_len:]
            
            # Calculate correlation
            correlation = np.corrcoef(btc_returns, gold_returns)[0, 1]
            
            # Calculate rolling correlation
            rolling_corr = pd.Series(btc_returns.values).rolling(20).corr(
                pd.Series(gold_returns.values)
            )
            
            # Calculate BTCXAU implied price
            btc_price = btc_data['close'].iloc[-1]
            gold_price = gold_data['close'].iloc[-1]
            btcxau_implied = btc_price / gold_price
            
            # Detect divergence
            btc_momentum = (btc_data['close'].iloc[-1] / btc_data['close'].iloc[-20] - 1) * 100
            gold_momentum = (gold_data['close'].iloc[-1] / gold_data['close'].iloc[-20] - 1) * 100
            
            divergence = btc_momentum - gold_momentum
            
            # Trading recommendation
            if abs(correlation) < 0.3 and abs(divergence) > 10:
                # Low correlation + high divergence = potential mean reversion
                if divergence > 0:
                    recommendation = "BTCXAU may be overvalued - consider SELL"
                else:
                    recommendation = "BTCXAU may be undervalued - consider BUY"
            else:
                recommendation = "No clear arbitrage opportunity"
            
            return {
                'correlation': float(correlation),
                'rolling_correlation': rolling_corr.iloc[-1] if len(rolling_corr) > 0 else None,
                'btc_price': float(btc_price),
                'gold_price': float(gold_price),
                'btcxau_implied': float(btcxau_implied),
                'btc_momentum_20d': float(btc_momentum),
                'gold_momentum_20d': float(gold_momentum),
                'divergence': float(divergence),
                'recommendation': recommendation,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing BTC/Gold correlation: {e}")
            return {}
    
    async def get_24_7_trading_status(self) -> Dict[str, Any]:
        """Get 24/7 trading status for all crypto/gold pairs"""
        status = {
            'is_active': self.is_active,
            'pairs': {},
            'total_positions': len(self.current_positions),
            'performance_summary': {}
        }
        
        for pair in CryptoGoldPair:
            config = self.pair_configs[pair.value]
            status['pairs'][pair.value] = {
                'is_24_7': config.is_24_7,
                'max_position_pct': config.max_position_pct,
                'current_position': self.current_positions.get(pair.value),
                'performance': self.performance[pair.value]
            }
        
        return status
    
    def get_latest_signals(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get latest trading signals"""
        signals = self.signal_history[-count:]
        return [
            {
                'symbol': s.symbol,
                'signal_type': s.signal_type,
                'confidence': s.confidence,
                'entry_price': s.entry_price,
                'stop_loss': s.stop_loss,
                'take_profit': s.take_profit,
                'reasoning': s.reasoning,
                'timestamp': s.timestamp.isoformat()
            }
            for s in signals
        ]


# Create global instance
crypto_gold_trader = CryptoGoldTrader()


async def analyze_all_crypto_gold_pairs(btc_data: pd.DataFrame = None,
                                        gold_data: pd.DataFrame = None,
                                        btcxau_data: pd.DataFrame = None) -> Dict[str, TradingSignal]:
    """
    Analyze all crypto/gold pairs and return signals
    """
    signals = {}
    
    if btc_data is not None and len(btc_data) > 0:
        signals['BTCUSD'] = await crypto_gold_trader.analyze_pair('BTCUSD', btc_data)
    
    if gold_data is not None and len(gold_data) > 0:
        signals['XAUUSD'] = await crypto_gold_trader.analyze_pair('XAUUSD', gold_data)
    
    if btcxau_data is not None and len(btcxau_data) > 0:
        signals['BTCXAU'] = await crypto_gold_trader.analyze_pair('BTCXAU', btcxau_data)
    
    return signals
