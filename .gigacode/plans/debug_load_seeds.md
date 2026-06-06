# План отладки load_seeds.py

## Проблема
Скрипт `tinkoff_trade_py/utils/load_seeds.py` не может загрузить CSV файлы из папки seeds.

## Причина
CSV файлы в подпапках seeds не содержат заголовков (header row). Данные идут в следующем порядке:
1. `instrument_uid` - идентификатор инструмента
2. `candle_time` - дата и время начала свечи в UTC
3. `open_price` - цена открытия
4. `close_price` - цена закрытия
5. `high_price` - максимальная цена
6. `low_price` - минимальная цена
7. `volume` - объем в лотах

Текущий код использует `pl.read_csv()` без параметра `has_header=False`, поэтому Polars интерпретирует первую строку данных как заголовки.

## Решение
1. Изменить `load_all_csv_to_df()` чтобы добавить `has_header=False` в `pl.read_csv()`
2. После чтения CSV добавить имена колонок: ['instrument_uid', 'candle_time', 'open_price', 'close_price', 'high_price', 'low_price', 'volume']
3. Преобразовать типы данных при необходимости (candle_time в datetime, volume в int) - это делать не надо

## Изменяемый файл
- `tinkoff_trade_py/utils/load_seeds.py`
