# single_controller.py
# import json

from fastapi import APIRouter, Request, HTTPException

from logic.AppLogger import AppLogger

from logic.utils.create_api_request import create_api_request
from logic.utils.send_api_request import send_api_request

APP_NAME = "api_server"
router = APIRouter(tags=["Service"])


@router.post("/single")
async def single_controller(request: Request):
    """
    リクエストを受け取り、config_file で指定したAPIを実行し、
    JSON形式で`{"results": [user_property value]}`を返します。
    """
    # --- 1. Logger setting and Instanciation ---
    api_logger = AppLogger(f"{APP_NAME}({request.url.path}):")
    api_logger.info_log(f"Receive {request.method}")

    try:
        api_request = await create_api_request(request)
        api_logger.info_log(f"API Client Request is {api_request}")
        # api_logger.info_log(f"API request URI: {api_request.url.path}")
        return await send_api_request(**api_request)
    except Exception as e:
        api_logger.error_log(f"API request is failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
