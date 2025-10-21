# Render.com デプロイガイド

## 概要
このガイドでは、MarkItDown BackendをRender.comにデプロイする方法を説明します。

## 前提条件
- Render.comアカウント
- GitHubリポジトリ
- OpenAI APIキー（オプション）

## デプロイ手順

### 1. Render.comでの新しいWebサービス作成

1. [Render Dashboard](https://dashboard.render.com/) にログイン
2. "New +" → "Web Service" を選択
3. GitHubリポジトリを接続

### 2. サービス設定

#### 基本設定
- **Name**: `markitdown-backend`
- **Region**: `Oregon (US West)`
- **Branch**: `main`
- **Root Directory**: `web-app/backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python start.py`

#### 環境変数設定
Render Dashboard の Environment タブで以下を設定：

**必須環境変数:**
```
PYTHONPATH=/opt/render/project/src
ENVIRONMENT=production
PYTHONUNBUFFERED=1
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

**オプション環境変数:**
```
OPENAI_API_KEY=sk-your-openai-api-key
FIREBASE_CREDENTIALS_PATH=/opt/render/project/src/firebase-credentials.json
LOG_LEVEL=INFO
```

### 3. 高度な設定

#### ヘルスチェック
- **Health Check Path**: `/health`
- **Health Check Grace Period**: `300` seconds

#### リソース設定
- **Plan**: Starter (512MB RAM, 0.1 CPU)
- **Auto-Deploy**: `Yes`

### 4. デプロイ実行

1. "Create Web Service" をクリック
2. 自動ビルド・デプロイが開始
3. ログでデプロイ状況を確認

## トラブルシューティング

### よくある問題

#### 1. ModuleNotFoundError: No module named 'app'
**解決策**: `start.py` スクリプトが自動的にPythonパスを設定します

#### 2. No open ports detected
**解決策**: `start.py` が環境変数 `PORT` からポートを取得してバインドします

#### 3. CORS エラー
**解決策**: `ALLOWED_ORIGINS` 環境変数にフロントエンドのURLを設定

### ログの確認
```bash
# Render Dashboard のログタブで確認
# または Render CLI を使用
render logs -s markitdown-backend
```

### 手動デバッグ
```bash
# Render Shell でコンテナにアクセス
render shell markitdown-backend

# Python パスの確認
python -c "import sys; print(sys.path)"

# モジュールのインポートテスト
python -c "from app.main import app; print('Import successful')"
```

## 本番環境での考慮事項

### セキュリティ
- 環境変数でAPIキーを管理
- HTTPS通信の確認
- CORS設定の適切な制限

### パフォーマンス
- Starter プランから開始
- 必要に応じてプランをアップグレード
- ログ監視とメトリクス確認

### 監視
- Render Dashboard でメトリクス確認
- アプリケーションログの定期チェック
- エラー率とレスポンス時間の監視

## 参考リンク
- [Render.com Documentation](https://render.com/docs)
- [Python on Render](https://render.com/docs/deploy-python)
- [Environment Variables](https://render.com/docs/environment-variables)
