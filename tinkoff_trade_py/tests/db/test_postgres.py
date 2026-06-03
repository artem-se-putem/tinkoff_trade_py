# tests/db/test_postgres.py

import pytest
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock
import polars as pl
import psycopg2

# Добавляем корень проекта в путь (как в test_minimal_fixed.py)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from db import PostgresClient


# ========== Фикстуры ==========

@pytest.fixture
def db_config():
    """Базовая конфигурация БД."""
    return {
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "user": "test_user",
        "password": "test_pass"
    }


# ========== Тесты ==========

def test_init_with_config(db_config):
    """Создание клиента с конфигом."""
    client = PostgresClient(db_config)
    assert client._config == db_config
    assert client._connection is None


def test_from_app_config():
    """Создание клиента из глобального конфига."""
    app_config = {
        "database": {
            "host": "testhost",
            "port": 5433,
            "database": "app_db",
            "user": "app_user",
            "password": "app_pass"
        }
    }
    client = PostgresClient.from_app_config(app_config)
    
    assert client._config["host"] == "testhost"
    assert client._config["port"] == 5433
    assert client._config["database"] == "app_db"


def test_from_app_config_with_defaults():
    """Пустой конфиг - подставляются дефолты."""
    client = PostgresClient.from_app_config({})
    
    assert client._config["host"] == "localhost"
    assert client._config["database"] == "tinkoff_trade"


@patch('psycopg2.connect')
def test_connection_creates_once(mock_connect, db_config):
    """Подключение создаётся только один раз (лениво)."""
    mock_conn = MagicMock()
    mock_conn.closed = 0
    mock_connect.return_value = mock_conn
    
    client = PostgresClient(db_config)
    
    # Первое обращение - создаёт
    conn1 = client.connection
    assert mock_connect.call_count == 1
    
    # Второе обращение - берёт из кэша
    conn2 = client.connection
    assert mock_connect.call_count == 1
    assert conn1 is conn2


def test_close_connection(db_config):
    """Закрытие соединения."""
    client = PostgresClient(db_config)
    
    mock_conn = MagicMock()
    mock_conn.closed = 0
    client._connection = mock_conn
    
    client.close()
    
    mock_conn.close.assert_called_once()
    assert client._connection is None


@patch('psycopg2.connect')
def test_check_connection_success(mock_connect, db_config):
    """Успешная проверка подключения."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    
    client = PostgresClient(db_config)
    result = client.check_connection()
    
    assert result is True
    mock_cursor.execute.assert_called_with("SELECT 1")
    mock_cursor.fetchone.assert_called_once()


@patch('psycopg2.connect')
def test_check_connection_failure(mock_connect, db_config):
    """Ошибка при проверке подключения."""
    mock_connect.side_effect = psycopg2.OperationalError("Connection failed")
    
    client = PostgresClient(db_config)
    result = client.check_connection()
    
    assert result is False


@patch('polars.read_database')
@patch('psycopg2.connect')
def test_load_dataframe(mock_connect, mock_read_db, db_config):
    """Загрузка таблицы в DataFrame."""
    expected_df = pl.DataFrame({"id": [1, 2], "price": [100, 200]})
    mock_read_db.return_value = expected_df
    
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    
    client = PostgresClient(db_config)
    result = client.load_dataframe("candles")
    
    mock_read_db.assert_called_once()
    assert result.equals(expected_df)


@patch('polars.read_database')
@patch('psycopg2.connect')
def test_load_dataframe_with_limit(mock_connect, mock_read_db, db_config):
    """Загрузка таблицы с лимитом."""
    expected_df = pl.DataFrame({"id": [1]})
    mock_read_db.return_value = expected_df
    
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    
    client = PostgresClient(db_config)
    result = client.load_dataframe("candles", limit=1)
    
    mock_read_db.assert_called_once()
    assert "LIMIT 1" in mock_read_db.call_args[0][0]


@patch('psycopg2.connect')
def test_execute_query_select(mock_connect, db_config):
    """Выполнение SELECT запроса."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = [("id",)]
    mock_cursor.fetchall.return_value = [(1,), (2,)]
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    
    client = PostgresClient(db_config)
    result = client.execute_query("SELECT * FROM users")
    
    mock_cursor.execute.assert_called_with("SELECT * FROM users", None)
    assert result == [(1,), (2,)]


@patch('psycopg2.connect')
def test_execute_query_insert(mock_connect, db_config):
    """Выполнение INSERT запроса."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.description = None
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    
    client = PostgresClient(db_config)
    result = client.execute_query(
        "INSERT INTO users VALUES (%s, %s)",
        params=(1, "john")
    )
    
    mock_cursor.execute.assert_called_with(
        "INSERT INTO users VALUES (%s, %s)",
        (1, "john")
    )
    mock_conn.commit.assert_called_once()
    assert result is None


@patch('psycopg2.connect')
def test_context_manager_auto_close(mock_connect, db_config):
    """Автоматическое закрытие при выходе из with."""
    mock_conn = MagicMock()
    mock_conn.closed = 0
    mock_connect.return_value = mock_conn
    
    with PostgresClient(db_config) as client:
        _ = client.connection
        assert client._connection is not None
    
    mock_conn.close.assert_called_once()


@patch('psycopg2.connect')
def test_context_manager_on_exception(mock_connect, db_config):
    """При ошибке соединение всё равно закрывается."""
    mock_conn = MagicMock()
    mock_conn.closed = 0
    mock_connect.return_value = mock_conn
    
    with pytest.raises(ValueError):
        with PostgresClient(db_config) as client:
            _ = client.connection
            raise ValueError("Test error")
    
    mock_conn.close.assert_called_once()


def test_context_manager_returns_self(db_config):
    """__enter__ возвращает self."""
    client = PostgresClient(db_config)
    with client as c:
        assert c is client


if __name__ == "__main__":
    pytest.main([__file__, "-v"])