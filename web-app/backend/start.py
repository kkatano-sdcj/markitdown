#!/usr/bin/env python3
"""
Render.com用のエントリーポイント
モジュールパスの問題を解決するためのスタートアップスクリプト
"""
import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 環境変数の設定
os.environ.setdefault("PYTHONPATH", str(project_root))

# メインアプリケーションをインポートして実行
if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    # ポート設定（Renderの環境変数から取得）
    port = int(os.environ.get("PORT", 8000))
    
    # サーバー起動
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
