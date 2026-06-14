"""Точка входа: часовой цикл загрузки → анализа → графика → решения."""
import time
from datetime import timedelta, datetime
from dotenv import load_dotenv
import matplotlib.pyplot as plt

from configs import FullConfig
from data import fetch_candles, cleanup_old_candles, get_candles_df
from analysis import calculate_rsi, generate_signal, get_recommendation, interactive_decision
from visualization import plot_candles
from utils import logger


def main():
    logger.info("starting main.py")
    load_dotenv()
    full_config = FullConfig.load()

    while True:
        try:
            run_cycle(full_config)
        except Exception as e:
            logger.error(f"❌ Ошибка в цикле: {e}")

        # Ожидание до следующего часа
        wait_seconds = seconds_until_next_hour()
        logger.info(f"⏳ Следующее обновление через {wait_seconds // 60} мин")
        time.sleep(wait_seconds)


def run_cycle(config):
    """Один цикл: загрузка → очистка → RSI/сигналы → график → решение."""
    logger.info("🔄 Начало цикла обновления")

    # 1. Загрузка часовых свечей
    fetch_candles(
        token=config.token_sandbox,
        postgres_config=config.postgres_config,
        instrument_uid=config.instrument_uid,
        timeframe=config.timeframe,
        days=config.retention_days,
    )

    # 2. Очистка старых данных из БД
    cleanup_old_candles(
        postgres_config=config.postgres_config,
        instrument_uid=config.instrument_uid,
        timeframe=config.timeframe,
        days=config.retention_days,
    )

    # 3. Чтение актуальных данных из БД
    df_candles = get_candles_df(config.postgres_config)

    if df_candles.is_empty():
        logger.warning("⚠️ Нет данных в БД, пропускаем цикл")
        return

    # 4. Вычисляем RSI и сигналы
    rsi_series = calculate_rsi(df_candles, period=config.rsi_period)
    df_candles = df_candles.with_columns(rsi_series.alias("rsi"))
    df_candles = generate_signal(df_candles, low=config.rsi_oversold, high=config.rsi_overbought)

    # 5. Закрываем старый график и строим новый
    plt.close('all')
    plot_candles(df_candles, instrument_uid=config.instrument_uid, limit=config.chart_limit)

    # 6. Интерактивный блок: сигнал и выбор действия
    recommendation = get_recommendation(df_candles, instrument_uid=config.instrument_uid)
    interactive_decision(recommendation)

    logger.info("✅ Цикл завершён")


def seconds_until_next_hour() -> int:
    """Вычисляет количество секунд до начала следующего часа."""
    now_dt = datetime.now()
    next_hour = now_dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    return max(1, int((next_hour - now_dt).total_seconds()))


if __name__ == "__main__":
    main()