"""Расчёт RSI и генерация торговых сигналов."""
import polars as pl


def calculate_rsi(df: pl.DataFrame, period: int = 14) -> pl.Series:
    """
    Вычисляет индикатор RSI (Relative Strength Index) по закрывающим ценам.
    Возвращает Series того же размера, где первые (period-1) значений NaN.
    """
    close = df["close_price"].cast(pl.Float64)
    delta = close.diff()
    up = delta.clip(lower_bound=0)
    down = delta.clip(upper_bound=0).abs()
    roll_up = up.rolling_mean(period)
    roll_down = down.rolling_mean(period)
    rs = roll_up / roll_down
    rsi = 100 - (100 / (1 + rs))
    return rsi


def generate_signal(df: pl.DataFrame, low: int = 30, high: int = 70) -> pl.DataFrame:
    """
    Генерирует сигналы BUY/SELL на основе пересечения уровней RSI.
    Добавляет колонку 'rsi_signal' (BUY, SELL или None).
    Требует наличия колонки 'rsi' в DataFrame.
    """
    rsi = df["rsi"]
    rsi_shift = rsi.shift(1)
    buy = (rsi_shift < low) & (rsi >= low)
    sell = (rsi_shift > high) & (rsi <= high)
    signal = pl.when(buy).then(pl.lit("BUY")).when(sell).then(pl.lit("SELL")).otherwise(None)
    return df.with_columns(signal.alias("rsi_signal"))