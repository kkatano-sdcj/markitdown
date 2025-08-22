"""
Markitdown Web API - メインアプリケーション
ファイル変換APIのエントリーポイント
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from api import conversion, settings, health
from api.websocket import websocket_endpoint
# Firebase機能が有効になったら有効化
# from api import storage
from services.config_manager import ConfigManager
from services.conversion_service import ConversionService

# ログレベルの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 設定マネージャーの初期化
config_manager = ConfigManager()

# 変換サービスの初期化
conversion_service = ConversionService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # 起動時の処理
    os.makedirs("./uploads", exist_ok=True)
    os.makedirs("./converted", exist_ok=True)
    
    # データベースサービスの初期化（必要なパッケージがインストールされている場合のみ）
    try:
        # 一時的に無効化
        pass
        # conversion_service.initialize_databases()
    except Exception as e:
        print(f"Warning: Failed to initialize database services: {e}")
    
    yield
    # 終了時の処理
    # 一時ファイルのクリーンアップなど

# FastAPIアプリケーションの作成
app = FastAPI(
    title="Markitdown Converter API",
    description="各種ドキュメントファイルをMarkdown形式に変換するWeb API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # フロントエンドのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルートパスのエンドポイント
@app.get("/")
async def root():
    """APIのルートパス"""
    return {
        "message": "Markitdown Converter API",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs",
        "redoc": "http://localhost:8000/redoc"
    }

# APIルーターの登録
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(conversion.router, prefix="/api/v1/conversion", tags=["conversion"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])
# Firebase機能が有効になったら有効化
# app.include_router(storage.router, tags=["storage"])

# WebSocketエンドポイント
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)