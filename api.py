import time
from datetime import datetime, timezone

import requests

from config import API_URL, CLIENT, CLIENT_KEY
from logger import logger


class APIClient:
    """
    Клиент для получения статистики через API.
    """

    def __init__(self):
        self.api_url = API_URL
        self.client_key = CLIENT_KEY
        self.client = CLIENT

    @staticmethod
    def format_date(date_time):
        """Преобразует дату в формат, необходимый API."""
        date_time_obj = datetime.strptime(
            date_time,
            "%Y-%m-%d %H:%M",
        )
        date_time_obj = date_time_obj.replace(tzinfo=timezone.utc)

        return date_time_obj.strftime("%Y-%m-%d %H:%M:%S.%f")

    def get_statistics(self, start_datetime, end_datetime):
        """
        Получает статистику за указанный период.

        Возвращает полученные данные или None,
        если запросы завершились неуспешно.
        """
        params = {
            "client": self.client,
            "client_key": self.client_key,
            "start": self.format_date(start_datetime),
            "end": self.format_date(end_datetime),
        }

        for attempt in range(3):
            try:
                response = requests.get(
                    self.api_url,
                    params=params,
                    timeout=30,
                )

                if response.status_code // 100 == 2:
                    data = response.json()
                    logger.info("Запрос выполнен успешно!")
                    return data

                if response.status_code // 100 == 5:
                    # Ошибка сервера может быть временной,
                    # поэтому повторяем запрос с увеличением задержки.
                    logger.warning(
                        f"Попытка {attempt + 1} из 3: "
                        f"сервер вернул код {response.status_code}."
                    )

                    if attempt < 2:
                        time.sleep(2**attempt)

                    continue

                # Для ошибок клиента повторный запрос с теми же
                # параметрами, как правило, не имеет смысла.
                logger.error(
                    f"Сервер вернул код {response.status_code}. "
                    "ETL-пайплайн будет остановлен."
                )
                break

            except requests.exceptions.JSONDecodeError as err:
                logger.warning(
                    f"Попытка {attempt + 1} из 3: ошибка обработки JSON: {err}"
                )

                if attempt < 2:
                    time.sleep(2**attempt)

                continue

            except requests.exceptions.RequestException as err:
                logger.warning(f"Попытка {attempt + 1} из 3: ошибка запроса: {err}")

                if attempt < 2:
                    time.sleep(2**attempt)

                continue

        else:
            logger.error("Все попытки исчерпаны")

        return None
