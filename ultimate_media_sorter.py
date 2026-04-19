import os
import shutil
import hashlib
from datetime import datetime
from PIL import Image
from pathlib import Path

# 1. Снимаем все лимиты. Читаем любые размеры!
Image.MAX_IMAGE_PIXELS = None 

def get_file_hash(path):
    """Уникальный отпечаток: Размер + MD5 содержимое."""
    try:
        file_size = os.path.getsize(path)
        hasher = hashlib.md5()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return f"{file_size}_{hasher.hexdigest()}"
    except:
        return None

def get_best_date(path):
    """Ищем дату: EXIF -> Дата создания файла."""
    try:
        image = Image.open(path)
        info = image._getexif()
        if info:
            for tag in [36867, 306]:
                if tag in info:
                    return datetime.strptime(info[tag], '%Y:%m:%d %H:%M:%S')
    except:
        pass

    try:
        # Если EXIF нет, берем дату из системы
        stats = os.stat(path)
        return datetime.fromtimestamp(min(stats.st_mtime, stats.st_ctime))
    except:
        return None

def main():
    print("\n" + "═"*50)
    print("🏆 FINAL ARCHIVE SYSTEM v5.0: THE END")
    print("═"*50)
    print("📸 ФОТО: JPG, PNG, HEIC, BMP, TIFF, WEBP, GIF, PSD")
    print("🎥 ВИДЕО: MP4, MOV, AVI, MKV, WMV, MPG, 3GP")
    print("═"*50)
    
    src_input = input("👉 Откуда (Источник): ").strip().replace('"', '').replace("'", "")
    dst_input = input("👉 Куда (Золотой архив): ").strip().replace('"', '').replace("'", "")
    
    source = Path(src_input)
    output = Path(dst_input)

    if not source.exists():
        print("❌ Ошибка: Путь не найден!")
        return

    output.mkdir(parents=True, exist_ok=True)
    
    # ВСЕВОЗМОЖНЫЕ РАСШИРЕНИЯ (ФОТО + ВИДЕО)
    media_exts = (
        # Фото и изображения
        '.jpg', '.jpeg', '.png', '.heic', '.webp', '.gif', '.bmp', '.tiff', '.tif', '.psd',
        '.JPG', '.JPEG', '.PNG', '.HEIC', '.WEBP', '.GIF', '.BMP', '.TIFF', '.TIF', '.PSD',
        # Видео
        '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.mpg', '.mpeg', '.3gp', '.m4v',
        '.MP4', '.MOV', '.AVI', '.MKV', '.WMV', '.MPG', '.MPEG', '.3GP', '.M4V'
    )
    
    junk_names = ('.DS_Store', 'Thumbs.db', 'desktop.ini')
    junk_exts = ('.lnk', '.url', '.tmp', '.ini')
    
    hashes_seen = set()
    stats = {'moved': 0, 'duplicates': 0, 'junk': 0, 'errors': 0}

    print("\n🏁 Финишная зачистка запущена. Поехали!")

    for root, dirs, files in os.walk(source, topdown=False):
        if str(output) in root:
            continue
            
        for file in files:
            file_path = Path(root) / file
            
            # А. ОБРАБОТКА МЕДИА
            if file.lower().endswith(media_exts):
                f_hash = get_file_hash(file_path)
                
                # Проверка на дубликат (размер + контент)
                if f_hash and f_hash in hashes_seen:
                    try:
                        file_path.unlink()
                        stats['duplicates'] += 1
                    except:
                        stats['errors'] += 1
                    continue
                
                if f_hash:
                    hashes_seen.add(f_hash)

                # Определяем дату для папки
                date = get_best_date(file_path)
                if date:
                    year = str(date.year)
                    month = date.strftime('%m-%B')
                    target_dir = output / year / month
                    target_dir.mkdir(parents=True, exist_ok=True)
                    
                    target_path = target_dir / file
                    
                    # Если имена совпали, но файлы разные
                    counter = 1
                    while target_path.exists():
                        target_path = target_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
                        counter += 1
                    
                    try:
                        shutil.move(str(file_path), str(target_path))
                        stats['moved'] += 1
                    except:
                        stats['errors'] += 1
                continue

            # Б. УДАЛЕНИЕ МУСОРА
            is_junk = file in junk_names or \
                      file.startswith('._') or \
                      any(file.lower().endswith(ext) for ext in junk_exts)
            
            if is_junk:
                try:
                    file_path.unlink()
                    stats['junk'] += 1
                except:
                    stats['errors'] += 1

        # В. УДАЛЕНИЕ ПУСТЫХ ПАПОК
        for name in dirs:
            dir_path = Path(root) / name
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
            except:
                continue

    # Финальный аккорд
    print("\n" + "═"*50)
    print("🎉 МИССИЯ ВЫПОЛНЕНА!")
    print(f"📦 Итого перенесено (уникальных): {stats['moved']}")
    print(f"👯 Удалено дубликатов: {stats['duplicates']}")
    print(f"🧹 Выброшено мусора: {stats['junk']}")
    print("═"*50)
    print(f"📁 Весь твой архив теперь тут: {output}")
    print("😎 Поздравляю! Мы это сделали.")

if __name__ == "__main__":
    main()