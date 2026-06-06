# План исправления тестов для PostgresClient

## Проблемы

### 1. Метод `get_connection` не существует
- **Описание**: Тесты используют `client.get_connection`, но в классе `PostgresClient` есть свойство `connection`, а не метод `get_connection`.
- **Файлы**: `tests/db/test_postgres.py`
- **Тесты, которые падают**: 
  - `test_get_connection_creates_once`
  - `test_load_dataframe`
  - `test_load_dataframe_with_limit`
  - `test_read_table_alias`

### 2. Тесты контекстного менеджера не проходят
- **Описание**: Тесты `test_context_manager_auto_close` и `test_context_manager_on_exception` не проходят, потому что `mock_conn.close.assert_called_once()` не вызывается.
- **Причина**: В тестах используется `client.connection` (свойство), но в реализации `__exit__` вызывается `self.close()`, который проверяет `self._connection and not self._connection.closed`. Проблема в том, что `MagicMock.closed` по умолчанию равен 0 (False), но поведение может отличаться.

## Решения

### Исправление тестов

1. **Заменить `client.get_connection` на `client.connection`** во всех тестах, где используется это свойство.

2. **В тестах контекстного менеджера**:
   - Убедиться, что `mock_conn.closed` установлен в 0 (False) для корректной работы проверки в `close()`
   - Или изменить логику проверки в тестах, чтобы учитывать особенности `MagicMock`

## Требуемые изменения

### Файл: `tests/db/test_postgres.py`

1. В `test_get_connection_creates_once`:
   - Заменить `client.get_connection` на `client.connection`

2. В `test_load_dataframe`:
   - Заменить `client.get_connection` на `client.connection`

3. В `test_load_dataframe_with_limit`:
   - Заменить `client.get_connection` на `client.connection`

4. В `test_read_table_alias`:
   - Заменить `client.get_connection` на `client.connection`

5. В `test_context_manager_auto_close`:
   - Установить `mock_conn.closed = 0` перед использованием
   - Или изменить проверку на `mock_conn.close.called` вместо `assert_called_once()`

6. В `test_context_manager_on_exception`:
   - Установить `mock_conn.closed = 0` перед использованием
   - Или изменить проверку на `mock_conn.close.called` вместо `assert_called_once()`

## Проверка

После внесения изменений запустить тесты командой:
```bash
python -m pytest tests/db/test_postgres.py -v
```

Ожидаемый результат: все 16 тестов должны пройти успешно.
