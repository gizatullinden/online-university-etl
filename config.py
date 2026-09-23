import os

from dotenv import load_dotenv


load_dotenv()

API_URL = "https://b2b.itresume.ru/api/statistics"
CLIENT_KEY = os.getenv("CLIENT_KEY")
CLIENT = "Skillfactory"

DB_PASSWORD = os.getenv("DB_PASSWORD")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
