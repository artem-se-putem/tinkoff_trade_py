

свеча:

дано:
цена открытия
цена закрытия
период
date_from
date_to

результат:

rsi = 100 - 100 / (1 + avg_gain / avg_loss)


def rsi(df, period, ):
