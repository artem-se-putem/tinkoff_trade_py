import os
import yaml
from datetime import timedelta
from dotenv import load_dotenv


from t_tech.invest import CandleInterval, Client
from t_tech.invest.schemas import CandleSource
from t_tech.invest.utils import now


def main():
    load_dotenv()
    env_dct = {
        'token_prod': os.getenv("TINKOFF_TOKEN"),
        'token_sandbox': os.getenv("TINKOFF_TOKEN_SANDBOX"),
        'sandbox_flag': os.getenv("TINKOFF_SANDBOX_FLAG"),
        'config_path': os.getenv("CONFIG_PATH")
    }

    if not env_dct['token_sandbox']:
        return 'Проверь token_sandbox в .env'
    
    if not env_dct['config_path']:
        return 'Проверь config_path в .env'
    

    with open(env_dct['config_path'], 'r', encoding='utf-8') as f:
        raw_config = yaml.safe_load(f)
    
    with Client(env_dct['token_sandbox']) as client:
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
