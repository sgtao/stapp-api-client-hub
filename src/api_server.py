import argparse
from fastapi import FastAPI
import uvicorn

from api.v0.routes import router as api_v0_router
from logic.AppLogger import AppLogger


APP_NAME = "api_server"
app = FastAPI(title="API Server", version="0.1.0")

# ルーター登録
app.include_router(api_v0_router, prefix="/api/v0")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the FastAPI server.")
    parser.add_argument(
        "--port", type=int, default=3000, help="Port number to listen on"
    )
    args = parser.parse_args()

    print(f"Starting server on port: {args.port}")
    api_logger = AppLogger(APP_NAME)
    api_logger.info_log(f"Starting server on port: {args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)
