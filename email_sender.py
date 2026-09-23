import smtplib
import ssl
from email.message import EmailMessage

from config import (
    EMAIL_PASSWORD,
    EMAIL_RECIPIENT,
    EMAIL_SENDER,
    SMTP_PORT,
    SMTP_SERVER,
)
from logger import logger


class EmailSender:
    """
    Отправляет уведомления с результатами ETL-процесса.
    """

    def send(self, report):
        """
        Формирует и отправляет письмо с результатами ETL-процесса.
        """
        msg = EmailMessage()

        message = (
            "ETL-процесс завершён успешно.\n\n"
            f"Период (period): {report['period']}\n"
            f"Всего попыток (total_attempts): {report['total_attempts']}\n"
            f"Запусков кода (run_attempts): {report['run_attempts']}\n"
            f"Отправок решений (submit_attempts): {report['submit_attempts']}\n"
            f"Успешных решений (successful_submits): {report['successful_submits']}\n"
            f"Неуспешных решений (failed_submits): {report['failed_submits']}\n"
            f"Уникальных пользователей (unique_users): {report['unique_users']}\n"
            f"Процент успешных решений (success_rate): "
            f"{report['success_rate']:.2f}%\n"
        )

        msg.set_content(message)
        msg["Subject"] = "Результат ETL-процесса"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECIPIENT

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL(
                SMTP_SERVER,
                SMTP_PORT,
                context=context,
            ) as server:
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)

            logger.info("Email с результатами ETL-процесса успешно отправлен.")

        except (smtplib.SMTPException, OSError) as err:
            logger.error(f"Ошибка отправки email: {err}")
