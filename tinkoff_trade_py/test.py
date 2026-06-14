"""Разовый запуск: загрузка → RSI → график → решение (без цикла)."""
from datetime import timedelta
from dotenv import load_dotenv

from t_tech.invest import CandleInterval, Client
from t_tech.invest.schemas import CandleSource
from t_tech.invest.utils import now

from configs import FullConfig
from db import PostgresClient
from utils import logger

from data import fetch_candles, get_candles_df
from analysis import calculate_rsi, generate_signal, get_recommendation, interactive_decision
from visualization import plot_candles


def main():
    logger.info("starting test.py")
    load_dotenv()
    full_config = FullConfig.load()

    # Загрузка свечей
    fetch_candles(
        token=full_config.token_sandbox,
        postgres_config=full_config.postgres_config,
        instrument_uid=full_config.instrument_uid,
        timeframe=full_config.timeframe,
        days=full_config.retention_days,
    )

    df_candles = get_candles_df(full_config.postgres_config)

    # Вычисляем RSI и добавляем как колонку
    rsi_series = calculate_rsi(df_candles, period=full_config.rsi_period)
    df_candles = df_candles.with_columns(rsi_series.alias("rsi"))

    # Генерируем сигналы BUY/SELL
    df_candles = generate_signal(df_candles, low=full_config.rsi_oversold, high=full_config.rsi_overbought)

    # Рисуем график с RSI и сигналами
    plot_candles(df_candles, instrument_uid=full_config.instrument_uid, limit=full_config.chart_limit)

    # Интерактивный блок
    recommendation = get_recommendation(df_candles, instrument_uid=full_config.instrument_uid)
    interactive_decision(recommendation)

    return 0


if __name__ == "__main__":
    main()