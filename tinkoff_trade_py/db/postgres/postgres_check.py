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
    logger.info('result test_query:', cur.fetchone())
    logger.info(True)