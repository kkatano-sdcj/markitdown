# Markitdown Web Application

様々な形式のファイル（docx、xlsx、PDF、pptx）をMarkdown形式に変換するWebアプリケーションです。

## 機能

- 複数ファイルの一括変換
- ドラッグ&ドロップによるファイルアップロード
- OpenAI APIを使用した変換結果の強化（オプション）
- リアルタイムの変換進捗表示
- 変換済みファイルのダウンロード

## アーキテクチャ

このプロジェクトはモノレポ構成で、以下のコンポーネントから構成されています：

- **Backend**: FastAPI (Python) - markitdownライブラリを使用したファイル変換API
- **Frontend**: React (TypeScript) - ユーザーインターフェース
- **Infrastructure**: Docker & Docker Compose - コンテナオーケストレーション

## 必要な環境

- Docker Desktop (Docker & Docker Compose)
- Git

## セットアップと起動

1. リポジトリをクローン
```bash
cd web-app
```

2. Docker Composeで起動
```bash
docker-compose up -d
```

3. アプリケーションにアクセス
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 開発

### 開発モードで起動

```bash
# 開発モードで起動（ホットリロード有効）
docker-compose up

# バックグラウンドで起動
docker-compose up -d

# ログを確認
docker-compose logs -f

# 特定のサービスのログを確認
docker-compose logs -f backend
docker-compose logs -f frontend
```

### サービスの再ビルド

```bash
# 全サービスを再ビルド
docker-compose build

# 特定のサービスを再ビルド
docker-compose build backend
docker-compose build frontend
```

### サービスの停止

```bash
# サービスを停止
docker-compose down

# ボリュームも含めて削除
docker-compose down -v
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
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py           # FastAPIアプリケーション
│       ├── api/              # APIエンドポイント
│       ├── services/         # ビジネスロジック
│       └── models/           # データモデル
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── App.tsx           # メインコンポーネント
│       ├── components/       # UIコンポーネント
│       ├── services/         # API通信
│       └── types/            # TypeScript型定義
└── docker-compose.yml        # Docker Compose設定
```

## 環境変数

### Backend
- `ENVIRONMENT`: 実行環境（development/production）
- `OPENAI_API_KEY`: OpenAI APIキー（オプション）

### Frontend
- `REACT_APP_API_URL`: Backend APIのURL

## トラブルシューティング

### ポートが使用中の場合
```bash
# 使用中のポートを確認
lsof -i :3000
lsof -i :8000

# プロセスを終了
kill -9 <PID>
```

### コンテナの再起動
```bash
docker-compose restart backend
docker-compose restart frontend
```

### ログの確認
```bash
docker-compose logs backend
docker-compose logs frontend
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。