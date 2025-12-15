# echo_controller.py
# import json

from fastapi import APIRouter, Request, HTTPException

from logic.AppLogger import AppLogger

from logic.ResponseOperator import ResponseOperator

APP_NAME = "api_server"
router = APIRouter(tags=["Service"])


async def extract_speified_path(target, response_path=None):
    """
    `target`から`response_path`の指定プロパティを抽出する
    :param target: 変換対象のオブジェクト
    :param response_path: パス (文字列)
    :return: レスポンスオブジェクト
    """
    api_logger = AppLogger(APP_NAME)
    api_logger.info_log(f"target(type:{type(target)}): {target}")
    api_logger.info_log(f"response path: {response_path}")
    response_op = ResponseOperator()
    # target_json = target.json()
    # result = target_json
    result = None
    if response_path is None or response_path == ".":
        result = target
    else:
        result = response_op.extract_property_from_json(target, response_path)
    api_logger.info_log(f"Return API response result: {result}")

    return {"results": result}


@router.post("/echo_target")
async def execute_service(request: Request):
    """
    リクエストボディの`target`から、`response_path`で指定した位置を抽出
    JSON形式で`{"results": [user_property value]}`を返します。
    """
    # --- 1. Logger setting and Instanciation ---
    api_logger = AppLogger(f"{APP_NAME}({request.url.path}):")
    api_logger.info_log(f"Receive {request.method}")

    # --- 2. リクエストと設定読み込み ---
    try:
        body_data = await request.json()
        api_logger.info_log(f"Receive body {body_data}")
        target = body_data.get("target", {})
        response_path = body_data.get("response_path", ".")
        return await extract_speified_path(target, response_path)
    except Exception as e:
        api_logger.error_log(f"API request is failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
