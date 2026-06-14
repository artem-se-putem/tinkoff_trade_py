"""Загрузка свечей из API, очистка старых данных, чтение из БД."""
from datetime import timedelta
import polars as pl

from t_tech.invest import CandleInterval, Client
from t_tech.invest.schemas import CandleSource
from t_tech.invest.utils import now

from db import PostgresClient
from utils import logger


def fetch_candles(token: str, postgres_config: dict,
                  instrument_uid: str = "T_TQBR",
                  timeframe: str = "1hour",
                  days: int = 60):
    """Загрузка свечей из API T-Invest за последние N дней и запись в БД."""
    logger.info(f"📥 Загрузка свечей {instrument_uid} за {days} дней ({timeframe})")
    with Client(token) as client:
        lst_candles = []
        with PostgresClient(postgres_config) as postgres_client:
            for candle in client.get_all_candles(
                instrument_id=instrument_uid,
                from_=now() - timedelta(days=days),
                interval=CandleInterval.CANDLE_INTERVAL_HOUR,
                candle_source_type=CandleSource.CANDLE_SOURCE_UNSPECIFIED,
            ):
                lst_candles.append(candle)
            logger.info(f"📥 Получено свечей: {len(lst_candles)}")
            postgres_client.insert_candles_batch(
                lst_candles, instrument_uid=instrument_uid, timeframe=timeframe
            )


def cleanup_old_candles(postgres_config: dict,
                        instrument_uid: str = "T_TQBR",
                        timeframe: str = "1hour",
                        days: int = 60):
    """Удаляет из БД свечи старше N дней для инструмента и таймфрейма."""
    cutoff = now() - timedelta(days=days)
    logger.info(f"🗑️ Удаление свечей старше {cutoff} ({instrument_uid}, {timeframe})")
    with PostgresClient(postgres_config) as postgres_client:
        postgres_client.execute_query(
            """
            DELETE FROM candles
            WHERE instrument_uid = %s
              AND timeframe = %s
              AND candle_time < %s
            """,
            (instrument_uid, timeframe, cutoff)
        )
        postgres_client.connection.commit()
    logger.info("🗑️ Очистка завершена")


def get_candles_df(postgres_config: dict) -> pl.DataFrame:
    """Получает свечи из БД и возвращает их в виде Polars DataFrame."""
    with PostgresClient(postgres_config) as postgres_client:
        df_candles = postgres_client.read_table("candles")
    return df_candles