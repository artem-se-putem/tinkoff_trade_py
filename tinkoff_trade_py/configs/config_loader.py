# config/config.py
import os
import yaml
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path
from utils import logger

PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class EnvConfig:
    token_prod: str
    token_sandbox: str
    sandbox_flag: bool
    config_path: str
    
    @classmethod
    def load(cls) -> 'EnvConfig':
        token_prod = os.getenv("TINKOFF_TOKEN", "")
        token_sandbox = os.getenv("TINKOFF_TOKEN_SANDBOX", "")
        sandbox_flag = os.getenv("TINKOFF_SANDBOX_FLAG", "False").lower() == "true"
        config_path = os.getenv("CONFIG_PATH", "")
        
        if not token_sandbox:
            raise ValueError("TINKOFF_TOKEN_SANDBOX не найден")
        if not config_path:
            raise ValueError("CONFIG_PATH не найден")
        
        config_file = Path(config_path)
        if not config_file.exists():
            config_file = PROJECT_ROOT / config_path
            if not config_file.exists():
                raise FileNotFoundError(f"Файл конфига не найден: {config_path}")
            config_path = str(config_file)        
        
        return cls(
            token_prod=token_prod,
            token_sandbox=token_sandbox,
            sandbox_flag=sandbox_flag,
            config_path=config_path
        )


@dataclass
class FullConfig:
    """Полная конфигурация приложения (объединяет EnvConfig и YAML)"""
    # Из EnvConfig
    token_prod: str
    token_sandbox: str
    sandbox_flag: bool
    config_path: str
    
    # Из YAML (типизированные поля под ваш config.yaml)
    # Базы данных
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    postgres_config: Optional[Dict[str, Any]] = field(default_factory=dict)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_database: str = "tinkoff_trade"
    
    # Стратегия RSI
    strategy_name: str = "rsi_strategy"
    rsi_period: int = 14
    rsi_oversold: int = 30
    rsi_overbought: int = 70
    order_quantity: int = 1
    stop_loss_percent: float = 2.0
    take_profit_percent: float = 4.0
    
    # Инструменты для торговли
    instruments: List[str] = field(default_factory=list)
    
    # Общие настройки
    log_level: str = "INFO"
    timeframe: str = '1 sec'
    
    @classmethod
    def load(cls) -> 'FullConfig':
        """Загрузить полный конфиг из .env и YAML"""
        # 1. Загружаем переменные окружения
        env_config = EnvConfig.load()
        
        # 2. Загружаем YAML файл
        with open(env_config.config_path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f) or {}
            logger.info(yaml_data)
        
        # 3. Создаём датакласс, объединяя env + yaml
        cls.postgres_config = yaml_data.get('postgres')
        if cls.postgres_config is None:
            cls.postgres_config = {}
        return cls(
            # Из EnvConfig (обязательные)
            token_prod=env_config.token_prod,
            token_sandbox=env_config.token_sandbox,
            sandbox_flag=env_config.sandbox_flag,
            config_path=env_config.config_path,
            
            # Из YAML (с значениями по умолчанию)
            redis_host=yaml_data.get('redis_host', 'localhost'),
            redis_port=yaml_data.get('redis_port', 6379),
            # redis_db=yaml_data.get('redis_db', 0),
            postgres_host=cls.postgres_config.get('host', 'localhost'),
            postgres_port=cls.postgres_config.get('port', 5432),
            postgres_user=cls.postgres_config.get('user', 'postgres'),
            postgres_password=cls.postgres_config.get('password', 'postgres'),
            postgres_database=cls.postgres_config.get('database', 'tinkoff_trade'),
            # strategy_name=yaml_data.get('strategy_name', 'rsi_strategy'),
            # rsi_period=yaml_data.get('rsi_period', 14),
            # rsi_oversold=yaml_data.get('rsi_oversold', 30),
            # rsi_overbought=yaml_data.get('rsi_overbought', 70),
            # order_quantity=yaml_data.get('order_quantity', 1),
            # stop_loss_percent=yaml_data.get('stop_loss_percent', 2.0),
            # take_profit_percent=yaml_data.get('take_profit_percent', 4.0),
            # instruments=yaml_data.get('instruments', []),
            log_level=yaml_data.get('log_level', 'INFO'),
            timeframe=yaml_data.get('timeframe', 60),
        )


# ========== ИСПОЛЬЗОВАНИЕ ==========
if __name__ == '__main__':
    config = FullConfig.load()
    logger.info(f"Token sandbox: {config.token_sandbox[:10]}...")
    logger.info(f"RSI период: {config.rsi_period}")
    logger.info(f"Инструменты: {config.instruments}")
    logger.info(f"Redis: {config.redis_host}:{config.redis_port}")