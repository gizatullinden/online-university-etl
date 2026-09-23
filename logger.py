import logging
from datetime import datetime, timedelta
from pathlib import Path


current_date = datetime.now().strftime("%Y-%m-%d")

logs_dir = Path("logs")
log_file = logs_dir / f"{current_date}.log"

logs_dir.mkdir(exist_ok=True)

logger = logging.getLogger("online_university_etl")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")


# Не создаём повторные обработчики при повторном импорте модуля.
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(
        filename=log_file,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def clean_old_logs():
    """
    Удаляет файлы логов старше трёх дней.
    """
    cutoff_date = datetime.now() - timedelta(days=3)
    deleted_count = 0

    for file in logs_dir.iterdir():
        if not file.is_file() or file.suffix != ".log":
            continue

        # Текущий лог должен сохраняться независимо от его даты изменения.
        if file.name == log_file.name:
            continue

        file_date = datetime.fromtimestamp(file.stat().st_mtime)

        if file_date < cutoff_date:
            file.unlink()
            deleted_count += 1

    logger.info(f"Очистка старых логов завершена. Удалено файлов: {deleted_count}.")
