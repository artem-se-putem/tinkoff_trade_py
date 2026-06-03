import polars as pl
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values

# ============================================
# КОНФИГУРАЦИЯ
# ============================================

timeframe = "1min"
seeds_folder = Path(__file__).parent.parent / "seeds" / f"{timeframe}"

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "tinkoff_trade",
    "user": "postgres",
    "password": "postgres"
}

# ============================================
# ФУНКЦИИ
# ============================================

def load_all_csv_to_df(folder: Path) -> pl.DataFrame:
    """
    Загружает все CSV из всех подпапок в один Polars DataFrame (все цены -> float)
    """
    csv_files = list(folder.rglob("*.csv"))
    
    if not csv_files:
        raise FileNotFoundError(f"CSV файлы не найдены в {folder}")
    
    print(f"📁 Найдено CSV файлов: {len(csv_files)}")
    
    dfs = []
    failed_files = []
    
    for csv_file in csv_files:
        df = None
        
        # Пробуем разные разделители
        for sep in [';', ',']:
            try:
                # Читаем CSV с принудительными типами float для цен
                df = pl.read_csv(
                    csv_file,
                    separator=sep,
                    encoding='utf8',
                    has_header=False,
                    new_columns=['instrument_uid', 'candle_time', 'open_price', 
                            'close_price', 'high_price', 'low_price', 'volume'],
                    schema_overrides={
                        'open_price': pl.Float64,
                        'close_price': pl.Float64,
                        'high_price': pl.Float64,
                        'low_price': pl.Float64,
                        'volume': pl.Int64,
                    },
                    null_values=['NA', 'N/A', 'null', 'NULL', '', 'NaN'],
                    try_parse_dates=False
                )
                break
            except Exception as e:
                continue
        
        if df is None:
            failed_files.append(csv_file.name)
            print(f"    ⚠️ Пропущен: {csv_file.name}")
            continue
        
        # Добавляем имя файла
        df = df.with_columns(pl.lit(csv_file.stem).alias('source_file'))
        dfs.append(df)
        
        # Прогресс
        print(f"  ✓ {csv_file.name} -> {df.height} строк")
    
    if failed_files:
        print(f"\n⚠️ Пропущено файлов: {len(failed_files)}")
    
    if not dfs:
        raise ValueError("Нет данных для объединения")
    
    # Объединяем все DataFrame
    combined_df = pl.concat(dfs)
    
    print(f"\n✅ Всего строк: {combined_df.height:,}")
    print(f"📊 Колонки и типы:")
    for col, dtype in combined_df.schema.items():
        print(f"    {col}: {dtype}")
    
    return combined_df


def save_to_postgres(df: pl.DataFrame, table_name: str, conn):
    """
    Сохраняет Polars DataFrame в PostgreSQL
    """
    # Преобразуем Polars DataFrame в список кортежей
    # Добавляем колонку с константным значением
    df_with_timeframe = df.with_columns(pl.lit(timeframe).alias('timeframe'))

    records = df_with_timeframe.select([
        'instrument_uid', 'candle_time', 'open_price', 'close_price',
        'high_price', 'low_price', 'volume', 'timeframe'
    ]).to_numpy().tolist()
    
    sql = f"""
        INSERT INTO {table_name} (
            instrument_uid, candle_time, open_price, close_price, 
            high_price, low_price, volume, timeframe
        ) VALUES %s
        ON CONFLICT (instrument_uid, candle_time, timeframe) DO NOTHING
    """
    
    with conn.cursor() as cur:
        execute_values(cur, sql, records, page_size=1000)
    conn.commit()
    
    print(f"✅ Сохранено {len(records)} записей в {table_name}")


def main():
    df = load_all_csv_to_df(seeds_folder)
    
    conn = psycopg2.connect(**DB_CONFIG)
    save_to_postgres(df, "candles", conn)
    conn.close()


if __name__ == "__main__":
    main()
