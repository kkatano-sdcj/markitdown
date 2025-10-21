# Render.com デプロイ手順（修正版）

## 🚨 重要な設定変更

### 1. Renderダッシュボードでの設定

#### 基本設定
- **Name**: `markitdown-backend`
- **Environment**: `Python 3`
- **Region**: `Oregon (US West)`
- **Branch**: `main` または `master`
- **Root Directory**: `web-app/backend` ← **重要**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python start.py`

#### 環境変数（Environment タブで設定）
```
PYTHONPATH=/opt/render/project/src
ENVIRONMENT=production
PYTHONUNBUFFERED=1
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
PORT=10000
```

**注意**: `PORT`は通常Renderが自動設定しますが、明示的に設定することも可能です。

### 2. デバッグ用の段階的アプローチ

#### Step 1: 最小限のテスト
1. **Start Command**を `python test_minimal.py` に変更
2. デプロイして基本的なポートバインディングを確認
3. ログで以下を確認：
   - Python version
   - Directory structure
   - PORT environment variable

#### Step 2: 完全なアプリケーション
1. Step 1が成功したら **Start Command**を `python start.py` に戻す
2. ログで詳細なデバッグ情報を確認
3. インポートエラーの具体的な原因を特定

### 3. よくある問題と解決策

#### 問題: ModuleNotFoundError: No module named 'app'
**原因**: 
- Root Directoryの設定が間違っている
- PYTHONPATHが正しく設定されていない
- ファイル構造がRenderで期待される形と異なる

**解決策**:
1. Root Directoryが `web-app/backend` に設定されていることを確認
2. `app/__init__.py` ファイルが存在することを確認
3. `start.py` の詳細ログでディレクトリ構造を確認

#### 問題: No open ports detected
**原因**:
- アプリケーションがインポートエラーで起動していない
- uvicorn.run() に到達していない
- ポート設定が間違っている

**解決策**:
1. まず `test_minimal.py` で基本動作を確認
2. ログでアプリケーション起動までの流れを追跡
3. PORT環境変数が正しく設定されていることを確認

### 4. ログの確認方法

Renderダッシュボードの「Logs」タブで以下を確認：

1. **ビルドログ**: 依存関係のインストール状況
2. **デプロイログ**: アプリケーション起動の詳細
3. **ランタイムログ**: 実行時エラーとデバッグ情報

### 5. トラブルシューティング用コマンド

Render Shellでのデバッグ（必要に応じて）:
```bash
# ディレクトリ構造確認
ls -la
ls -la app/

# Python環境確認
python --version
python -c "import sys; print(sys.path)"

# モジュールインポートテスト
python -c "import app.main; print('Success')"
```

### 6. 成功の指標

以下のログが表示されれば成功：
```
✓ uvicorn imported successfully
✓ Successfully imported app.main directly
App type: <class 'fastapi.applications.FastAPI'>
App title: Markitdown Converter API
Starting uvicorn server...
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000
```

### 7. 緊急時の対応

すべてが失敗した場合：
1. `render-test.yaml` を使用して最小限のアプリをテスト
2. 成功したら段階的に機能を追加
3. 各段階でログを詳細に確認
