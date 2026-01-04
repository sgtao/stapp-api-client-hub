# config_controller.py
import json

from fastapi import APIRouter, Request, HTTPException

from ui.ConfigFiles import ConfigFiles
from logic.AppLogger import AppLogger
from logic.utils.read_yaml_file import read_yaml_file

APP_NAME = "api_server"
router = APIRouter(tags=["Config"])

# def get_config_list():
#     # assets/privatesフォルダからyamlファイルを選択
#     config_files = ConfigFiles()
#     return config_files.get_config_files_list()
# src/api/v0/config_controller.py
def get_config_list(config_mode = "default"):
    # config_mode = getattr(request.app.state, "config_mode", "default")
    config_files = ConfigFiles(config_mode=config_mode)
    return config_files.get_config_files_list()


def get_config_title(config_file_path: str):
    config_data = read_yaml_file(config_file_path)
    return {"title": config_data.get("title"), "note": config_data.get("note")}


@router.get("/configs")
async def configs(request: Request):
    """
    app.state.config_mode に基づいて表示するYAMLリストを切り替えます。
    JSON形式で`{"results": [config_files]}`を返します。
    """
    api_logger = AppLogger(APP_NAME)
    api_logger.info_log(f"{request.url.path} Receive {request.method}")
    config_mode = getattr(request.app.state, "config_mode", "default")
    return {"results": get_config_list(config_mode)}


@router.post("/config-title")
async def config_title(request: Request):
    api_logger = AppLogger(APP_NAME)
    """
    config_file で指定したファイルの`title`と`note`を返します。
    """
    try:
        body_data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, detail="Invalid JSON format in request body"
        )

    # 1. config_file の取得とYAML読み込み
    config_file_path = body_data.get("config_file")
    api_logger.debug_log(f"Request Config title of {config_file_path}")
    if not config_file_path:
        raise HTTPException(status_code=400, detail="Missing 'config_file'")

    result_data = get_config_title(config_file_path)
    api_logger.debug_log(f"Return Config title: {result_data}")
    return {"results": result_data}
