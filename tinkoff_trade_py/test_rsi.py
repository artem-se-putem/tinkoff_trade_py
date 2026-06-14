import polars as pl
import pytest
from tinkoff_trade_py.analysis.rsi import calculate_rsi, generate_signal
from tinkoff_trade_py.analysis.recommendation import get_recommendation


def test_calculate_rsi_basic():
    # Simple increasing prices should produce high RSI values
    data = {
        "instrument_uid": ["T_TQBR"] * 5,
        "candle_time": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"],
        "open_price": [10, 11, 12, 13, 14],
        "close_price": [11, 12, 13, 14, 15],
        "low_price": [9, 10, 11, 12, 13],
        "high_price": [12, 13, 14, 15, 16],
        "volume": [100, 110, 120, 130, 140],
    }
    df = pl.DataFrame(data)
    rsi = calculate_rsi(df, period=2)
    # After the first period, RSI should be 100 for strictly rising prices
    assert rsi[2] == pytest.approx(100.0, rel=1e-2)


def test_generate_signal_crossings():
    # Create a dataframe with RSI manually set to cross thresholds
    data = {
        "instrument_uid": ["T_TQBR"] * 4,
        "candle_time": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"],
        "close_price": [1, 2, 1, 2],
        "open_price": [1, 1, 2, 1],
        "low_price": [0.5, 0.8, 0.9, 1],
        "high_price": [1.2, 2.2, 1.5, 2.5],
        "volume": [10, 20, 15, 25],
    }
    df = pl.DataFrame(data)
    # Force RSI column that crosses below 30 then above 30
    df = df.with_columns(pl.Series([35.0, 25.0, 35.0, 45.0]).alias("rsi"))
    signal_df = generate_signal(df, low=30, high=70)
    signals = signal_df.select("rsi_signal").to_series().to_list()
    # Expect BUY on index 2 (cross up) and no SELL because high threshold not crossed
    assert signals[2] == "BUY"
    assert signals[0] is None


def test_get_recommendation_buy_zone():
    """RSI < 30 → рекомендация BUY"""
    data = {
        "instrument_uid": ["T_TQBR"] * 20,
        "candle_time": [f"2023-01-{i:02d}" for i in range(1, 21)],
        "open_price": [10.0] * 20,
        "close_price": [float(i) for i in range(5, 25)],
        "low_price": [9.0] * 20,
        "high_price": [25.0] * 20,
        "volume": [100] * 20,
    }
    df = pl.DataFrame(data)
    rsi = calculate_rsi(df, period=14)
    df = df.with_columns(rsi.alias("rsi"))
    df = generate_signal(df)
    rec = get_recommendation(df, instrument_uid="T_TQBR")
    assert rec["signal"] in ("BUY", "SELL", "HOLD")
    assert rec["instrument_uid"] == "T_TQBR"
    assert rec["close_price"] > 0
    assert "reason" in rec


def test_get_recommendation_oversold():
    """Принудительно задаём RSI < 30 — должна быть рекомендация BUY"""
    data = {
        "instrument_uid": ["T_TQBR"] * 3,
        "candle_time": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "open_price": [10.0, 10.0, 10.0],
        "close_price": [10.0, 10.0, 10.0],
        "low_price": [9.0, 9.0, 9.0],
        "high_price": [11.0, 11.0, 11.0],
        "volume": [100, 100, 100],
    }
    df = pl.DataFrame(data)
    # Принудительно задаём RSI = 25 (перепроданность)
    df = df.with_columns(pl.Series([None, None, 25.0]).alias("rsi"))
    df = generate_signal(df)
    rec = get_recommendation(df, instrument_uid="T_TQBR")
    assert rec["signal"] == "BUY"
    assert "перепроданности" in rec["reason"]


def test_get_recommendation_overbought():
    """Принудительно задаём RSI > 70 — должна быть рекомендация SELL"""
    data = {
        "instrument_uid": ["T_TQBR"] * 3,
        "candle_time": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "open_price": [10.0, 10.0, 10.0],
        "close_price": [10.0, 10.0, 10.0],
        "low_price": [9.0, 9.0, 9.0],
        "high_price": [11.0, 11.0, 11.0],
        "volume": [100, 100, 100],
    }
    df = pl.DataFrame(data)
    # Принудительно задаём RSI = 80 (перекупленность)
    df = df.with_columns(pl.Series([None, None, 80.0]).alias("rsi"))
    df = generate_signal(df)
    rec = get_recommendation(df, instrument_uid="T_TQBR")
    assert rec["signal"] == "SELL"
    assert "перекупленности" in rec["reason"]