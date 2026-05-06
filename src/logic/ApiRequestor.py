# ApiRequestor.py
import time

import requests
import urllib.parse

# import streamlit as st

from logic.AppLogger import AppLogger


class ApiRequestor:
    def __init__(self):
        self.session = requests.Session()
        # self.logger = logging.getLogger(__name__)
        self.api_logger = AppLogger(__name__)

    def send_request(self, url, method, headers=None, body=None, timeout=30):
        """
        汎用的なAPIリクエストメソッド
        APIリクエストを送信し、429エラー時にリトライを行う。
        :param url: APIエンドポイント
        :param method: HTTPメソッド (GET, POST, PUT, DELETE)
        :param headers: リクエストヘッダー (辞書形式)
        :param body: リクエストボディ (辞書形式)
        :param timeout: リクエストタイムアウト (ディフォルト 30秒)
        :return: レスポンスオブジェクトまたはエラーメッセージ
        """
        max_retries = 3
        retry_wait = 30  # 秒

        # メソッド開始時のログ
        self.api_logger.api_start_log(url, method, headers, body)
        for attempt in range(max_retries + 1):
            try:

                # 一般的にリクエストボディを持つのは POST, PUT, PATCH です
                has_body = method in ["POST", "PUT", "PATCH"]
                # 全メソッド共通で1つのリクエスト文に集約可能
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body if has_body else None,
                    timeout=timeout,  # 引数で受け取った値を使用
                )

                # ステータスコードが 429 の場合の処理
                if response.status_code == 429:
                    if attempt < max_retries:
                        self.api_logger.info_log(
                            f"Status 429. Retrying in {retry_wait}s... "
                            f"(Attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(retry_wait)
                        continue
                    else:
                        self.api_logger.error_log(
                            "Max retries reached for status 429."
                        )

                # 429以外、またはリトライ上限に達した場合はレスポンスを返す
                # ステータスコードチェック
                response.raise_for_status()
                # メソッド終了時のログ
                self.api_logger.api_success_log(response)
                # レスポンス解析
                return response

            except requests.exceptions.HTTPError as http_err:
                # HTTPエラー時のログ
                self.api_logger.error_log(f"HTTP error occurred: {http_err}")

                # HTTPエラー時の処理
                err_msg = ""
                err_msg += f"HTTPエラー: {http_err}\n"
                if hasattr(http_err.response, "status_code"):
                    err_msg += (
                        f"ステータスコード: {http_err.response.status_code}\n"
                    )
                    err_msg += f"理由: {http_err.response.reason}\n"
                    err_msg += f"詳細: {http_err.response.json()}"

                # 文字列ではなく、Exceptionとして投げる（または元のhttp_errを再送出する）
                raise Exception(err_msg) from http_err

            except requests.exceptions.RequestException as req_err:
                # その他のリクエストエラー時のログ
                self.api_logger.error_log(f"Request error occurred: {req_err}")
                raise

            except Exception as e:
                # その他例外発生時のログ
                self.api_logger.error_log(f"An unexpected error occurred: {e}")
                raise

    def send_api_request(
        self,
        uri,
        method,
        config_file,
        num_inputs=0,
        user_inputs=None,
        messages=None,
    ):
        """
        API呼び出しの高レベルラッパー関数
        :param uri: APIエンドポイント
        :param method: HTTPメソッド
        :param config_file: 設定ファイルパス
        :param num_inputs: ユーザー入力の数
        :param user_inputs: ユーザー入力 {user_input_0: "xxx", ...}
        :param messages: メッセージリスト [{"role": "user", "content": "..."}, ...]
        :return: レスポンスオブジェクト
        """
        if not config_file:
            raise ValueError("config_file must be specified")

        headers = {"Content-Type": "application/json"}
        body = {
            "config_file": config_file,
            "num_user_inputs": num_inputs,
            "user_inputs": user_inputs or {},
            "messages": messages or [],
        }

        response = self.send_request(uri, method, headers, body)
        response.raise_for_status()
        return response

    def replace_uri(self, session_state, uri):
        replaced_uri = uri
        for i in range(session_state["num_inputs"]):
            key = f"user_input_{i}"
            value = urllib.parse.quote(session_state[f"user_input_{i}"])
            replaced_uri = replaced_uri.replace(f"＜{key}＞", value)

        return replaced_uri

    def replace_body(self, session_state, body):
        replaced_body = body
        for i in range(session_state["num_inputs"]):
            key = f"user_input_{i}"
            value = session_state[f"user_input_{i}"].replace('"', "'")
            replaced_body = replaced_body.replace(f"＜{key}＞", value)

        return replaced_body
