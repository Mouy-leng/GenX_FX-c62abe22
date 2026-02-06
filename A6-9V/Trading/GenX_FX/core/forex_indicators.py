"""
Forex Indicators - Advanced technical indicators for forex and crypto trading
Supports BTCXAU, BTCUSD, XAUUSD and 10 forex pairs for 24/7 trading
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging


class IndicatorType(Enum):
    """Types of technical indicators"""
    TREND = "trend"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    OSCILLATOR = "oscillator"


@dataclass
class IndicatorConfig:
    """Configuration for indicators"""
    # RSI
    rsi_period: int = 14
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0
    
    # MACD
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    
    # Bollinger Bands
    bb_period: int = 20
    bb_std_dev: float = 2.0
    
    # Moving Averages
    sma_periods: List[int] = None
    ema_periods: List[int] = None
    
    # ATR
    atr_period: int = 14
    
    # Stochastic
    stoch_k_period: int = 14
    stoch_d_period: int = 3
    stoch_smooth: int = 3
    
    # ADX
    adx_period: int = 14
    
    # CCI
    cci_period: int = 20
    
    # Williams %R
    williams_period: int = 14
    
    # Ichimoku
    ichimoku_tenkan: int = 9
    ichimoku_kijun: int = 26
    ichimoku_senkou_b: int = 52
    
    def __post_init__(self):
        if self.sma_periods is None:
            self.sma_periods = [5, 10, 20, 50, 100, 200]
        if self.ema_periods is None:
            self.ema_periods = [9, 12, 21, 50, 100, 200]


class ForexIndicators:
    """
    Advanced technical indicators for forex and crypto trading
    Optimized for BTCXAU, BTCUSD, XAUUSD and major forex pairs
    """
    
    def __init__(self, config: IndicatorConfig = None):
        self.config = config or IndicatorConfig()
        self.logger = logging.getLogger(__name__)
    
    # ==========================================================================
    # TREND INDICATORS
    # ==========================================================================
    
    def calculate_sma(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return np.full(len(prices), np.nan)
        
        sma = np.convolve(prices, np.ones(period)/period, mode='valid')
        # Pad the beginning with NaN
        return np.concatenate([np.full(period-1, np.nan), sma])
    
    def calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return np.full(len(prices), np.nan)
        
        multiplier = 2 / (period + 1)
        ema = np.zeros(len(prices))
        ema[:period] = np.nan
        ema[period-1] = np.mean(prices[:period])
        
        for i in range(period, len(prices)):
            ema[i] = (prices[i] * multiplier) + (ema[i-1] * (1 - multiplier))
        
        return ema
    
    def calculate_wma(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Weighted Moving Average"""
        if len(prices) < period:
            return np.full(len(prices), np.nan)
        
        weights = np.arange(1, period + 1)
        wma = np.zeros(len(prices))
        wma[:period-1] = np.nan
        
        # Performance optimization: Cache the constant weight sum
        weight_sum = np.sum(weights)
        
        for i in range(period-1, len(prices)):
            wma[i] = np.sum(prices[i-period+1:i+1] * weights) / weight_sum
        
        return wma
    
    def calculate_dema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Double Exponential Moving Average"""
        ema1 = self.calculate_ema(prices, period)
        ema2 = self.calculate_ema(ema1, period)
        return 2 * ema1 - ema2
    
    def calculate_tema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Triple Exponential Moving Average"""
        ema1 = self.calculate_ema(prices, period)
        ema2 = self.calculate_ema(ema1, period)
        ema3 = self.calculate_ema(ema2, period)
        return 3 * ema1 - 3 * ema2 + ema3
    
    def calculate_kama(self, prices: np.ndarray, period: int = 10, 
                       fast: int = 2, slow: int = 30) -> np.ndarray:
        """Calculate Kaufman's Adaptive Moving Average"""
        if len(prices) < period:
            return np.full(len(prices), np.nan)
        
        # Calculate Efficiency Ratio
        change = np.abs(prices[period:] - prices[:-period])
        volatility = np.zeros(len(prices) - period)
        
        for i in range(len(volatility)):
            volatility[i] = np.sum(np.abs(np.diff(prices[i:i+period+1])))
        
        # Avoid division by zero
        volatility = np.where(volatility == 0, 1e-10, volatility)
        er = change / volatility
        
        # Calculate smoothing constants
        fast_sc = 2 / (fast + 1)
        slow_sc = 2 / (slow + 1)
        sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
        
        # Calculate KAMA
        kama = np.zeros(len(prices))
        kama[:period] = np.nan
        kama[period-1] = prices[period-1]
        
        for i in range(period, len(prices)):
            kama[i] = kama[i-1] + sc[i-period] * (prices[i] - kama[i-1])
        
        return kama
    
    # ==========================================================================
    # MOMENTUM INDICATORS
    # ==========================================================================
    
    def calculate_rsi(self, prices: np.ndarray, period: int = None) -> np.ndarray:
        """Calculate Relative Strength Index"""
        period = period or self.config.rsi_period
        
        if len(prices) < period + 1:
            return np.full(len(prices), 50.0)
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        rsi = np.zeros(len(prices))
        rsi[:period] = np.nan
        
        # Calculate initial average gain/loss
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        for i in range(period, len(prices) - 1):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi[i+1] = 100
            else:
                rs = avg_gain / avg_loss
                rsi[i+1] = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, prices: np.ndarray, 
                       fast: int = None, slow: int = None, 
                       signal: int = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        Returns: (macd_line, signal_line, histogram)
        """
        fast = fast or self.config.macd_fast
        slow = slow or self.config.macd_slow
        signal = signal or self.config.macd_signal
        
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_stochastic(self, high: np.ndarray, low: np.ndarray, 
                             close: np.ndarray, k_period: int = None,
                             d_period: int = None, smooth: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate Stochastic Oscillator
        Returns: (%K, %D)
        """
        k_period = k_period or self.config.stoch_k_period
        d_period = d_period or self.config.stoch_d_period
        smooth = smooth or self.config.stoch_smooth
        
        if len(close) < k_period:
            return np.full(len(close), 50.0), np.full(len(close), 50.0)
        
        stoch_k = np.zeros(len(close))
        stoch_k[:k_period-1] = np.nan
        
        for i in range(k_period-1, len(close)):
            highest_high = np.max(high[i-k_period+1:i+1])
            lowest_low = np.min(low[i-k_period+1:i+1])
            
            if highest_high == lowest_low:
                stoch_k[i] = 50.0
            else:
                stoch_k[i] = ((close[i] - lowest_low) / (highest_high - lowest_low)) * 100
        
        # Smooth %K
        stoch_k_smooth = self.calculate_sma(stoch_k, smooth)
        
        # Calculate %D
        stoch_d = self.calculate_sma(stoch_k_smooth, d_period)
        
        return stoch_k_smooth, stoch_d
    
    def calculate_williams_r(self, high: np.ndarray, low: np.ndarray,
                             close: np.ndarray, period: int = None) -> np.ndarray:
        """Calculate Williams %R"""
        period = period or self.config.williams_period
        
        if len(close) < period:
            return np.full(len(close), -50.0)
        
        williams_r = np.zeros(len(close))
        williams_r[:period-1] = np.nan
        
        for i in range(period-1, len(close)):
            highest_high = np.max(high[i-period+1:i+1])
            lowest_low = np.min(low[i-period+1:i+1])
            
            if highest_high == lowest_low:
                williams_r[i] = -50.0
            else:
                williams_r[i] = ((highest_high - close[i]) / (highest_high - lowest_low)) * -100
        
        return williams_r
    
    def calculate_cci(self, high: np.ndarray, low: np.ndarray,
                      close: np.ndarray, period: int = None) -> np.ndarray:
        """Calculate Commodity Channel Index"""
        period = period or self.config.cci_period
        
        # Typical price
        tp = (high + low + close) / 3
        
        if len(tp) < period:
            return np.full(len(tp), 0.0)
        
        cci = np.zeros(len(tp))
        cci[:period-1] = np.nan
        
        for i in range(period-1, len(tp)):
            sma_tp = np.mean(tp[i-period+1:i+1])
            mean_deviation = np.mean(np.abs(tp[i-period+1:i+1] - sma_tp))
            
            if mean_deviation == 0:
                cci[i] = 0.0
            else:
                cci[i] = (tp[i] - sma_tp) / (0.015 * mean_deviation)
        
        return cci
    
    def calculate_momentum(self, prices: np.ndarray, period: int = 10) -> np.ndarray:
        """Calculate Momentum Indicator"""
        if len(prices) < period + 1:
            return np.full(len(prices), 0.0)
        
        momentum = np.zeros(len(prices))
        momentum[:period] = np.nan
        momentum[period:] = prices[period:] - prices[:-period]
        
        return momentum
    
    def calculate_roc(self, prices: np.ndarray, period: int = 12) -> np.ndarray:
        """Calculate Rate of Change"""
        if len(prices) < period + 1:
            return np.full(len(prices), 0.0)
        
        roc = np.zeros(len(prices))
        roc[:period] = np.nan
        
        for i in range(period, len(prices)):
            if prices[i-period] != 0:
                roc[i] = ((prices[i] - prices[i-period]) / prices[i-period]) * 100
            else:
                roc[i] = 0.0
        
        return roc
    
    # ==========================================================================
    # VOLATILITY INDICATORS
    # ==========================================================================
    
    def calculate_bollinger_bands(self, prices: np.ndarray, 
                                  period: int = None, 
                                  std_dev: float = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate Bollinger Bands
        Returns: (upper_band, middle_band, lower_band)
        """
        period = period or self.config.bb_period
        std_dev = std_dev or self.config.bb_std_dev
        
        middle_band = self.calculate_sma(prices, period)
        
        if len(prices) < period:
            return (np.full(len(prices), np.nan), 
                    np.full(len(prices), np.nan), 
                    np.full(len(prices), np.nan))
        
        std = np.zeros(len(prices))
        std[:period-1] = np.nan
        
        for i in range(period-1, len(prices)):
            std[i] = np.std(prices[i-period+1:i+1])
        
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return upper_band, middle_band, lower_band
    
    def calculate_atr(self, high: np.ndarray, low: np.ndarray,
                      close: np.ndarray, period: int = None) -> np.ndarray:
        """Calculate Average True Range"""
        period = period or self.config.atr_period
        
        if len(close) < 2:
            return np.full(len(close), 0.0)
        
        # Calculate True Range
        tr = np.zeros(len(close))
        tr[0] = high[0] - low[0]
        
        for i in range(1, len(close)):
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i-1]),
                abs(low[i] - close[i-1])
            )
        
        # Calculate ATR using EMA
        atr = self.calculate_ema(tr, period)
        
        return atr
    
    def calculate_keltner_channels(self, high: np.ndarray, low: np.ndarray,
                                   close: np.ndarray, ema_period: int = 20,
                                   atr_period: int = 10, 
                                   multiplier: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate Keltner Channels
        Returns: (upper_channel, middle_channel, lower_channel)
        """
        middle = self.calculate_ema(close, ema_period)
        atr = self.calculate_atr(high, low, close, atr_period)
        
        upper = middle + (multiplier * atr)
        lower = middle - (multiplier * atr)
        
        return upper, middle, lower
    
    def calculate_donchian_channels(self, high: np.ndarray, low: np.ndarray,
                                    period: int = 20) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate Donchian Channels
        Returns: (upper_channel, middle_channel, lower_channel)
        """
        if len(high) < period:
            return (np.full(len(high), np.nan),
                    np.full(len(high), np.nan),
                    np.full(len(high), np.nan))
        
        upper = np.zeros(len(high))
        lower = np.zeros(len(low))
        upper[:period-1] = np.nan
        lower[:period-1] = np.nan
        
        for i in range(period-1, len(high)):
            upper[i] = np.max(high[i-period+1:i+1])
            lower[i] = np.min(low[i-period+1:i+1])
        
        middle = (upper + lower) / 2
        
        return upper, middle, lower
    
    # ==========================================================================
    # TREND STRENGTH INDICATORS
    # ==========================================================================
    
    def calculate_adx(self, high: np.ndarray, low: np.ndarray,
                      close: np.ndarray, period: int = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate ADX (Average Directional Index)
        Returns: (adx, +DI, -DI)
        """
        period = period or self.config.adx_period
        
        if len(close) < period + 1:
            return (np.full(len(close), np.nan),
                    np.full(len(close), np.nan),
                    np.full(len(close), np.nan))
        
        # Calculate +DM and -DM
        plus_dm = np.zeros(len(high))
        minus_dm = np.zeros(len(high))
        
        for i in range(1, len(high)):
            up_move = high[i] - high[i-1]
            down_move = low[i-1] - low[i]
            
            if up_move > down_move and up_move > 0:
                plus_dm[i] = up_move
            else:
                plus_dm[i] = 0
                
            if down_move > up_move and down_move > 0:
                minus_dm[i] = down_move
            else:
                minus_dm[i] = 0
        
        # Calculate ATR
        atr = self.calculate_atr(high, low, close, period)
        
        # Smoothed +DM and -DM
        plus_dm_smooth = self.calculate_ema(plus_dm, period)
        minus_dm_smooth = self.calculate_ema(minus_dm, period)
        
        # Calculate +DI and -DI
        plus_di = np.where(atr != 0, (plus_dm_smooth / atr) * 100, 0)
        minus_di = np.where(atr != 0, (minus_dm_smooth / atr) * 100, 0)
        
        # Calculate DX
        di_sum = plus_di + minus_di
        dx = np.where(di_sum != 0, (np.abs(plus_di - minus_di) / di_sum) * 100, 0)
        
        # Calculate ADX
        adx = self.calculate_ema(dx, period)
        
        return adx, plus_di, minus_di
    
    # ==========================================================================
    # VOLUME INDICATORS
    # ==========================================================================
    
    def calculate_obv(self, close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Calculate On-Balance Volume"""
        if len(close) < 2:
            return np.zeros(len(close))
        
        obv = np.zeros(len(close))
        obv[0] = volume[0]
        
        for i in range(1, len(close)):
            if close[i] > close[i-1]:
                obv[i] = obv[i-1] + volume[i]
            elif close[i] < close[i-1]:
                obv[i] = obv[i-1] - volume[i]
            else:
                obv[i] = obv[i-1]
        
        return obv
    
    def calculate_mfi(self, high: np.ndarray, low: np.ndarray,
                      close: np.ndarray, volume: np.ndarray,
                      period: int = 14) -> np.ndarray:
        """Calculate Money Flow Index"""
        if len(close) < period + 1:
            return np.full(len(close), 50.0)
        
        # Typical price
        tp = (high + low + close) / 3
        
        # Raw money flow
        mf = tp * volume
        
        # Positive and negative money flow
        pos_mf = np.zeros(len(close))
        neg_mf = np.zeros(len(close))
        
        for i in range(1, len(close)):
            if tp[i] > tp[i-1]:
                pos_mf[i] = mf[i]
            elif tp[i] < tp[i-1]:
                neg_mf[i] = mf[i]
        
        # Calculate MFI
        mfi = np.zeros(len(close))
        mfi[:period] = np.nan
        
        for i in range(period, len(close)):
            pos_sum = np.sum(pos_mf[i-period+1:i+1])
            neg_sum = np.sum(neg_mf[i-period+1:i+1])
            
            if neg_sum == 0:
                mfi[i] = 100.0
            else:
                mfr = pos_sum / neg_sum
                mfi[i] = 100 - (100 / (1 + mfr))
        
        return mfi
    
    def calculate_vwap(self, high: np.ndarray, low: np.ndarray,
                       close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Calculate Volume Weighted Average Price"""
        # Typical price
        tp = (high + low + close) / 3
        
        # Cumulative values
        cum_tp_vol = np.cumsum(tp * volume)
        cum_vol = np.cumsum(volume)
        
        # VWAP
        vwap = np.where(cum_vol != 0, cum_tp_vol / cum_vol, 0)
        
        return vwap
    
    # ==========================================================================
    # ICHIMOKU CLOUD
    # ==========================================================================
    
    def calculate_ichimoku(self, high: np.ndarray, low: np.ndarray,
                           close: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Calculate Ichimoku Cloud
        Returns dictionary with: tenkan_sen, kijun_sen, senkou_span_a, 
                                senkou_span_b, chikou_span
        """
        tenkan = self.config.ichimoku_tenkan
        kijun = self.config.ichimoku_kijun
        senkou_b = self.config.ichimoku_senkou_b
        
        # Tenkan-sen (Conversion Line)
        tenkan_sen = np.zeros(len(close))
        for i in range(tenkan-1, len(close)):
            tenkan_sen[i] = (np.max(high[i-tenkan+1:i+1]) + np.min(low[i-tenkan+1:i+1])) / 2
        tenkan_sen[:tenkan-1] = np.nan
        
        # Kijun-sen (Base Line)
        kijun_sen = np.zeros(len(close))
        for i in range(kijun-1, len(close)):
            kijun_sen[i] = (np.max(high[i-kijun+1:i+1]) + np.min(low[i-kijun+1:i+1])) / 2
        kijun_sen[:kijun-1] = np.nan
        
        # Senkou Span A (Leading Span A) - displaced forward by kijun periods
        senkou_span_a = (tenkan_sen + kijun_sen) / 2
        
        # Senkou Span B (Leading Span B) - displaced forward by kijun periods
        senkou_span_b = np.zeros(len(close))
        for i in range(senkou_b-1, len(close)):
            senkou_span_b[i] = (np.max(high[i-senkou_b+1:i+1]) + np.min(low[i-senkou_b+1:i+1])) / 2
        senkou_span_b[:senkou_b-1] = np.nan
        
        # Chikou Span (Lagging Span) - displaced back by kijun periods
        chikou_span = np.zeros(len(close))
        chikou_span[:-kijun] = close[kijun:]
        chikou_span[-kijun:] = np.nan
        
        return {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a,
            'senkou_span_b': senkou_span_b,
            'chikou_span': chikou_span
        }
    
    # ==========================================================================
    # COMPOSITE / ADVANCED INDICATORS
    # ==========================================================================
    
    def calculate_supertrend(self, high: np.ndarray, low: np.ndarray,
                             close: np.ndarray, period: int = 10,
                             multiplier: float = 3.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate SuperTrend indicator
        Returns: (supertrend, trend_direction)
        """
        atr = self.calculate_atr(high, low, close, period)
        hl2 = (high + low) / 2
        
        # Basic bands
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        
        supertrend = np.zeros(len(close))
        direction = np.zeros(len(close))  # 1 = uptrend, -1 = downtrend
        
        supertrend[0] = upper_band[0]
        direction[0] = 1
        
        for i in range(1, len(close)):
            # Calculate final bands
            if upper_band[i] < supertrend[i-1] or close[i-1] > supertrend[i-1]:
                upper_band[i] = upper_band[i]
            else:
                upper_band[i] = supertrend[i-1]
            
            if lower_band[i] > supertrend[i-1] or close[i-1] < supertrend[i-1]:
                lower_band[i] = lower_band[i]
            else:
                lower_band[i] = supertrend[i-1]
            
            # Determine trend
            if direction[i-1] == 1:  # Was in uptrend
                if close[i] < lower_band[i]:
                    direction[i] = -1
                    supertrend[i] = upper_band[i]
                else:
                    direction[i] = 1
                    supertrend[i] = lower_band[i]
            else:  # Was in downtrend
                if close[i] > upper_band[i]:
                    direction[i] = 1
                    supertrend[i] = lower_band[i]
                else:
                    direction[i] = -1
                    supertrend[i] = upper_band[i]
        
        return supertrend, direction
    
    def calculate_pivot_points(self, high: float, low: float,
                               close: float) -> Dict[str, float]:
        """
        Calculate Pivot Points (Standard)
        Returns dictionary with pivot point and support/resistance levels
        """
        pivot = (high + low + close) / 3
        
        r1 = (2 * pivot) - low
        s1 = (2 * pivot) - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        r3 = high + 2 * (pivot - low)
        s3 = low - 2 * (high - pivot)
        
        return {
            'pivot': pivot,
            'r1': r1, 's1': s1,
            'r2': r2, 's2': s2,
            'r3': r3, 's3': s3
        }
    
    def calculate_fibonacci_retracements(self, high: float, 
                                         low: float) -> Dict[str, float]:
        """
        Calculate Fibonacci Retracement levels
        """
        diff = high - low
        
        return {
            'level_0': high,
            'level_236': high - (diff * 0.236),
            'level_382': high - (diff * 0.382),
            'level_500': high - (diff * 0.500),
            'level_618': high - (diff * 0.618),
            'level_786': high - (diff * 0.786),
            'level_100': low
        }
    
    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================
    
    def calculate_all_indicators(self, high: np.ndarray, low: np.ndarray,
                                 close: np.ndarray, 
                                 volume: np.ndarray = None) -> Dict[str, Any]:
        """
        Calculate all indicators at once for efficiency
        Returns dictionary with all indicator values
        """
        results = {}
        
        # Trend indicators
        for period in self.config.sma_periods:
            results[f'sma_{period}'] = self.calculate_sma(close, period)
        
        for period in self.config.ema_periods:
            results[f'ema_{period}'] = self.calculate_ema(close, period)
        
        # Momentum indicators
        results['rsi'] = self.calculate_rsi(close)
        macd, signal, hist = self.calculate_macd(close)
        results['macd'] = macd
        results['macd_signal'] = signal
        results['macd_histogram'] = hist
        
        stoch_k, stoch_d = self.calculate_stochastic(high, low, close)
        results['stoch_k'] = stoch_k
        results['stoch_d'] = stoch_d
        
        results['williams_r'] = self.calculate_williams_r(high, low, close)
        results['cci'] = self.calculate_cci(high, low, close)
        results['momentum'] = self.calculate_momentum(close)
        results['roc'] = self.calculate_roc(close)
        
        # Volatility indicators
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(close)
        results['bb_upper'] = bb_upper
        results['bb_middle'] = bb_middle
        results['bb_lower'] = bb_lower
        
        results['atr'] = self.calculate_atr(high, low, close)
        
        kc_upper, kc_middle, kc_lower = self.calculate_keltner_channels(high, low, close)
        results['kc_upper'] = kc_upper
        results['kc_middle'] = kc_middle
        results['kc_lower'] = kc_lower
        
        # Trend strength
        adx, plus_di, minus_di = self.calculate_adx(high, low, close)
        results['adx'] = adx
        results['plus_di'] = plus_di
        results['minus_di'] = minus_di
        
        # Ichimoku
        ichimoku = self.calculate_ichimoku(high, low, close)
        results.update({f'ichimoku_{k}': v for k, v in ichimoku.items()})
        
        # SuperTrend
        supertrend, direction = self.calculate_supertrend(high, low, close)
        results['supertrend'] = supertrend
        results['supertrend_direction'] = direction
        
        # Volume indicators (if volume provided)
        if volume is not None:
            results['obv'] = self.calculate_obv(close, volume)
            results['mfi'] = self.calculate_mfi(high, low, close, volume)
            results['vwap'] = self.calculate_vwap(high, low, close, volume)
        
        return results
    
    def get_signal_strength(self, indicators: Dict[str, Any]) -> float:
        """
        Calculate overall signal strength from indicators
        Returns value between -1 (strong sell) and 1 (strong buy)
        """
        signals = []
        
        # RSI signal
        if 'rsi' in indicators:
            rsi = indicators['rsi'][-1] if not np.isnan(indicators['rsi'][-1]) else 50
            if rsi < self.config.rsi_oversold:
                signals.append(1.0)  # Oversold = buy signal
            elif rsi > self.config.rsi_overbought:
                signals.append(-1.0)  # Overbought = sell signal
            else:
                signals.append((50 - rsi) / 50)  # Neutral scaled
        
        # MACD signal
        if 'macd_histogram' in indicators:
            hist = indicators['macd_histogram'][-1] if not np.isnan(indicators['macd_histogram'][-1]) else 0
            signals.append(np.clip(hist / 10, -1, 1))
        
        # Stochastic signal
        if 'stoch_k' in indicators and 'stoch_d' in indicators:
            stoch_k = indicators['stoch_k'][-1] if not np.isnan(indicators['stoch_k'][-1]) else 50
            if stoch_k < 20:
                signals.append(1.0)
            elif stoch_k > 80:
                signals.append(-1.0)
            else:
                signals.append((50 - stoch_k) / 50)
        
        # ADX trend strength
        if 'adx' in indicators:
            adx = indicators['adx'][-1] if not np.isnan(indicators['adx'][-1]) else 0
            if adx > 25:  # Strong trend
                if 'plus_di' in indicators and 'minus_di' in indicators:
                    plus_di = indicators['plus_di'][-1]
                    minus_di = indicators['minus_di'][-1]
                    if plus_di > minus_di:
                        signals.append(0.5)  # Bullish trend
                    else:
                        signals.append(-0.5)  # Bearish trend
        
        # SuperTrend signal
        if 'supertrend_direction' in indicators:
            direction = indicators['supertrend_direction'][-1]
            signals.append(direction * 0.5)
        
        # Calculate average signal
        if signals:
            return np.mean(signals)
        return 0.0


# Convenience function for quick indicator calculation
def calculate_forex_indicators(high: np.ndarray, low: np.ndarray,
                               close: np.ndarray, volume: np.ndarray = None,
                               config: IndicatorConfig = None) -> Dict[str, Any]:
    """
    Convenience function to calculate all forex indicators
    """
    calculator = ForexIndicators(config)
    return calculator.calculate_all_indicators(high, low, close, volume)
