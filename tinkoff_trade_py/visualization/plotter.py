# visualization/plotter.py
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from typing import List, Optional
from datetime import datetime

def plot_simple_candlestick(prices: List[float], title: str = "Price Chart"):
    """Простой график цены"""
    plt.figure(figsize=(12, 6))
    plt.plot(prices, 'b-', linewidth=1)
    plt.title(title)
    plt.xlabel('Время')
    plt.ylabel('Цена')
    plt.grid(True, alpha=0.3)
    
    # Добавляем скользящие средние
    if len(prices) >= 14:
        ma14 = [sum(prices[i-14:i])/14 for i in range(14, len(prices))]
        plt.plot(range(13, len(prices)), ma14, 'r--', label='SMA 14', linewidth=1)
        plt.legend()
    
    plt.tight_layout()
    plt.show()


try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ Для графиков установите: pip install matplotlib")


def plot_rsi_analysis(
    instrument_uid: str,
    dates: List[datetime],
    prices: List[float],
    rsi_values: List[float],
    current_rsi: float,
    current_price: float,
    signal: str,
    reason: str,
    oversold: int = 30,
    overbought: int = 70,
    save_path: str = "reports"
) -> Optional[str]:
    """
    Визуализация RSI анализа
    
    Args:
        instrument_uid: UID инструмента
        dates: Список дат
        prices: Список цен
        rsi_values: Список значений RSI
        current_rsi: Текущее значение RSI
        current_price: Текущая цена
        signal: Сигнал ('buy', 'sell', 'hold')
        reason: Причина сигнала
        oversold: Уровень перепроданности
        overbought: Уровень перекупленности
        save_path: Путь для сохранения графика
    
    Returns:
        Путь к сохранённому файлу или None
    """
    
    if not MATPLOTLIB_AVAILABLE:
        print("⚠️ Matplotlib не установлен. Пропускаем визуализацию")
        return None
    
    if not dates or not prices or not rsi_values:
        print("⚠️ Нет данных для визуализации")
        return None
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    fig.suptitle(f'RSI Анализ: {instrument_uid}', fontsize=14, fontweight='bold')
    
    # ===== График 1: Цена =====
    ax1.plot(dates, prices, 'b-', linewidth=1.5, label='Цена закрытия')
    ax1.set_ylabel('Цена (руб)', fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')
    
    # Отметка текущей цены
    ax1.axhline(y=current_price, color='g', linestyle='--', alpha=0.7)
    ax1.text(dates[-1], current_price, f' {current_price:.2f}', 
             verticalalignment='bottom', fontsize=9, color='green')
    
    # ===== График 2: RSI =====
    ax2.plot(dates, rsi_values, 'purple', linewidth=1.5, label='RSI (14)')
    ax2.set_ylabel('RSI', fontsize=11)
    ax2.set_xlabel('Дата', fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    # Линии уровней
    ax2.axhline(y=overbought, color='r', linestyle='--', alpha=0.5, 
                label=f'Перекупленность ({overbought})')
    ax2.axhline(y=oversold, color='g', linestyle='--', alpha=0.5, 
                label=f'Перепроданность ({oversold})')
    ax2.axhline(y=50, color='gray', linestyle=':', alpha=0.5)
    
    # Закраска зон
    ax2.fill_between(dates, overbought, 100, alpha=0.15, color='red', 
                     label='Зона продажи')
    ax2.fill_between(dates, 0, oversold, alpha=0.15, color='green', 
                     label='Зона покупки')
    
    ax2.set_ylim(0, 100)
    ax2.legend(loc='upper left')
    
    # Текущее значение RSI
    ax2.axhline(y=current_rsi, color='orange', linestyle=':', alpha=0.7)
    ax2.text(dates[-1], current_rsi, f' RSI={current_rsi:.1f}', 
             verticalalignment='bottom', fontsize=10, color='orange', 
             fontweight='bold')
    
    # Форматирование дат
    fig.autofmt_xdate()
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    # ===== Сигнал и рекомендация =====
    signal_config = {
        'buy': ('green', 'ПОКУПКА 🟢'),
        'sell': ('red', 'ПРОДАЖА 🔴'),
        'hold': ('gray', 'ДЕРЖАТЬ ⚪')
    }.get(signal, ('gray', 'НЕТ СИГНАЛА'))
    
    fig.text(0.02, 0.02, f"Решение: {signal_config[1]} | {reason}", 
             fontsize=10, color=signal_config[0], fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9))
    
    plt.tight_layout()
    
    # Сохраняем график
    import os
    from datetime import datetime as dt
    
    os.makedirs(save_path, exist_ok=True)
    filename = f"{save_path}/{instrument_uid}_{dt.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(filename, dpi=100, bbox_inches='tight')
    print(f"📊 График сохранён: {filename}")
    
    plt.show()
    plt.close()
    
    return filename


def plot_console_chart(prices: List[float], rsi: float, width: int = 50):
    """
    Простой консольный график (ASCII)
    """
    if not prices:
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
    
    # Рисуем график
    for i in range(width - 1, -1, -5):  # Сверху вниз с шагом 5
        line = ""
        for n in normalized:
            if n >= i:
                line += "█"
            else:
                line += " "
        print(f"│{line}│")
    
    print("└" + "─" * width + "┘")
    print(f"  Мин: {min_price:.2f}  Макс: {max_price:.2f}  Текущая: {prices[-1]:.2f}")
    
    # RSI шкала
    print("\n📊 RSI шкала:")
    bar_length = 40
    filled = int(bar_length * rsi / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"  {bar} {rsi:.1f}")
    
    if rsi < 30:
        print("  🟢 Зона перепроданности! -> ПОКУПКА")
    elif rsi > 70:
        print("  🔴 Зона перекупленности! -> ПРОДАЖА")
    else:
        print("  ⚪ Нейтральная зона -> ДЕРЖАТЬ")
    
    print("=" * (width + 4) + "\n")


def plot_strategy_summary(signals_history: List[dict]):
    """
    График истории сигналов
    """
    if not MATPLOTLIB_AVAILABLE or not signals_history:
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    dates = [s['timestamp'] for s in signals_history]
    prices = [s['price'] for s in signals_history]
    
    # Цвета для сигналов
    colors = []
    for s in signals_history:
        if s['action'] == 'buy':
            colors.append('green')
        elif s['action'] == 'sell':
            colors.append('red')
        else:
            colors.append('gray')
    
    ax.scatter(dates, prices, c=colors, s=100, alpha=0.7, zorder=5)
    ax.plot(dates, prices, 'b-', alpha=0.3, zorder=1)
    
    ax.set_title('История торговых сигналов', fontsize=14)
    ax.set_xlabel('Дата')
    ax.set_ylabel('Цена')
    ax.grid(True, alpha=0.3)
    
    # Легенда
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', label='Покупка'),
        Patch(facecolor='red', label='Продажа'),
        Patch(facecolor='gray', label='Держать')
    ]
    ax.legend(handles=legend_elements, loc='upper left')
    
    plt.tight_layout()
    
    import os
    os.makedirs('reports', exist_ok=True)
    filename = f"reports/signals_history_{datetime.now().strftime('%Y%m%d')}.png"
    plt.savefig(filename, dpi=100)
    plt.show()
    plt.close()
    
    print(f"📊 История сигналов сохранена: {filename}")
