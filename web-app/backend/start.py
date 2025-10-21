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

# デバッグ情報を出力
print(f"Python version: {sys.version}")
print(f"Project root: {project_root}")
print(f"sys.path: {sys.path}")
print(f"Environment PORT: {os.environ.get('PORT', 'not set')}")

# メインアプリケーションをインポートして実行
if __name__ == "__main__":
    import uvicorn

    try:
        from app.main import app
        print("Successfully imported app.main")
    except ImportError as e:
        print(f"ImportError: {e}")
        print("Attempting alternative import...")
        # 代替パスでインポート
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", project_root / "app" / "main.py")
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        app = main_module.app
        print("Successfully imported app using alternative method")

    # ポート設定（Renderの環境変数から取得）
    port = int(os.environ.get("PORT", 8000))

    print(f"Starting server on 0.0.0.0:{port}")

    # サーバー起動
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
