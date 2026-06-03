from typing import Dict, Any, Optional
import psycopg2
import polars as pl
from psycopg2.extensions import connection as PsycopgConnection


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
    
    @classmethod
    def from_app_config(cls, app_config: Dict[str, Any]) -> 'PostgresClient':
        """
        Создает клиент из глобального конфига приложения.
        
        Args:
            app_config: Глобальный конфиг приложения, где есть секция 'database'
        """
        db_config = app_config.get('database', {})
        # Заполняем значениями по умолчанию, если чего-то нет
        default_config = {
            "host": "localhost",
            "port": 5432,
            "database": "tinkoff_trade",
            "user": "postgres",
            "password": "postgres"
        }
        # Объединяем: значения из app_config перезаписывают default
        final_config = {**default_config, **db_config}
        return cls(final_config)
    
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
            return True
        except Exception as e:
            print(f"Ошибка подключения к PostgreSQL: {e}")
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
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[list]:
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
    
    def __enter__(self):
        """Поддержка контекстного менеджера."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое закрытие при выходе из контекста."""
        self.close()