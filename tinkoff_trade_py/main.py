import os
import yaml
from datetime import timedelta
from dotenv import load_dotenv

from t_tech.invest import CandleInterval, Client
from t_tech.invest.schemas import CandleSource
from t_tech.invest.utils import now

from configs import FullConfig, EnvConfig
from db import PostgresClient, RedisClient
from utils import logger


def main():
    logger.info("starting main.py")
    load_dotenv()
    full_config = FullConfig.load()
    postgres_client = PostgresClient(full_config)
    postgres_client.check_connection()
    
    # with Client(full_config.token_sandbox) as client:
    #     for candle in client.get_all_candles(
    #         instrument_id="T_TQBR",
    #         from_=now() - timedelta(days=365),
    #         interval=CandleInterval.CANDLE_INTERVAL_HOUR,
    #         candle_source_type=CandleSource.CANDLE_SOURCE_UNSPECIFIED,
    #     ):
    #         logger.info(candle)

    return 0


if __name__ == "__main__":
    main()
