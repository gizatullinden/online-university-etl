import psycopg2

from database import get_connection
from logger import logger


def load_data(data):
    """Загружает преобразованные данные в PostgreSQL."""
    conn = get_connection()
    cursor = conn.cursor()

    loaded_count = 0
    error_count = 0

    try:
        for record in data:
            try:
                # SAVEPOINT позволяет откатить только текущую запись,
                # не прерывая загрузку остальных данных.
                cursor.execute("SAVEPOINT record_savepoint")

                cursor.execute(
                    """
                    INSERT INTO code_attempts(
                        user_id,
                        oauth_consumer_key,
                        lis_result_sourcedid,
                        lis_outcome_service_url,
                        is_correct,
                        attempt_type,
                        created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        record["user_id"],
                        record["oauth_consumer_key"],
                        record["lis_result_sourcedid"],
                        record["lis_outcome_service_url"],
                        record["is_correct"],
                        record["attempt_type"],
                        record["created_at"],
                    ),
                )

                loaded_count += 1

            except psycopg2.Error as err:
                error_count += 1
                logger.error(f"Ошибка записи: {err}")

                cursor.execute("ROLLBACK TO SAVEPOINT record_savepoint")

        try:
            conn.commit()

        except psycopg2.Error as err:
            # При ошибке COMMIT откатываем всю транзакцию.
            conn.rollback()
            logger.error(f"Ошибка фиксации транзакции: {err}")
            raise

        logger.info(
            f"Загрузка завершена. "
            f"Успешно загружено: {loaded_count}, "
            f"ошибок: {error_count}."
        )

    finally:
        cursor.close()
        conn.close()
