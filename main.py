import argparse
from datetime import datetime, timedelta, timezone

from aggregator import aggregate_data
from api import APIClient
from email_sender import EmailSender
from google_sheets import GoogleSheetsClient
from loader import load_data
from logger import clean_old_logs, logger
from transformer import transform_data
from validator import validate_data


def parse_args():
    """Возвращает аргументы командной строки."""
    parser = argparse.ArgumentParser()

    parser.add_argument("--start")
    parser.add_argument("--end")

    return parser.parse_args()


def get_yesterday():
    """
    Возвращает начало и конец предыдущего дня
    в формате YYYY-MM-DD HH:MM.
    """
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)

    start_datetime = yesterday.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    end_datetime = yesterday.replace(
        hour=23,
        minute=59,
        second=0,
        microsecond=0,
    )

    return (
        start_datetime.strftime("%Y-%m-%d %H:%M"),
        end_datetime.strftime("%Y-%m-%d %H:%M"),
    )


def validate_datetime(date_time):
    """
    Проверяет дату на соответствие формату
    YYYY-MM-DD HH:MM.
    """
    try:
        datetime.strptime(date_time, "%Y-%m-%d %H:%M")
        return date_time
    except ValueError:
        raise ValueError("Некорректный формат даты. Используйте YYYY-MM-DD HH:MM.")


def get_date_range(args):
    """
    Определяет период обработки данных.

    Если даты не переданы, используется предыдущий день.
    При передаче --start и --end проверяется их формат
    и последовательность.
    """
    if args.start is None and args.end is None:
        return get_yesterday()

    if args.start is not None and args.end is not None:
        start_datetime = validate_datetime(args.start)
        end_datetime = validate_datetime(args.end)

        start = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M")
        end = datetime.strptime(end_datetime, "%Y-%m-%d %H:%M")

        if start > end:
            raise ValueError("Дата начала не может быть позже даты окончания.")

        return start_datetime, end_datetime

    raise ValueError("Необходимо передать оба аргумента: --start и --end.")


def main(start_datetime, end_datetime):
    """
    Запускает ETL-пайплайн для указанного периода.
    """
    clean_old_logs()

    api_client = APIClient()
    email_sender = EmailSender()

    logger.info(f"Запрашиваем данные за период: {start_datetime} — {end_datetime}.")

    data = api_client.get_statistics(
        start_datetime,
        end_datetime,
    )

    if data is None:
        logger.error("Не удалось получить данные. ETL-пайплайн остановлен.")
        return

    logger.info("Данные успешно получены. Передаём данные на следующий этап.")

    valid_data = validate_data(data)

    if valid_data is None:
        logger.error("Ни одна запись не прошла валидацию.")
        return

    if not valid_data:
        logger.info("За указанный период данных нет. Загрузка в БД не требуется.")
        return

    logger.info("Записи прошли валидацию.")

    transformed_data = transform_data(valid_data)

    logger.info("Данные успешно преобразованы.")

    start_date = start_datetime.split()[0]
    end_date = end_datetime.split()[0]

    if start_date == end_date:
        report_period = start_date
    else:
        report_period = f"{start_date} — {end_date}"

    report = aggregate_data(
        transformed_data,
        report_period,
    )

    load_data(transformed_data)

    # Внешние сервисы используются после успешной загрузки данных в БД.
    google_sheets_client = GoogleSheetsClient()
    if google_sheets_client.upload(report):
        logger.info("Агрегированный отчёт загружен в Google Sheets.")

    email_sender.send(report)


if __name__ == "__main__":
    args = parse_args()
    start_datetime, end_datetime = get_date_range(args)
    main(start_datetime, end_datetime)
