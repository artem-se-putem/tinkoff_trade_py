import os
import yaml

from dataclasses import dataclass
from typing import Optional

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
        
        return cls(
            token_prod=token_prod,
            token_sandbox=token_sandbox,
            sandbox_flag=sandbox_flag,
            config_path=config_path
        )

def load_full_config():
    env_config = EnvConfig.load()

    with open(env_config.config_path, 'r', encoding='utf-8') as f:
        full_config = yaml.safe_load(f)

    return full_config