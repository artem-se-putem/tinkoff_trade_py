import zipfile
from pathlib import Path
from utils import logger

# Папка с архивами
folder = Path(__file__).parent

# Находим все zip файлы
for zip_file in folder.glob("*.zip"):
    logger.info(f"Распаковка: {zip_file.name}")
    
    # Распаковываем в папку с именем архива (без .zip)
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(folder / zip_file.stem)
    
    logger.info(f"  ✅ Готово! Файлы в: {zip_file.stem}")

logger.info("Все архивы распакованы!")