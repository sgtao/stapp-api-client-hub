# hello.py
from fastapi import APIRouter, Request
from logic.AppLogger import AppLogger


APP_NAME = "api_server"
router = APIRouter(tags=["Config"])


@router.get("/hello")
@router.post("/hello")
async def hello(request: Request):
    """
    GETとPOSTメソッドで`/api/v0/hello`エンドポイントにアクセスすると、
    JSON形式で`{"results": "hello"}`を返します。
    """
    api_logger = AppLogger(APP_NAME)
    api_logger.info_log(f"{request.url.path} Receive {request.method}")
    return {"results": "hello"}
