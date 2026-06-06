from typing import Dict, Any, Optional
import psycopg2
import polars as pl
from psycopg2.extensions import connection as PsycopgConnection
from utils import logger


class PostgresClient:
    """
    Клиент для работы с PostgreSQL.
    
    Пример использования:
        
        # Или через глобальный конфиг
        client = PostgresClient.from_app_config(app.config)
        
        # Проверка подключения
        if client.check_connection():
            df = client.read_table("candles")
    """
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        Инициализация клиента.
        
        Args:
            db_config: Словарь с параметрами подключения.
                Обязательные ключи: host, port, database, user, password
        """
        self._config = db_config
        self._connection: Optional[PsycopgConnection] = None
        
    @property # дает синглтон, кэширует после первого обращения (выполняется только один раз)
    def connection(self) -> PsycopgConnection:
        """
        Ленивое создание подключения.
        Подключение создаётся только при первом обращении.
        """
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(**self._config)
        return self._connection
    
    def close(self) -> None:
        """Закрывает подключение к БД."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None
    
    def check_connection(self) -> bool:
        """
        Проверяет подключение к PostgreSQL.
        
        Returns:
            True если подключение успешно, иначе False
        """
        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
                logger.info("Успешное подключение к PostgreSQL")
            return True
        except Exception as e:
            logger.info(f"Ошибка подключения к PostgreSQL: {e}")
            return False
    
    def load_dataframe(self, table_name: str, limit: Optional[int] = None) -> pl.DataFrame:
        """
        Загружает таблицу в Polars DataFrame.
        
        Args:
            table_name: Имя таблицы
            limit: Ограничение количества строк (опционально)
        
        Returns:
            Polars DataFrame с данными
        """
        query = f"SELECT * FROM {table_name}"
        if limit:
            query = f"{query} LIMIT {limit}"
        
        return pl.read_database(query, self.connection)
    
    def read_table(self, table_name: str, limit: Optional[int] = None) -> pl.DataFrame:
        """
        Читает таблицу и возвращает Polars DataFrame (алиас для load_dataframe).
        
        Args:
            table_name: Имя таблицы
            limit: Ограничение количества строк
        
        Returns:
            Polars DataFrame с данными
        """
        return self.load_dataframe(table_name, limit)
    
    def execute_query(self, query: str, params: Optional[tuple | list] = None) -> Optional[list]:
        """
        Выполняет произвольный SQL запрос.
        
        Args:
            query: SQL запрос
            params: Параметры для безопасной подстановки
        
        Returns:
            Список кортежей для SELECT, None для INSERT/UPDATE/DELETE
        """
        with self.connection.cursor() as cur:
            cur.execute(query, params)
            if cur.description:  # Если есть результат (SELECT)
                return cur.fetchall()
            self.connection.commit()
            return None
        
    # ========== ВСТАВКА СВЕЧИ ==========
    
    def insert_candle(self, candle, instrument_uid: str = "T_TQBR", timeframe: str = "1hour"):
        """
        Вставка одной свечи в таблицу candles
        
        Args:
            candle: объект HistoricCandle из Tinkoff API
            instrument_uid: UID инструмента
            timeframe: интервал свечи (1min, 5min, hour, day)
        """
        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO candles (
                        instrument_uid, candle_time, 
                        open_price, close_price, high_price, low_price,
                        volume, timeframe, is_complete
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (instrument_uid, candle_time, timeframe) 
                    DO UPDATE SET
                        open_price = EXCLUDED.open_price,
                        close_price = EXCLUDED.close_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        volume = EXCLUDED.volume,
                        is_complete = EXCLUDED.is_complete
                """, (
                    instrument_uid,
                    candle.time,
                    float(candle.open.units + candle.open.nano / 1e9),
                    float(candle.close.units + candle.close.nano / 1e9),
                    float(candle.high.units + candle.high.nano / 1e9),
                    float(candle.low.units + candle.low.nano / 1e9),
                    candle.volume,
                    timeframe,
                    candle.is_complete
                ))
                self.connection.commit()
                logger.debug(f"📊 Свеча вставлена: {instrument_uid} {candle.time}")
                
        except Exception as e:
            self.connection.rollback()
            logger.error(f"❌ Ошибка вставки свечи: {e}")
            raise
    
    def insert_candles_batch(self, candles: list, instrument_uid: str = "T_TQBR", timeframe: str = "1hour"):
        """
        Массовая вставка через обычный execute (медленнее, но проще)
        """
        if not candles:
            return
        
        inserted = 0
        failed = 0
        
        for candle in candles:
            try:
                open_price = candle.open.units + candle.open.nano / 1e9
                close_price = candle.close.units + candle.close.nano / 1e9
                high_price = candle.high.units + candle.high.nano / 1e9
                low_price = candle.low.units + candle.low.nano / 1e9
                
                query = """
                    INSERT INTO candles (
                        instrument_uid, candle_time, 
                        open_price, close_price, high_price, low_price,
                        volume, timeframe, is_complete
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (instrument_uid, candle_time, timeframe) 
                    DO UPDATE SET
                        open_price = EXCLUDED.open_price,
                        close_price = EXCLUDED.close_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        volume = EXCLUDED.volume,
                        is_complete = EXCLUDED.is_complete
                """
                
                params = (
                    instrument_uid,
                    candle.time,
                    open_price,
                    close_price,
                    high_price,
                    low_price,
                    candle.volume,
                    timeframe,
                    candle.is_complete
                )
                
                self.execute_query(query, params)
                inserted += 1
                
            except Exception as e:
                failed += 1
                logger.error(f"Ошибка вставки свечи {candle.time}: {e}")
        
        self.connection.commit()
        logger.info(f"Вставлено: {inserted}, ошибок: {failed}")     
    
    def __enter__(self):
        """Поддержка контекстного менеджера."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие при выходе из контекста."""
        self.close()