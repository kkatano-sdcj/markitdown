# MarkItDown Web Application

様々な形式のファイル（DOCX, XLSX, PDF, PPTXなど）をMarkdown形式に変換するWebアプリケーションです。

## 機能

- ✅ 複数ファイルの一括変換
- ✅ ドラッグ&ドロップによるファイルアップロード
- ✅ OpenAI APIを使用した変換結果の強化（オプション）
- ✅ リアルタイムの変換進捗表示（WebSocket）
- ✅ 変換済みファイルのダウンロード
- ✅ YouTube URL変換
- ✅ 画像OCR（PaddleOCR）

## アーキテクチャ

このプロジェクトは**ハイブリッドデプロイ**を採用しています：

- **Frontend**: React + TypeScript → **Vercelにデプロイ**（グローバルCDN）
- **Backend**: FastAPI + Python → **Docker運用**（自社サーバー/VPS）
- **Infrastructure**: Docker & Nginx - バックエンドのみ

## 必要な環境

### 開発環境
- Node.js 18以上
- Docker & Docker Compose
- Git

### 本番環境
- Docker & Docker Compose（バックエンド用）
- Vercelアカウント（フロントエンド用）

## セットアップと起動

### 開発環境

1. **バックエンドの起動**
```bash
# リポジトリをクローン
cd web-app

# 環境変数を設定
cp backend/.env.example backend/.env

# Dockerでバックエンドを起動
docker-compose up -d

# ログを確認
docker-compose logs -f backend
```

2. **フロントエンドの起動**
```bash
# フロントエンドディレクトリに移動
cd frontend

# 依存関係をインストール
npm install

# 環境変数を設定
cp .env.example .env.local

# 開発サーバーを起動
npm start
```

3. **アクセス**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 開発ワークフロー

### バックエンド開発

```bash
# バックエンドを起動
docker-compose up -d

# ログを確認
docker-compose logs -f backend

# バックエンドを再ビルド
docker-compose build backend
docker-compose up -d

# バックエンドを停止
docker-compose down
```

### フロントエンド開発

```bash
# フロントエンドディレクトリに移動
cd frontend

# 開発サーバーを起動（ホットリロード有効）
npm start

# ビルドテスト
npm run build

# テストを実行
npm test
```

### デバッグ

```bash
# バックエンドのログ
docker-compose logs -f backend

# コンテナに接続
docker-compose exec backend bash

# フロントエンドのデバッグ
# ブラウザの開発者ツールを使用
```

## API仕様

### エンドポイント

#### ヘルスチェック
- `GET /health` - サービスの稼働状態を確認

#### ファイル変換
- `POST /api/v1/conversion/upload` - 単一ファイルの変換
- `POST /api/v1/conversion/batch` - 複数ファイルの一括変換
- `GET /api/v1/conversion/download/{filename}` - 変換済みファイルのダウンロード
- `GET /api/v1/conversion/supported-formats` - サポートされているファイル形式

#### 設定管理
- `GET /api/v1/settings/api` - API設定の取得
- `POST /api/v1/settings/api/configure` - APIキーの設定
- `POST /api/v1/settings/api/test` - API接続テスト

詳細なAPI仕様は http://localhost:8000/docs で確認できます。

## プロジェクト構造

```
web-app/
├── backend/                  # FastAPI バックエンド（Docker運用）
│   ├── Dockerfile           # 開発用
│   ├── Dockerfile.prod      # 本番用
│   ├── requirements.txt
│   └── app/
│       ├── main.py          # FastAPIアプリケーション
│       ├── api/             # APIエンドポイント
│       ├── services/        # ビジネスロジック
│       └── models/          # データモデル
├── frontend/                # React フロントエンド（Vercel運用）
│   ├── package.json
│   ├── vercel.json          # Vercel設定
│   └── src/
│       ├── App.tsx          # メインコンポーネント
│       ├── components/      # UIコンポーネント
│       ├── services/        # API通信
│       └── types/           # TypeScript型定義
├── nginx/                   # Nginxリバースプロキシ（本番のみ）
├── scripts/                 # デプロイスクリプト
├── docker-compose.yml       # 開発環境（バックエンドのみ）
└── docker-compose.prod.yml  # 本番環境（バックエンドのみ）
```

## 環境変数

### Backend (.env)
- `APP_ENV`: 実行環境（development/production）
- `OPENAI_API_KEY`: OpenAI APIキー（オプション）
- `ALLOWED_ORIGINS`: CORS許可オリジン（開発: http://localhost:3000、本番: Vercelドメイン）
- `DEBUG`: デバッグモード（true/false）

### Frontend (.env.local)
- `REACT_APP_API_URL`: Backend APIのURL（開発: http://localhost:8000）
- `REACT_APP_WS_URL`: WebSocket URL（開発: ws://localhost:8000）
- `REACT_APP_ENV`: 環境（development/production）

詳細は各ディレクトリの `.env.example` を参照してください。

## 本番環境へのデプロイ

詳細は以下のドキュメントを参照してください：

- **クイックスタート**: [QUICK_START.md](QUICK_START.md) - 5分でデプロイ
- **ハイブリッドデプロイガイド**: [DEPLOYMENT_HYBRID.md](DEPLOYMENT_HYBRID.md) - 詳細な手順
- **Vercelデプロイガイド**: [frontend/VERCEL_DEPLOYMENT.md](frontend/VERCEL_DEPLOYMENT.md) - フロントエンド専用

### 概要

1. **バックエンド** → Dockerで自社サーバー/VPSにデプロイ
   ```bash
   ./scripts/deploy.sh
   ```

2. **フロントエンド** → Vercelにデプロイ
   ```bash
   cd frontend
   vercel --prod
   ```

## トラブルシューティング

### バックエンドが起動しない

```bash
# ログを確認
docker-compose logs backend

# コンテナを再起動
docker-compose restart backend

# 完全にクリーンアップして再起動
docker-compose down -v
docker-compose up -d --build
```

### フロントエンドがAPIに接続できない

1. バックエンドが起動しているか確認
   ```bash
   curl http://localhost:8000/health
   ```

2. `.env.local` の `REACT_APP_API_URL` を確認

3. ブラウザのコンソールでCORSエラーを確認
   - バックエンドの `ALLOWED_ORIGINS` に `http://localhost:3000` が含まれているか確認

### ポートが使用中の場合

```bash
# 使用中のポートを確認
lsof -i :3000  # フロントエンド
lsof -i :8000  # バックエンド

# プロセスを終了
kill -9 <PID>
```

## テスト

```bash
# バックエンドのテスト
docker-compose exec backend pytest

# フロントエンドのテスト
cd frontend
npm test
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。