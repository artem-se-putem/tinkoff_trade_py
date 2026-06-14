"""Отрисовка графиков: свечи + RSI (оверлей) + объём."""
import polars as pl
import matplotlib.pyplot as plt


def plot_candles(df: pl.DataFrame,
                  instrument_uid: str = "T_TQBR",
                  limit: int = 200):
    """Отрисовка свечей + RSI (оверлей), объёма и BUY/SELL сигналов.

    Параметры
    ----------
    df: DataFrame со свечами, колонкой 'rsi' и опционально 'rsi_signal'.
    instrument_uid: фильтр по инструменту.
    limit: количество последних свечей.
    """
    # Фильтрация по инструменту
    if instrument_uid:
        df = df.filter(pl.col("instrument_uid") == instrument_uid)
    # Сортировка и ограничение
    df = df.sort("candle_time").tail(limit)

    # Подготовка данных для matplotlib
    pdf = df.to_pandas()

    # Создаём графики: цена+RSI (оверлей) + объём
    fig, (ax_price, ax_volume) = plt.subplots(2, 1, figsize=(14, 10), sharex=True,
                                               gridspec_kw={'height_ratios': [3, 1]})

    # ----- Цена (свечи) -----
    for _, row in pdf.iterrows():
        col = 'green' if row['close_price'] >= row['open_price'] else 'red'
        # Тени
        ax_price.plot([row['candle_time'], row['candle_time']],
                      [row['low_price'], row['high_price']], color='black', linewidth=0.5)
        # Тело
        ax_price.plot([row['candle_time'], row['candle_time']],
                      [row['open_price'], row['close_price']], color=col, linewidth=4)
    ax_price.set_ylabel('Цена, ₽')
    ax_price.grid(True, alpha=0.3)

    # ----- RSI (оверлей на ценовой график) -----
    has_rsi = "rsi" in pdf.columns
    if has_rsi:
        ax_rsi = ax_price.twinx()
        ax_rsi.plot(pdf['candle_time'], pdf['rsi'], color='purple', linewidth=1.2,
                    alpha=0.8, label='RSI (14)')
        ax_rsi.axhline(70, color='red', linestyle='--', linewidth=0.8, alpha=0.6)
        ax_rsi.axhline(30, color='green', linestyle='--', linewidth=0.8, alpha=0.6)
        ax_rsi.fill_between(pdf['candle_time'], 70, 100, alpha=0.05, color='red')
        ax_rsi.fill_between(pdf['candle_time'], 0, 30, alpha=0.05, color='green')
        ax_rsi.set_ylim(0, 100)
        ax_rsi.set_ylabel('RSI', color='purple', fontsize=11)
        ax_rsi.tick_params(axis='y', labelcolor='purple')

        # Сигналы BUY/SELL — маркеры на ценовом графике
        has_signals = "rsi_signal" in pdf.columns
        if has_signals:
            buys_pdf = pdf[pdf['rsi_signal'] == 'BUY']
            sells_pdf = pdf[pdf['rsi_signal'] == 'SELL']
            if len(buys_pdf) > 0:
                ax_price.scatter(buys_pdf['candle_time'], buys_pdf['low_price'],
                                 marker='^', color='green', s=120, zorder=5, label='BUY')
            if len(sells_pdf) > 0:
                ax_price.scatter(sells_pdf['candle_time'], sells_pdf['high_price'],
                                 marker='v', color='red', s=120, zorder=5, label='SELL')

        # Объединяем легенды с обеих осей
        lines_price, labels_price = ax_price.get_legend_handles_labels()
        lines_rsi, labels_rsi = ax_rsi.get_legend_handles_labels()
        ax_rsi.legend(lines_price + lines_rsi, labels_price + labels_rsi,
                       loc='upper left', fontsize=9)

        ax_price.set_title(f'Свечи + RSI  ({instrument_uid})', fontsize=13)
    else:
        ax_price.set_title(f'Свечи  ({instrument_uid})', fontsize=13)

    # ----- Объём -----
    colors = ['green' if c >= o else 'red' for c, o in zip(pdf['close_price'], pdf['open_price'])]
    ax_volume.bar(pdf['candle_time'], pdf['volume'], color=colors, alpha=0.7)
    ax_volume.set_title('Объём торгов')
    ax_volume.set_ylabel('Объём')
    ax_volume.grid(True, alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()