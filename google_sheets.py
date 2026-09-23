import gspread

from logger import logger


class GoogleSheetsClient:
    """
    Клиент для работы с Google Sheets.
    Отвечает за загрузку агрегированного отчёта.
    """

    def __init__(self):
        self.gc = gspread.service_account(
            filename="credentials/google_service_account.json"
        )
        self.spreadsheet = self.gc.open_by_key(
            "1R9rf82SZzekYtCUcLI3sh_YGspsWkAeI2wruYAuYfOM"
        )
        self.worksheet = self.spreadsheet.sheet1

    def upload(self, report):
        """
        Загружает агрегированный отчёт в Google Sheets.

        Ошибка внешнего сервиса фиксируется в логе,
        но не прерывает основной ETL-процесс.
        """
        row = [
            report["period"],
            report["total_attempts"],
            report["run_attempts"],
            report["submit_attempts"],
            report["successful_submits"],
            report["failed_submits"],
            report["unique_users"],
            report["success_rate"],
        ]

        try:
            self.worksheet.append_row(row)
            return True
        except Exception as err:
            logger.error(f"Ошибка загрузки отчёта в Google Sheets: {err}")
            return False
