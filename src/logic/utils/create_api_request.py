# create_api_request.py
import json
import os

from fastapi import Request, HTTPException
import pandas as pd

from logic.ApiRequestor import ApiRequestor
from logic.AppLogger import AppLogger
from logic.utils.read_yaml_file import read_yaml_file
from logic.utils.convert_config_to_header import convert_config_to_header

APP_NAME = "create_api_request"


def get_apikey():
    # API-KEYの確認
    if os.getenv("API_KEY"):
        return os.getenv("API_KEY")
    else:
        return ""


def replace_body(session_state, body_str):

    body = json.loads(body_str)

    def replace_value(obj):
        if isinstance(obj, dict):
            return {k: replace_value(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_value(v) for v in obj]
        elif isinstance(obj, str):
            # {user_input_0} のようなプレースホルダ置換
            for k, v in session_state.items():
                obj = obj.replace(f"{{{k}}}", str(v))

            # ＜user_input_0＞ のような全角プレースホルダ置換
            num_inputs = session_state.get("num_inputs", 0)
            for i in range(num_inputs):
                key = f"user_input_{i}"
                value = str(session_state.get(key, "")).replace('"', "'")
                obj = obj.replace(f"＜{key}＞", value)

            return obj
        else:
            return obj

    return replace_value(body)


def make_session_state(config):
    session_state = {}
    cfg_session_state = {}
    if "session_state" in config:
        cfg_session_state = config.get("session_state", {})
    elif "single_config" in config:
        cfg_session_state = config.get("single_config", {})
    else:
        return session_state

    if "method" in cfg_session_state:
        session_state["method"] = cfg_session_state.get("method")
    if "uri" in cfg_session_state:
        session_state["uri"] = cfg_session_state.get("uri")

    if "header_df" in cfg_session_state:
        get_header = cfg_session_state.get("header_df")
        header_list = []
        for header_item in get_header:
            auth_value = header_item["Value"].replace(
                "＜API_KEY＞", config.get("api_key", "")
            )
            header_list.append(
                {
                    "Property": header_item["Property"],
                    "Value": auth_value,
                }
            )
        header_df = pd.DataFrame(header_list)
        session_state["header_df"] = header_df

    if "req_body" in cfg_session_state:
        _req_body = cfg_session_state.get("req_body")
        if isinstance(_req_body, str):
            try:
                # JSON文字列を辞書に変換
                session_state["req_body"] = json.loads(_req_body)
            except json.JSONDecodeError:
                # JSONでなければそのままラップして保持
                session_state["req_body"] = {"raw": _req_body}
        else:
            # すでにdictやlistならそのまま使う
            session_state["req_body"] = _req_body

    session_state["use_dynamic_inputs"] = (
        cfg_session_state.get("use_dynamic_inputs") != "false"
    )

    if "user_property_path" in cfg_session_state:
        session_state["user_property_path"] = cfg_session_state.get(
            "user_property_path"
        )

    return session_state


async def create_api_request(request: Request, use_messages=True):
    """
    リクエストからAPIリクエストの情報を抽出します。
    """
    api_logger = AppLogger(f"{APP_NAME}({request.url.path}):")
    api_logger.info_log(f"Create API Request of {request.method}")

    try:
        body_data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    try:
        # construct_request_from_body 内で例外が発生しても適切に上位へ伝える
        return construct_request_from_body(body_data, use_messages)
    except Exception as e:
        # 元の例外が HTTPException ならそのまま、それ以外なら 500 でラップ
        if isinstance(e, HTTPException):
            raise e
        api_logger.error_log(f"Internal Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def construct_request_from_body(body_data, use_messages=True):
    # --- 1. 設定の読み込みとセッション構築 ---
    config_file_path = body_data.get("config_file")
    if not config_file_path:
        raise HTTPException(status_code=400, detail="Missing 'config_file'")

    config_data = read_yaml_file(config_file_path)
    config_data["api_key"] = get_apikey()

    session_state = make_session_state(config_data)

    # ユーザー入力の動的マッピング
    num_user_inputs = body_data.get("num_user_inputs", 0)
    user_inputs = body_data.get("user_inputs", {})
    session_state["num_inputs"] = num_user_inputs

    for i in range(num_user_inputs):
        key = f"user_input_{i}"
        session_state[key] = user_inputs.get(key, "")

    # 必須項目のチェック（KeyError防止）
    api_url = session_state.get("uri")
    method = session_state.get("method", "POST")
    if not api_url:
        raise HTTPException(
            status_code=500, detail="API URI is not defined in config"
        )

    headers = convert_config_to_header(session_state)

    # --- 2. リクエストボディの組み立て ---
    # 元の req_body を破壊しないよう、新しいリストとしてメッセージを結合
    base_req_body = (
        session_state.get("req_body", {}) if method != "GET" else {}
    )

    # メッセージの結合（元のリストを汚染しない手法）
    current_messages = list(base_req_body.get("messages", []))  # コピーを作成
    if use_messages:
        input_messages = body_data.get("messages", [])
        combined_messages = current_messages + input_messages
    else:
        combined_messages = current_messages

    # ボディの作成（shallow copy）
    req_body = {**base_req_body, "messages": combined_messages}

    # --- 3. 動的入力の置換処理 ---
    if session_state.get("use_dynamic_inputs", False):
        api_requestor = ApiRequestor()
        api_url = api_requestor.replace_uri(session_state, api_url)

        # 辞書のまま渡すか、必要ならここでdumpsする
        replaced = replace_body(session_state, json.dumps(req_body))

        if isinstance(replaced, str):
            req_body = json.loads(replaced)
        elif isinstance(replaced, dict):
            req_body = replaced
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected type from replace_body: {type(replaced)}",
            )

    return {
        "url": api_url,
        "method": method,
        "headers": headers,
        "req_body": req_body,
        "response_path": session_state.get("user_property_path"),
    }
