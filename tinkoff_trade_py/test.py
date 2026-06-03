import zipfile
from pathlib import Path

# Папка с архивами
folder = Path("./seeds/")

# Находим все zip файлы
for zip_file in folder.glob("*.zip"):
    print(f"Распаковка: {zip_file.name}")
    
    # Распаковываем в папку с именем архива (без .zip)
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(folder / zip_file.stem)
    
    print(f"  ✅ Готово! Файлы в: {zip_file.stem}")

print("Все архивы распакованы!")