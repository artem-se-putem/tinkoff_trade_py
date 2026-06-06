# utils/logger_config.py
import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logger(name: str = "trading_bot", log_file: Optional[str] = None) -> logging.Logger:
    """
    Настройка логгера с выводом в консоль и (опционально) в файл
    """
    logger = logging.getLogger(name)
    
    # Чтобы не дублировались обработчики при多次ном вызове
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # Формат сообщений
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)-4d | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # 1. Вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 2. Вывод в файл (если указан)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Глобальный логгер по умолчанию
logger = setup_logger()