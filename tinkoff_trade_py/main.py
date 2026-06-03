import os
import yaml
from datetime import timedelta
from dotenv import load_dotenv

from t_tech.invest import CandleInterval, Client
from t_tech.invest.schemas import CandleSource
from t_tech.invest.utils import now

from utils.config_loader import load_full_config


def main():
    load_dotenv()
    full_config = load_full_config()
    
    with Client(full_config['token_sandbox']) as client:
        for candle in client.get_all_candles(
            instrument_id="T_TQBR",
            from_=now() - timedelta(days=365),
            interval=CandleInterval.CANDLE_INTERVAL_HOUR,
            candle_source_type=CandleSource.CANDLE_SOURCE_UNSPECIFIED,
        ):
            print(candle)

    return 0


if __name__ == "__main__":
    main()
