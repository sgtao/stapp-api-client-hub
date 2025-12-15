# create_api_request.py
import json
import os

from fastapi import Request, HTTPException
import pandas as pd

from logic.ApiRequestor import ApiRequestor

from logic.utils.read_yaml_file import read_yaml_file
from logic.utils.convert_config_to_header import convert_config_to_header


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
    if "session_state" not in config:
        return session_state

    cfg_session_state = config.get("session_state", {})
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


async def create_api_request(request: Request):
    """
    リクエストからAPIリクエストの情報を抽出します。
    :param request: FastAPIのRequestオブジェクト
    :return: APIリクエストの情報 (辞書形式)
    """
    # --- 1. リクエストと設定読み込み ---
    api_request = {}
    try:
        body_data = await request.json()
        # api_logger.debug_log(f"request body: {body_data}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    num_user_inputs = body_data.get("num_user_inputs", 0)
    user_inputs = body_data.get("user_inputs", {})

    config_file_path = body_data.get("config_file")
    if not config_file_path:
        raise HTTPException(status_code=400, detail="Missing 'config_file'")
    config_data = read_yaml_file(config_file_path)
    config_data["api_key"] = get_apikey()
    session_state = make_session_state(config_data)
    # print(f"session_state: {session_state}")
    session_state["num_inputs"] = num_user_inputs
    for i in range(num_user_inputs):
        session_state[f"user_input_{i}"] = user_inputs.get(
            f"user_input_{i}", ""
        )

    api_url = session_state["uri"]
    method = session_state["method"]
    headers = convert_config_to_header(session_state)
    req_body = session_state.get("req_body", {}) if method != "GET" else {}
    # print(f"Original req_body: {req_body}")

    if session_state.get("use_dynamic_inputs", False):
        api_requestor = ApiRequestor()
        api_url = api_requestor.replace_uri(session_state, api_url)
        replaced = replace_body(session_state, json.dumps(req_body))

        if isinstance(replaced, str):
            # JSON文字列ならパース
            req_body = json.loads(replaced)
        elif isinstance(replaced, dict):
            # 既にdictならそのまま
            req_body = replaced
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected type from replace_body: {type(replaced)}",
            )

        # print(f"Replaced req_body: {req_body}")

    api_request = {
        "url": api_url,
        "method": method,
        "headers": headers,
        "req_body": req_body,
        "response_path": session_state.get("user_property_path"),
    }

    return api_request
