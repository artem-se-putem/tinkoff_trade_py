import sys
from pathlib import Path

# Добавляем корневую папку проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import psycopg2
from utils import logger

default_config = {
    "host": "localhost",
    "port": 5432,
    "database": "tinkoff_trade",
    "user": "postgres",
    "password": "postgres"
}

connection = psycopg2.connect(**default_config)
with connection.cursor() as cur:
    cur.execute("SELECT 1")
    result = cur.fetchone()
    logger.info('result test_query: %s', result)
    logger.info(True)