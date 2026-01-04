import argparse
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from api.v0.routes import router as api_v0_router
from logic.AppLogger import AppLogger

APP_NAME = "api_server"

# グローバル変数（モジュールレベル）でポート番号を保持
_server_port = 3000  # デフォルト値


def parse_args():
    parser = argparse.ArgumentParser(description="Run the FastAPI server.")
    parser.add_argument(
        "--port", type=int, default=3000, help="Port number to listen on"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="default",
        help="config mode (e.g. single, multi)",
    )
    return parser.parse_args()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPIのライフサイクル管理
    起動時と終了時の処理を定義
    """
    # === 起動時の処理 ===
    app.state.port = _server_port
    api_logger = AppLogger(APP_NAME)
    api_logger.info_log(f"Server initialized with port: {_server_port}")

    yield  # ここでアプリケーションが実行される

    # === 終了時の処理 ===
    api_logger.info_log("Server shutting down")


# FastAPIアプリケーションの作成（lifespanを設定）
app = FastAPI(
    title="API Server",
    version="0.1.1",
    lifespan=lifespan,  # ★ ライフサイクル管理を追加
)

# ルーター登録
app.include_router(api_v0_router, prefix="/api/v0")


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Run the FastAPI server.")
    # parser.add_argument(
    #     "--port", type=int, default=3000, help="Port number to listen on"
    # )
    args = parse_args()

    # ★ グローバル変数に保存
    _server_port = args.port
    # ★ アプリケーションの状態に保存（lifespan内でもアクセス可能）
    app.state.config_mode = args.config

    print(f"Starting server on port: {args.port}")
    api_logger = AppLogger(APP_NAME)
    api_logger.info_log(f"Starting server on port: {args.port}")

    uvicorn.run(app, host="0.0.0.0", port=args.port)
