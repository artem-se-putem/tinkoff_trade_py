import sys
from pathlib import Path

# Добавляем корневую папку проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import redis
from utils import logger

# Подключение к Redis в Docker
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

# Проверка
logger.info(r.ping())  # True, если всё работает
