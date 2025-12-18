# hello.py
import platform
import sys
import yaml

from fastapi import APIRouter, Request
from logic.AppLogger import AppLogger


APP_NAME = "api_server"
router = APIRouter(tags=["Config"])


def dict_to_yaml(data: dict, style: str = "block") -> str:
    """
    Python辞書をYAML形式の文字列に変換するヘルパー関数

    Args:
        data: 変換する辞書データ
        style: 出力スタイル（"block" or "flow"）
            - "block": 改行あり、読みやすい形式（デフォルト）
            - "flow": 1行形式、コンパクト

    Returns:
        YAML形式の文字列
    """
    return yaml.dump(
        data,
        allow_unicode=True,
        default_flow_style=(style == "flow"),
        indent=2,
        sort_keys=False,
    )


@router.get("/hello")
@router.post("/hello")
async def hello(request: Request):
    """
    GETとPOSTメソッドで`/api/v0/hello`エンドポイントにアクセスすると、
    JSON形式で`{"results": "hello"}`を返します。
    """
    api_logger = AppLogger(APP_NAME)
    api_logger.info_log(f"{request.url.path} Receive {request.method}")

    # app.stateからポート番号を取得
    port = request.app.state.port

    # Pythonバージョンの取得
    _python_version = (
        f"{sys.version_info.major}."
        f"{sys.version_info.minor}."
        f"{sys.version_info.micro}"
    )

    # サーバー情報の構築
    server_info = {
        "server_info": {
            "port": port,
            "host": request.client.host if request.client else "unknown",
            "method": request.method,
            "path": request.url.path,
            "python_version": _python_version,
            "platform": platform.system(),
            "app_version": request.app.version,
        }
    }
    # YAML形式への変換
    server_info_yaml = dict_to_yaml(server_info)
    api_logger.info_log(f"server_info :\n{server_info_yaml}")

    return {"results": f"hello from {port}"}
