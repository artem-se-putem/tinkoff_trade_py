import os
import yaml

from dataclasses import dataclass
from typing import Optional
from pathlib import Path

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
            # Пробуем относительно корня проекта
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

def load_full_config():
    # TODO: поменять конфиг на класс
    env_config = EnvConfig.load()

    with open(env_config.config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    full_config = config | env_config.__dict__

    return full_config