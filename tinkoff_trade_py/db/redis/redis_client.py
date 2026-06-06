import redis
from typing import Dict, Any, Optional
from utils import logger

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
    
    def set_price(self, figi: str, price: float):
        """Сохранить текущую цену"""
        self.client.set(f"price:{figi}", price)
    
    def get_price(self, figi: str) -> Optional[float]:
        """Получить текущую цену"""
        price = self.client.get(f"price:{figi}")
        return float(price) if price else None
    
    def set_rsi(self, figi: str, rsi: float):
        """Сохранить значение RSI"""
        self.client.set(f"rsi:{figi}", rsi)
    
    def get_rsi(self, figi: str) -> Optional[float]:
        """Получить значение RSI"""
        rsi = self.client.get(f"rsi:{figi}")
        return float(rsi) if rsi else None


# Тест
if __name__ == '__main__':
    r = RedisClient()
    r.set_price('SBER', 245.30)
    r.set_rsi('SBER', 65.4)
    
    logger.info(f"Цена: {r.get_price('SBER')}")
    logger.info(f"RSI: {r.get_rsi('SBER')}")