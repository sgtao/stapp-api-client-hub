# ChatService.py
import json
import os

from fastapi import Request, HTTPException

if os.getenv("LOCAL_USE_STREAMLIT", "0") == "1":
    from components.ApiClient import ApiClient
else:
    from logic.utils.ApiClientLog import ApiClientLog as ApiClient

from logic.ApiClientCore import ApiClientCore
from logic.AppLogger import AppLogger
from logic.ClientConfigManager import ClientConfigManager
from logic.ResponseOperator import ResponseOperator
from logic.utils.read_yaml_file import read_yaml_file
from logic.utils.create_api_request import create_api_request
from logic.utils.send_api_request import send_api_request

APP_TITLE = "ChatService"


class ChatService:
    """
    ChatService クラスは、設定情報・セッション状態・メッセージ群をもとに
    一連の API リクエストやレスポンス抽出を順次実行する統括サービスです。

    各アクションの種類（"request" または "extract"）に応じて
    適切な処理を行い、結果を蓄積・ログ出力・UI表示します。
    """

    def __init__(self):
        self.app_logger = AppLogger(APP_TITLE)
        # instanciation using logic
        self.config_mgr = ClientConfigManager()
        self.client = ApiClientCore(self.app_logger)
        self.response_op = ResponseOperator()
        self.api_client_comp = ApiClient()
        self.use_streamlit = True

    def get_apikey(self):
        # API-KEYの確認
        if os.getenv("API_KEY"):
            return os.getenv("API_KEY")
        else:
            return ""

    def read_action_config(self, config_file_path):
        config_data = read_yaml_file(config_file_path)
        config_data["api_key"] = self.get_apikey()
        action_configs = []
        if "session_state" in config_data:
            action_configs.append({"type": "single"})
        if "single_config" in config_data:
            action_configs.append({"type": "single"})
        if "action_state" in config_data:
            action_configs = config_data.get("action_state", [])
        if "action_config" in config_data:
            action_configs = config_data.get("action_config", [])

        return action_configs

    def prepare_post_data(self, body_data):
        """
        クライアントから渡されたリクエストボディ (`body_data`) を解析し、
        API呼び出しに必要な構造化データを生成します。

        Parameters
        ----------
        body_data : dict
            クライアントリクエストの本文。以下のキーを含む想定:
                - config_file : str  設定ファイルのパス
                - num_user_inputs : int  入力数
                - user_inputs : dict  入力データの辞書
                - messages : list  APIへ送信するメッセージ群

        Returns
        -------
        dict
            API呼び出し処理用の辞書オブジェクト。
            {
                "action_configs": list,
                "session_state": dict,
                "messages": list
            }

        """
        config_file_path = body_data.get("config_file")
        if not config_file_path:
            raise HTTPException(
                status_code=400, detail="Missing 'config_file'"
            )
        # config_data = read_yaml_file(config_file_path)

        # print(f"config_data: {config_data}")

        action_configs = self.read_action_config(config_file_path)

        session_state = {}
        num_user_inputs = body_data.get("num_user_inputs", 0)
        user_inputs = body_data.get("user_inputs", {})
        session_state["num_inputs"] = num_user_inputs
        for i in range(num_user_inputs):
            session_state[f"user_input_{i}"] = user_inputs.get(
                f"user_input_{i}", ""
            )

        messages = body_data.get("messages")

        post_data = {
            "action_configs": action_configs,
            "session_state": session_state,
            "messages": messages,
        }
        return post_data

    def convert_messages_obj(self, messages):
        return {"messages": messages}

    def post_messages_with_configs(
        self,
        messages,
        session_state,
        action_configs,
    ):
        """
        複数のアクション設定を順に処理し、APIリクエストまたはデータ抽出を実行します。

        各アクション設定 (`action_configs`) の "type" に応じて以下を行います:
            - "request": 設定に基づいてAPIをPOSTし、レスポンスを解析。
            - "extract": JSON文字列から指定パスの値を抽出。

        Parameters
        ----------
        messages : list
            送信するメッセージ群（リクエスト本文に相当）。
        session_state : dict
            セッション中の状態情報（動的置換に利用）。
        action_configs : list[dict]
            各アクションの設定情報。type, uri, config_fileなどを含む。

        Returns
        -------
        Any
            最終アクションの結果（成功・抽出結果・または None）。

        Raises
        ------
        Exception
            各アクションの実行中に発生した例外（ログ出力と警告UIを伴う）。
        """
        self.app_logger.info_log(f"post message: {messages}")
        self.app_logger.info_log(f"with config: {action_configs}")

        results = []
        result = ""

        for index, cfg in enumerate(action_configs):
            # print(cfg)
            _type = cfg.get("type", "request")

            if _type == "request":
                try:
                    action_config = self.config_mgr.replace_action_config(
                        session_state, cfg, results
                    )
                    # print(action_config)
                    config_file = action_config.get("config_file", "")
                    uri = action_config.get("uri")

                    response = self.client.post_msgs_with_config(
                        config=action_config,
                        messages=messages,
                    )
                    result = self.response_op.extract_response_value(
                        response,
                        path=action_config.get("user_property_path", "."),
                    )

                    self.api_client_comp.show_success_ui(
                        f"Success Request of {config_file} is {result}.",
                        uri=uri,
                        response=response,
                    )

                except Exception:
                    result = response.json()
                    self.api_client_comp.show_warning_ui(
                        f"Exception occured at {config_file}",
                    )
            elif _type == "extract":
                action_config = self.config_mgr.replace_extract_config(
                    session_state=session_state,
                    action_config=cfg,
                    results=results,
                )
                if action_config.get("target", "") == "messages":
                    target_obj = self.convert_messages_obj(messages)
                else:
                    _target_text = action_config.get("target", "")
                    # print(f"_target_text: {_target_text}")
                    target_obj = json.loads(_target_text)

                # print(f"_target_obj: {_target_obj}")
                user_property_path = action_config.get(
                    "user_property_path", "."
                )
                # print(f"user_property_path: {user_property_path}")
                try:
                    result = self.response_op.extract_property_from_json(
                        json_data=target_obj,
                        property_path=user_property_path,
                    )
                    self.api_client_comp.show_success_ui(
                        f"Success to extract is {result}.",
                    )
                except Exception:
                    result = target_obj
                    self.api_client_comp.show_warning_ui(
                        f"Exception occured at extract, so set {result}",
                    )

            else:
                result = "Nothing!"

            self.app_logger.info_log(f"Action result_{index}: {result}")
            results.append(result)

        # return results[-1] if results else None
        return results

    async def process_message_request(self, request: Request):
        self.use_streamlit = False
        # --- 1. リクエストと設定読み込み ---
        try:
            body_data = await request.json()
            # api_logger.debug_log(f"request body: {body_data}")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")

        try:

            # print(f"body_data: {body_data}")

            post_data = self.prepare_post_data(body_data)
            session_state = post_data["session_state"]
            messages = post_data["messages"]
            action_configs = post_data["action_configs"]

            # print(f"action_config: {action_configs}")

        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"APIリクエスト作成失敗: {e}"
            )

        if not messages:
            raise HTTPException(
                status_code=400, detail="messages not found in request body"
            )

        # --- 2. single相当のリクエスト(`session_state`付きconfigの場合) ---
        _type = action_configs[0].get("type", "")
        if _type == "single":
            results = []
            try:
                api_request = await create_api_request(request)
                result = await send_api_request(**api_request)
                results.append(result)
                return results
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        # --- 3. ChatServiceを使ったリクエスト ---
        try:
            # send message:
            results = self.post_messages_with_configs(
                session_state=session_state,
                messages=messages,
                action_configs=action_configs,
            )
            return results
        except Exception as e:
            raise HTTPException(
                status_code=502, detail=f"APIリクエスト失敗: {e}"
            )
