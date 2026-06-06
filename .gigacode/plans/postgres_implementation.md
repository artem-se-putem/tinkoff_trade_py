# План реализации postgres.py

## Цель
Создать файл `c:\deals\tinkoff_trade_py\tinkoff_trade_py\db\postgres.py` с функциями для работы с PostgreSQL.

## Требования
1. Подключение к PostgreSQL (использовать psycopg2)
2. Функция проверки подключения
3. Функция загрузки датафрейма polars из PostgreSQL таблицы
4. Функция чтения таблицы в виде Polars DataFrame

## Параметры подключения
- host: localhost
- port: 5432
- database: tinkoff_trade
- user: postgres
- password: postgres

## Структура файла
- `connect()`: создание соединения
- `check_connection()`: проверка подключения
- `load_dataframe(table_name)`: загрузка таблицы в Polars DataFrame
- `read_table(table_name)`: чтение таблицы

## Шаги реализации
1. Создать файл postgres.py
2. Добавить конфигурацию подключения
3. Реализовать функцию connect()
4. Реализовать функцию check_connection()
5. Реализовать функцию load_dataframe()
6. Реализовать функцию read_table()
