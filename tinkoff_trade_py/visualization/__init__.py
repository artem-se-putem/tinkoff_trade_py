from typing import List, Optional


def plot_console_chart(prices: List[float], rsi: Optional[float] = None, width: int = 50):
    """
    Простой консольный график (ASCII)
    
    Args:
        prices: Список цен
        rsi: Текущее значение RSI (опционально)
        width: Ширина графика
    """
    if not prices:
        print("Нет данных для отображения")
        return
    
    min_price = min(prices)
    max_price = max(prices)
    price_range = max_price - min_price
    
    if price_range == 0:
        price_range = 1
    
    # Нормализуем цены
    normalized = [int((p - min_price) / price_range * (width - 1)) for p in prices]
    
    print("\n" + "=" * (width + 4))
    print(f"📈 Цена закрытия (последние {len(prices)} значений)")
    print("=" * (width + 4))
    
    # Рисуем график (сверху вниз)
    for level in range(width - 1, -1, -5):
        line = ""
        for n in normalized:
            if n >= level:
                line += "█"
            else:
                line += " "
        print(f"│{line}│")
    
    print("└" + "─" * width + "┘")
    print(f"  Мин: {min_price:.2f}  Макс: {max_price:.2f}  Текущая: {prices[-1]:.2f}")
    
    # RSI шкала
    if rsi is not None:
        print("\n📊 RSI:")
        bar_length = 40
        filled = int(bar_length * rsi / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"  [{bar}] {rsi:.1f}")
        
        if rsi < 30:
            print("  🟢 RSI < 30: Зона перепроданности -> РЕКОМЕНДАЦИЯ: ПОКУПКА")
        elif rsi > 70:
            print("  🔴 RSI > 70: Зона перекупленности -> РЕКОМЕНДАЦИЯ: ПРОДАЖА")
        else:
            print("  ⚪ 30 ≤ RSI ≤ 70: Нейтральная зона -> РЕКОМЕНДАЦИЯ: ДЕРЖАТЬ")
    
    print("=" * (width + 4) + "\n")


def plot_simple_chart(prices: List[float], title: str = "Price Chart"):
    """Упрощённый линейный график в консоли"""
    if not prices:
        return
    
    min_price = min(prices)
    max_price = max(prices)
    
    print(f"\n📊 {title}")
    print(f"  Диапазон: {min_price:.2f} - {max_price:.2f}")
    
    # Простой спарклайн (Sparkline)
    spark_chars = "▁▂▃▄▅▆▇█"
    spark_line = ""
    
    for price in prices:
        if max_price == min_price:
            idx = 0
        else:
            idx = int((price - min_price) / (max_price - min_price) * (len(spark_chars) - 1))
        spark_line += spark_chars[idx]
    
    print(f"  {spark_line}")
    print(f"  Текущая: {prices[-1]:.2f}\n")


def show_decision(
    instrument_uid: str,
    current_price: float,
    rsi: float,
    signal: str,
    reason: str,
    oversold: int = 30,
    overbought: int = 70
):
    """Показать торговое решение в наглядном виде"""
    print("\n" + "=" * 60)
    print(f"📊 {instrument_uid}")
    print("=" * 60)
    
    print(f"💰 Цена: {current_price:.2f}")
    print(f"📈 RSI (14): {rsi:.1f}")
    
    # RSI шкала
    bar_length = 40
    filled = int(bar_length * rsi / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\n  RSI шкала: [{bar}]")
    
    # Отметка уровней
    oversold_pos = int(bar_length * oversold / 100)
    overbought_pos = int(bar_length * overbought / 100)
    print(f"              {' ' * oversold_pos}↓{oversold}     {' ' * (overbought_pos - oversold_pos - 3)}↓{overbought}")
    
    # Сигнал
    if signal == 'buy':
        print(f"\n🟢 РЕШЕНИЕ: ПОКУПАТЬ")
        print(f"   Причина: {reason}")
    elif signal == 'sell':
        print(f"\n🔴 РЕШЕНИЕ: ПРОДАВАТЬ")
        print(f"   Причина: {reason}")
    else:
        print(f"\n⚪ РЕШЕНИЕ: ДЕРЖАТЬ")
        print(f"   Причина: {reason}")
    
    print("=" * 60 + "\n")


__all__ = [
    'plot_console_chart',
    'plot_simple_chart', 
    'show_decision'
]