#!/usr/bin/env python3
"""
Render.com用のエントリーポイント - 改良版
モジュールパスの問題を解決するためのスタートアップスクリプト
"""
import sys
import os
import signal
import time
from pathlib import Path

def signal_handler(signum, frame):
    print(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

# シグナルハンドラーを設定
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# 現在のディレクトリ情報を出力
current_dir = Path.cwd()
script_dir = Path(__file__).parent.resolve()

print("=== Render.com Startup Debug Info ===")
print(f"Current working directory: {current_dir}")
print(f"Script directory: {script_dir}")
print(f"Script file: {__file__}")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

# ディレクトリ構造を確認
print("\n=== Directory Structure ===")
for item in script_dir.iterdir():
    if item.is_dir():
        print(f"DIR:  {item.name}/")
        if item.name == "app":
            for subitem in item.iterdir():
                print(f"  {subitem.name}")
    else:
        print(f"FILE: {item.name}")

# Pythonパスの設定
print(f"\n=== Python Path Setup ===")
print(f"Original sys.path: {sys.path[:3]}...")

# スクリプトのディレクトリをPythonパスに追加
sys.path.insert(0, str(script_dir))
os.environ["PYTHONPATH"] = str(script_dir)

print(f"Updated sys.path[0]: {sys.path[0]}")
print(f"PYTHONPATH env var: {os.environ.get('PYTHONPATH')}")

# 環境変数の確認
print(f"\n=== Environment Variables ===")
print(f"PORT: {os.environ.get('PORT', 'not set')}")
print(f"ENVIRONMENT: {os.environ.get('ENVIRONMENT', 'not set')}")
print(f"PYTHONUNBUFFERED: {os.environ.get('PYTHONUNBUFFERED', 'not set')}")

# 必要なディレクトリを事前作成
print(f"\n=== Directory Creation ===")
try:
    uploads_dir = script_dir / "uploads"
    converted_dir = script_dir / "converted"
    uploads_dir.mkdir(exist_ok=True)
    converted_dir.mkdir(exist_ok=True)
    print(f"✓ Created: {uploads_dir}")
    print(f"✓ Created: {converted_dir}")
except Exception as e:
    print(f"✗ Directory creation error: {e}")

# メインアプリケーションをインポートして実行
if __name__ == "__main__":
    try:
        print(f"\n=== Application Import ===")
        
        # uvicornのインポートテスト
        import uvicorn
        print("✓ uvicorn imported successfully")
        
        # アプリケーションのインポート
        app = None
        
        # 方法1: 直接インポート
        try:
            print("Attempting direct import: from app.main import app")
            from app.main import app
            print("✓ Successfully imported app.main directly")
        except ImportError as e1:
            print(f"✗ Direct import failed: {e1}")
            
            # 方法2: 動的インポート
            try:
                print("Attempting dynamic import...")
                import importlib.util
                
                main_py_path = script_dir / "app" / "main.py"
                print(f"Looking for main.py at: {main_py_path}")
                
                if not main_py_path.exists():
                    raise FileNotFoundError(f"main.py not found at {main_py_path}")
                
                spec = importlib.util.spec_from_file_location("main", main_py_path)
                if spec is None or spec.loader is None:
                    raise ImportError("Could not create module spec")
                
                main_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(main_module)
                app = main_module.app
                print("✓ Successfully imported app using dynamic method")
                
            except Exception as e2:
                print(f"✗ Dynamic import failed: {e2}")
                
                # 方法3: 最後の手段 - sys.pathを調整
                try:
                    print("Attempting sys.path adjustment...")
                    app_dir = script_dir / "app"
                    if app_dir.exists():
                        sys.path.insert(0, str(app_dir))
                        print(f"Added to sys.path: {app_dir}")
                        
                        import main
                        app = main.app
                        print("✓ Successfully imported using sys.path adjustment")
                    else:
                        raise FileNotFoundError(f"app directory not found: {app_dir}")
                        
                except Exception as e3:
                    print(f"✗ All import methods failed: {e3}")
                    print("\n=== Critical Error ===")
                    print("Could not import the FastAPI application.")
                    print("Please check the file structure and dependencies.")
                    sys.exit(1)

        if app is None:
            print("✗ App is None after import attempts")
            sys.exit(1)

        # アプリケーションの検証
        print(f"\n=== Application Validation ===")
        print(f"App type: {type(app)}")
        print(f"App title: {getattr(app, 'title', 'Unknown')}")
        
        # ポート設定
        port = int(os.environ.get("PORT", 8000))
        host = "0.0.0.0"
        
        print(f"\n=== Server Startup ===")
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Starting uvicorn server...")

        # サーバー起動
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            # Renderでの安定性向上
            loop="asyncio",
            http="httptools"
        )

    except KeyboardInterrupt:
        print("\n=== Shutdown ===")
        print("Server stopped by user")
    except Exception as e:
        print(f"\n=== Critical Startup Error ===")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
        # デバッグのため少し待機
        print("Waiting 10 seconds before exit for log inspection...")
        time.sleep(10)
        sys.exit(1)
