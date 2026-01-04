# action_controller.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from logic.AppLogger import AppLogger
from logic.ChatService import ChatService

APP_NAME = "api_server"
router = APIRouter(tags=["Messages"])


@router.post("/actions")
async def post_messages(request: Request):
    """
    messagesを含むリクエストを受け取り、
    config_file で指定したAPIを実行し、実行経過・実行結果を
    JSON形式で返します。
    """
    # --- 1. Logger setting and Instanciation ---
    api_logger = AppLogger(f"{APP_NAME}({request.url.path}):")
    api_logger.info_log(f"Receive {request.method}")

    chat_service = ChatService()

    # --- 2. ChatServiceを使った変換とリクエスト ---
    try:
        results = await chat_service.process_message_request(request)
        # response = results[-1] if results else None

        # 結果の返却
        return JSONResponse(content={"results": results})

    except Exception as e:
        api_logger.error_log(f"APIリクエスト失敗: {e}")
        raise HTTPException(status_code=400, detail=str(e))
