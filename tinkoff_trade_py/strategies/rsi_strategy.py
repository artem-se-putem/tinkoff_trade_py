# strategies/rsi_strategy.py
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import deque

from .base import BaseStrategy, Signal
from utils import logger


class RSIStrategy(BaseStrategy):
    """RSI (Relative Strength Index) стратегия"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Параметры стратегии
        self.rsi_period = config.get('rsi_period', 14)
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        self.order_quantity = config.get('order_quantity', 1)
        
        # Хранение истории цен для каждого инструмента
        self.price_history: Dict[str, List[float]] = {}
        
        # Отслеживание последнего сигнала
        self.last_signal: Dict[str, str] = {}
        
        logger.info(f"RSI стратегия инициализирована: "
                   f"period={self.rsi_period}, "
                   f"oversold={self.rsi_oversold}, "
                   f"overbought={self.rsi_overbought}")
    
    def set_price_history(self, instrument_uid: str, prices: List[float]):
        """Установить историю цен для инструмента"""
        self.price_history[instrument_uid] = prices.copy()
        logger.info(f"{instrument_uid}: установлена история из {len(prices)} цен")
    
    def add_price(self, instrument_uid: str, price: float):
        """Добавить новую цену в историю"""
        if instrument_uid not in self.price_history:
            self.price_history[instrument_uid] = []
        self.price_history[instrument_uid].append(price)
        # Ограничиваем размер истории
        if len(self.price_history[instrument_uid]) > self.rsi_period * 2:
            self.price_history[instrument_uid] = self.price_history[instrument_uid][-self.rsi_period * 2:]
    
    def analyze(self, instrument_uid: str, data: Dict[str, Any]) -> Signal:
        """
        Анализ данных и генерация сигнала
        """
        current_price = data.get('current_price')
        if not current_price:
            return Signal('hold', instrument_uid, 0, reason="Нет текущей цены")
        
        # Получаем историю цен
        prices = data.get('prices')
        if prices:
            # Если переданы цены, устанавливаем их
            self.set_price_history(instrument_uid, prices)
        else:
            # Используем сохранённую историю
            prices = self.price_history.get(instrument_uid, [])
        
        # Добавляем текущую цену
        self.add_price(instrument_uid, current_price)
        prices = self.price_history.get(instrument_uid, [])
        
        logger.debug(f"{instrument_uid}: история цен из {len(prices)} элементов, RSI период={self.rsi_period}")
        
        # Проверяем, достаточно ли данных
        if len(prices) < self.rsi_period + 1:
            return Signal(
                'hold', instrument_uid, 0,
                reason=f"Недостаточно данных: {len(prices)}/{self.rsi_period + 1}"
            )
        
        # Получаем или вычисляем RSI
        rsi = data.get('rsi')
        if rsi is None:
            rsi = self.calculate_rsi(prices, self.rsi_period)
        
        # Генерируем сигнал
        signal = self._generate_signal(instrument_uid, current_price, rsi)
        
        logger.info(
            f"{instrument_uid} | RSI={rsi:.1f} | "
            f"Цена={current_price:.2f} | "
            f"Сигнал={signal.action.upper()} | {signal.reason}"
        )
        
        return signal
    
    def _generate_signal(self, instrument_uid: str, price: float, rsi: float) -> Signal:
        """Генерация торгового сигнала на основе RSI"""
        
        last_action = self.last_signal.get(instrument_uid, 'hold')
        
        # Сигнал на покупку (oversold)
        if rsi < self.rsi_oversold:
            if last_action != 'buy':
                self.last_signal[instrument_uid] = 'buy'
                return Signal(
                    action='buy',
                    instrument_uid=instrument_uid,
                    quantity=self.order_quantity,
                    price=price,
                    reason=f"RSI={rsi:.1f} ниже {self.rsi_oversold} (перепроданность)"
                )
            else:
                return Signal(
                    'hold', instrument_uid, 0,
                    reason=f"Уже есть активный сигнал BUY, RSI={rsi:.1f}"
                )
        
        # Сигнал на продажу (overbought)
        elif rsi > self.rsi_overbought:
            if last_action != 'sell':
                self.last_signal[instrument_uid] = 'sell'
                return Signal(
                    action='sell',
                    instrument_uid=instrument_uid,
                    quantity=self.order_quantity,
                    price=price,
                    reason=f"RSI={rsi:.1f} выше {self.rsi_overbought} (перекупленность)"
                )
            else:
                return Signal(
                    'hold', instrument_uid, 0,
                    reason=f"Уже есть активный сигнал SELL, RSI={rsi:.1f}"
                )
        
        # Нет сигнала
        else:
            self.last_signal[instrument_uid] = 'hold'
            return Signal(
                'hold', instrument_uid, 0,
                reason=f"RSI={rsi:.1f} в нейтральной зоне ({self.rsi_oversold}-{self.rsi_overbought})"
            )
    
    def get_status(self, instrument_uid: str) -> Dict[str, Any]:
        """Получить статус стратегии для инструмента"""
        prices = self.price_history.get(instrument_uid, [])
        return {
            'instrument_uid': instrument_uid,
            'history_length': len(prices),
            'rsi_period': self.rsi_period,
            'last_signal': self.last_signal.get(instrument_uid, 'hold'),
        }
    
    def visualize_decision(self, instrument_uid: str, prices: List[float], rsi: float, signal: Signal):
        """Визуализация принятого решения"""
        try:
            from datetime import datetime, timedelta
            
            # Создаём даты
            dates = [datetime.now() - timedelta(days=len(prices)-i) for i in range(len(prices))]
            
            # Рассчитываем историю RSI
            rsi_history = []
            for i in range(len(prices)):
                if i >= self.rsi_period:
                    hist_rsi = self.calculate_rsi(prices[:i+1], self.rsi_period)
                    rsi_history.append(hist_rsi)
                else:
                    rsi_history.append(50)
            
            plot_rsi_decision(
                instrument_uid=instrument_uid,
                dates=dates,
                prices=prices,
                rsi_values=rsi_history,
                current_rsi=rsi,
                current_price=prices[-1],
                signal=signal.action,
                reason=signal.reason,
                oversold=self.rsi_oversold,
                overbought=self.rsi_overbought
            )
        except Exception as e:
            print(f"Ошибка визуализации: {e}")