import ast
from datetime import datetime

from logger import logger

required_fields = [
    "lti_user_id",
    "passback_params",
    "is_correct",
    "attempt_type",
    "created_at",
]


def validate_data(data):
    """
    Проверяет и частично преобразует данные, полученные от API.

    Возвращает:
        list — записи, прошедшие валидацию;
        [] — если API вернул пустой список;
        None — если структура данных некорректна
        или ни одна запись не прошла валидацию.
    """
    if not isinstance(data, list):
        logger.warning("Некорректная структура данных: ожидался список записей.")
        return None

    if not data:
        return []

    valid_data = []

    for record in data:
        if not isinstance(record, dict):
            logger.warning("Некорректная запись имеет неверный тип и была пропущена.")
            continue

        for field in required_fields:
            if field not in record:
                logger.warning(f"В записи отсутствует обязательное поле: {field}")
                break
        else:
            lti_user_id = record["lti_user_id"]

            if not isinstance(lti_user_id, str):
                logger.warning(
                    f"Некорректный тип данных lti_user_id: "
                    f"значение = '{lti_user_id}', "
                    f"тип = {type(lti_user_id)}"
                )
                continue

            if not lti_user_id:
                logger.warning("Некорректное значение lti_user_id: строка пустая.")
                continue

            passback_params = record["passback_params"]

            if not isinstance(passback_params, str):
                logger.warning(
                    "Некорректный тип данных passback_params: ожидалась строка."
                )
                continue

            try:
                # literal_eval безопасно преобразует строковое
                # представление Python-объекта без выполнения произвольного кода.
                passback_params = ast.literal_eval(passback_params)
            except (ValueError, SyntaxError):
                logger.warning(
                    "Некорректное содержимое passback_params: "
                    "не удалось преобразовать строку."
                )
                continue

            if not isinstance(passback_params, dict):
                logger.warning(
                    "Некорректный тип данных passback_params: ожидался словарь."
                )
                continue

            oauth_consumer_key = passback_params.get("oauth_consumer_key")
            if oauth_consumer_key is not None and not isinstance(
                oauth_consumer_key, str
            ):
                logger.warning(
                    "Некорректный тип данных oauth_consumer_key: ожидалась строка."
                )
                continue

            lis_result_sourcedid = passback_params.get("lis_result_sourcedid")
            if lis_result_sourcedid is not None and not isinstance(
                lis_result_sourcedid, str
            ):
                logger.warning(
                    "Некорректный тип данных lis_result_sourcedid: ожидалась строка."
                )
                continue

            lis_outcome_service_url = passback_params.get("lis_outcome_service_url")
            if lis_outcome_service_url is not None and not isinstance(
                lis_outcome_service_url, str
            ):
                logger.warning(
                    "Некорректный тип данных lis_outcome_service_url: ожидалась строка."
                )
                continue

            attempt_type = record["attempt_type"]

            if not isinstance(attempt_type, str):
                logger.warning(
                    "Некорректный тип данных attempt_type: ожидалась строка."
                )
                continue

            if attempt_type not in ("run", "submit"):
                logger.warning(
                    "Некорректное значение attempt_type: ожидалось 'run' или 'submit'."
                )
                continue

            is_correct = record["is_correct"]

            # Для запуска кода результат проверки отсутствует,
            # для отправки решения API передаёт 0 или 1.
            if attempt_type == "run" and is_correct is not None:
                logger.warning(
                    "Некорректное значение is_correct: "
                    "для attempt_type 'run' ожидалось None."
                )
                continue

            if attempt_type == "submit" and is_correct not in (0, 1):
                logger.warning("Некорректное значение is_correct: ожидалось 0 или 1.")
                continue

            if attempt_type == "submit":
                record["is_correct"] = bool(is_correct)

            created_at = record["created_at"]

            if not isinstance(created_at, str):
                logger.warning("Некорректный тип данных created_at: ожидалась строка.")
                continue

            try:
                datetime.strptime(
                    created_at,
                    "%Y-%m-%d %H:%M:%S.%f",
                )
            except ValueError:
                logger.warning(
                    "Некорректное значение created_at: "
                    "ожидался формат YYYY-MM-DD HH:MM:SS.ffffff."
                )
                continue

            # Извлекаем параметры LTI в отдельные поля,
            # которые используются при загрузке в PostgreSQL.
            record["oauth_consumer_key"] = oauth_consumer_key
            record["lis_result_sourcedid"] = lis_result_sourcedid
            record["lis_outcome_service_url"] = lis_outcome_service_url

            del record["passback_params"]

            valid_data.append(record)

    if not valid_data:
        logger.warning("Все полученные записи не прошли валидацию.")
        return None

    return valid_data
