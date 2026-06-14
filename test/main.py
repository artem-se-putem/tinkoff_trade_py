import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ============================================
# 1. СОЗДАЁМ НЕБОЛЬШИЕ ДАННЫЕ
# ============================================

# Создаём даты (10 дней)
dates = []
prices = []

start_date = datetime(2026, 6, 1)
for i in range(10):
    date = start_date + timedelta(days=i)
    dates.append(date)
    
    # Цена доллара: от 85 до 95 с небольшими колебаниями
    price = 90 + 2 * (i % 3) + 0.5 * (i % 5) - 1.5 * (i % 4)
    prices.append(round(price, 2))

# Создаём DataFrame
df = pd.DataFrame({
    'date': dates,
    'usd_rub': prices,
    'volume': [1000, 1200, 900, 1500, 1100, 1300, 800, 1400, 950, 1600]
})

print("=" * 50)
print("📊 НАШИ ДАННЫЕ")
print("=" * 50)
print(df)
print("\n")

# ============================================
# 2. ПРОСТОЙ ГРАФИК (ЛИНИЯ)
# ============================================

plt.figure(figsize=(10, 5))

# График цены
plt.subplot(1, 2, 1)  # 1 строка, 2 колонки, 1-й график
plt.plot(df['date'], df['usd_rub'], marker='o', linewidth=2, color='blue')
plt.title('Курс USD/RUB', fontsize=14)
plt.xlabel('Дата')
plt.ylabel('Цена (₽)')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)

# График объёма
plt.subplot(1, 2, 2)  # 1 строка, 2 колонки, 2-й график
plt.bar(df['date'], df['volume'], color='green', alpha=0.7)
plt.title('Объём торгов', fontsize=14)
plt.xlabel('Дата')
plt.ylabel('Объём')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

# ============================================
# 3. СТАТИСТИКА
# ============================================
print("\n" + "=" * 50)
print("📈 СТАТИСТИКА")
print("=" * 50)
print(f"Максимальная цена: {df['usd_rub'].max()} ₽")
print(f"Минимальная цена: {df['usd_rub'].min()} ₽")
print(f"Средняя цена: {df['usd_rub'].mean():.2f} ₽")
print(f"Всего объём: {df['volume'].sum():,}")

# ============================================
# 4. КОГДА ЛУЧШЕ ПОКУПАТЬ?
# ============================================
min_price_row = df.loc[df['usd_rub'].idxmin()]
max_price_row = df.loc[df['usd_rub'].idxmax()]

print(f"\n💰 Лучший день для покупки: {min_price_row['date'].strftime('%Y-%m-%d')} по {min_price_row['usd_rub']} ₽")
print(f"💸 Лучший день для продажи: {max_price_row['date'].strftime('%Y-%m-%d')} по {max_price_row['usd_rub']} ₽")