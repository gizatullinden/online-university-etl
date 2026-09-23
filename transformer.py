from datetime import datetime


def transform_data(data):
    """
    Преобразует валидированные данные к формату,
    необходимому для загрузки в PostgreSQL.

    На входе:
        data — список записей, прошедших валидацию.

    На выходе:
        список преобразованных записей.
    """
    transformed_data = []

    for record in data:
        user_id = record.pop("lti_user_id")
        record["user_id"] = user_id

        record["created_at"] = datetime.strptime(
            record["created_at"],
            "%Y-%m-%d %H:%M:%S.%f",
        )

        transformed_data.append(record)

    return transformed_data
