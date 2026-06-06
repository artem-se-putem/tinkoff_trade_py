# test.py
import os
from datetime import timedelta
from dotenv import load_dotenv

from t_tech.invest import CandleInterval, Client
from t_tech.invest.schemas import CandleSource
from t_tech.invest.utils import now

from configs import FullConfig
from strategies.rsi_strategy import RSIStrategy
from utils import logger
from visualization import plot_console_chart, show_decision  # <- добавили импорт


def quotation_to_float(quotation) -> float:
    return quotation.units + quotation.nano / 1e9


def main():
    logger.info("🚀 Запуск торгового бота с RSI стратегией")
    load_dotenv()
    full_config = FullConfig.load()
    
    strategy_config = {
        'rsi_period': full_config.rsi_period,
        'rsi_oversold': full_config.rsi_oversold,
        'rsi_overbought': full_config.rsi_overbought,
        'order_quantity': full_config.order_quantity,
    }
    strategy = RSIStrategy(strategy_config)
    
    with Client(full_config.token_sandbox) as client:
        for instrument_uid in full_config.instruments:
            logger.info(f"📊 Анализ инструмента: {instrument_uid}")
            
            candles = []
            try:
                for candle in client.get_all_candles(
                    instrument_id=instrument_uid,
                    from_=now() - timedelta(days=60),
                    interval=CandleInterval.CANDLE_INTERVAL_DAY,
                    candle_source_type=CandleSource.CANDLE_SOURCE_UNSPECIFIED,
                ):
                    candles.append(candle)
            except Exception as e:
                logger.error(f"Ошибка получения свечей: {e}")
                continue
            
            if len(candles) < strategy.rsi_period + 1:
                logger.warning(f"  Недостаточно данных: {len(candles)}/{strategy.rsi_period + 1}")
                continue
            
            prices = [quotation_to_float(c.close) for c in candles]
            current_price = prices[-1]
            
            signal = strategy.analyze(
                instrument_uid=instrument_uid,
                data={
                    'current_price': current_price,
                    'prices': prices,
                }
            )
            
            # Получаем RSI для отображения
            rsi = strategy.calculate_rsi(prices, strategy.rsi_period)
            
            # ВИЗУАЛИЗАЦИЯ
            plot_console_chart(prices[-30:], rsi, width=50)
            show_decision(
                instrument_uid=instrument_uid,
                current_price=current_price,
                rsi=rsi,
                signal=signal.action,
                reason=signal.reason,
                oversold=full_config.rsi_oversold,
                overbought=full_config.rsi_overbought
            )
            
            # Логирование результата
            if signal.action == 'buy':
                logger.info(f"🟢 СИГНАЛ ПОКУПКИ: {signal.reason}")
            elif signal.action == 'sell':
                logger.info(f"🔴 СИГНАЛ ПРОДАЖИ: {signal.reason}")
            else:
                logger.info(f"⚪ {signal.reason}")
    
    logger.info("✅ Бот завершил работу")


if __name__ == "__main__":
    main()