import psycopg2

from config import DB_PASSWORD


def get_connection():
    """Создаёт и возвращает соединение с PostgreSQL."""
    return psycopg2.connect(
        database="online_university_etl",
        user="postgres",
        password=DB_PASSWORD,
        host="localhost",
        port="5432",
    )
