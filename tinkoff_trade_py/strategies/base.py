from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from utils import logger


@dataclass
class Signal:
    """Торговый сигнал"""
    action: str  # 'buy', 'sell', 'hold'
    instrument_uid: str
    quantity: int
    price: Optional[float] = None
    reason: str = ""
    confidence: float = 1.0  # 0-1


class BaseStrategy(ABC):
    """Базовый класс для всех торговых стратегий"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
        self.logger = logger
    
    @abstractmethod
    def analyze(self, instrument_uid: str, data: Dict[str, Any]) -> Signal:
        """
        Анализ данных и генерация торгового сигнала
        
        Args:
            instrument_uid: UID инструмента
            data: Словарь с данными (цены, индикаторы, свечи)
            
        Returns:
            Signal: Торговый сигнал
        """
        pass
    
    def calculate_rsi(self, prices: list, period: int = 14) -> float:
        """Расчёт RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return 50.0  # Нейтральное значение
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            diff = prices[i] - prices[i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))
        
        # Берём последние 'period' значений
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def validate_signal(self, signal: Signal) -> bool:
        """Валидация сигнала перед отправкой"""
        if signal.action == 'hold':
            return False
        
        if signal.quantity <= 0:
            self.logger.warning(f"Неверное количество: {signal.quantity}")
            return False
        
        if signal.action not in ['buy', 'sell']:
            self.logger.warning(f"Неизвестное действие: {signal.action}")
            return False
        
        return True