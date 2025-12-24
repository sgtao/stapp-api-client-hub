# ApiClientLog.py
from logic.AppLogger import AppLogger

APP_TITLE = "ApiClientLog"


class ApiClientLog:
    def __init__(self, logger: AppLogger = None):
        self.logger = logger or AppLogger(APP_TITLE)

    def show_error_ui(self, message):
        """メッセージをログ"""
        self.logger.error_log(message)

    def show_warning_ui(self, message):
        """メッセージをログ"""
        self.logger.info_log(f"WARNING: {message}")

    def show_info_ui(self, message):
        """メッセージをログ"""
        self.logger.info_log(message)

    def show_success_ui(
        self,
        message,
        uri="",
        response=None,
    ):
        """成功時のログ"""
        self.logger.info_log(f"Request {uri} Success of {message}.")
        if response is not None:
            self.logger.api_success_log(response)
