"""Рекомендации и интерактивный выбор действия."""
import polars as pl


def get_recommendation(df: pl.DataFrame, instrument_uid: str = "T_TQBR") -> dict:
    """Формирует рекомендацию по последней свече на основе RSI и сигналов.

    Возвращает словарь:
        instrument_uid, candle_time, close_price, rsi,
        signal (BUY/SELL/HOLD), reason (строка с объяснением)
    """
    if instrument_uid:
        df = df.filter(pl.col("instrument_uid") == instrument_uid)
    df = df.sort("candle_time")
    last = df.tail(1)

    close_price = last["close_price"].item()
    candle_time = last["candle_time"].item()
    rsi_val = last["rsi"].item() if "rsi" in last.columns else None
    rsi_signal = last["rsi_signal"].item() if "rsi_signal" in last.columns else None

    # Определяем рекомендацию
    if rsi_val is None or str(rsi_val) == "null":
        signal = "HOLD"
        reason = "Недостаточно данных для расчёта RSI"
    elif rsi_signal == "BUY":
        signal = "BUY"
        reason = f"RSI пересёк уровень 30 снизу вверх (RSI={rsi_val:.1f}) — выход из перепроданности"
    elif rsi_signal == "SELL":
        signal = "SELL"
        reason = f"RSI пересёк уровень 70 сверху вниз (RSI={rsi_val:.1f}) — выход из перекупленности"
    elif rsi_val < 30:
        signal = "BUY"
        reason = f"RSI={rsi_val:.1f} < 30 — зона перепроданности, возможен отскок вверх"
    elif rsi_val > 70:
        signal = "SELL"
        reason = f"RSI={rsi_val:.1f} > 70 — зона перекупленности, возможна коррекция вниз"
    else:
        signal = "HOLD"
        reason = f"RSI={rsi_val:.1f} в нейтральной зоне (30–70), нет сигнала"

    return {
        "instrument_uid": instrument_uid,
        "candle_time": candle_time,
        "close_price": float(close_price),
        "rsi": float(rsi_val) if rsi_val is not None and str(rsi_val) != "null" else None,
        "signal": signal,
        "reason": reason,
    }


def interactive_decision(rec: dict) -> str:
    """Выводит рекомендацию в консоль и предлагает пользователю выбор действия.

    Параметры
    ----------
    rec: словарь от get_recommendation()

    Возвращает
    -----------
    Строку с выбранным действием: 'BUY', 'SELL' или 'SKIP'
    """
    icons = {"BUY": "🟢", "SELL": "🔴", "HOLD": "⚪"}

    print("\n" + "=" * 60)
    print("📊  ТОРГОВЫЙ СИГНАЛ")
    print("=" * 60)
    print(f"  Инструмент:  {rec['instrument_uid']}")
    print(f"  Время:       {rec['candle_time']}")
    print(f"  Цена:        {rec['close_price']:.2f} ₽")
    if rec['rsi'] is not None:
        print(f"  RSI (14):    {rec['rsi']:.1f}")
    else:
        print(f"  RSI (14):    —")
    print(f"  Рекомендация: {icons.get(rec['signal'], '')} {rec['signal']}")
    print(f"  Причина:     {rec['reason']}")
    print("=" * 60)

    print("\n  Ваше действие:")
    print("    [1] 🟢 Купить  (BUY)")
    print("    [2] 🔴 Продать (SELL)")
    print("    [3] ⏭️  Пропустить (SKIP)")

    while True:
        choice = input("\n  Выберите [1/2/3]: ").strip()
        action_map = {"1": "BUY", "2": "SELL", "3": "SKIP"}
        if choice in action_map:
            action = action_map[choice]
            break
        print("  ⚠️  Введите 1, 2 или 3")

    match_icon = "✅" if action == rec["signal"] else "⚠️"
    action_names = {"BUY": "КУПИТЬ", "SELL": "ПРОДАТЬ", "SKIP": "ПРОПУСТИТЬ"}
    print(f"\n  {match_icon} Вы выбрали: {action_names[action]}")
    if action == "SKIP":
        print("  Решение не принято. Ожидание следующего сигнала.")
    elif action == rec["signal"]:
        print(f"  ✅ Совпадает с рекомендацией ({rec['signal']}).")
    else:
        print(f"  ⚠️ Не совпадает с рекомендацией ({rec['signal']}). Решение за вами!")
    print("=" * 60 + "\n")

    return action