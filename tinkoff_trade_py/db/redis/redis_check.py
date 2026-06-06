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