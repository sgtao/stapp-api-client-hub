# message_controller.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from logic.AppLogger import AppLogger
from logic.LlmAPI import LlmAPI
from logic.utils.create_api_request import create_api_request

APP_NAME = "api_server"
router = APIRouter(tags=["Messages"])


async def process_llm_request(request: Request):
    api_logger = AppLogger(f"{APP_NAME}(process_llm_rqeuests):")
    # --- 1. リクエストと設定読み込み ---
    try:
        messages = []
        api_request = await create_api_request(request)
        if api_request["method"] == "GET":
            api_logger.info_log("cannot support to GET request")
            raise HTTPException(
                status_code=400, detail="cannot support to GET request"
            )
        # get message from request
        body_data = await request.json()
        messages = body_data.get("messages")

    except Exception as e:
        api_logger.error_log(f"APIリクエスト作成失敗: {e}")
        raise HTTPException(
            status_code=400, detail=f"APIリクエスト作成失敗: {e}"
        )

    if not messages:
        raise HTTPException(
            status_code=400, detail="messages not found in request body"
        )

    # --- 2. LlmAPIを使った変換とリクエスト ---
    try:
        llm = LlmAPI(
            # uri=sent_uri,
            uri=api_request["url"],
            header_dict=api_request["headers"],
            req_body=api_request["req_body"],
            user_property_path=api_request["response_path"],
        )

        # send message:
        response = llm.single_response(messages)

        # 結果の返却
        return JSONResponse(content={"results": response})

    except Exception as e:
        api_logger.error_log(f"APIリクエスト失敗: {e}")
        raise HTTPException(status_code=502, detail=f"APIリクエスト失敗: {e}")


@router.post("/messages")
async def post_messages(request: Request):
    """
    messagesを含むリクエストを受け取り、
    config_file で指定したAPIを実行し、
    JSON形式で`{"results": [user_property value]}`を返します。
    """
    # --- 1. Logger setting and Instanciation ---
    api_logger = AppLogger(f"{APP_NAME}({request.url.path}):")
    api_logger.info_log(f"Receive {request.method}")

    # --- 2. LlmAPIを使った変換とリクエスト ---
    try:
        return await process_llm_request(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
