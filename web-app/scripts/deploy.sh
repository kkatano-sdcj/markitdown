#!/bin/bash

# ========================================
# MarkItDown 本番環境デプロイスクリプト
# ========================================

set -e  # エラーが発生したら即座に終了

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

log_info "MarkItDown 本番環境へのデプロイを開始します..."

# 環境変数ファイルの確認
if [ ! -f "./backend/.env.production" ]; then
    log_error "backend/.env.production が見つかりません"
    exit 1
fi

if [ ! -f "./frontend/.env.production" ]; then
    log_error "frontend/.env.production が見つかりません"
    exit 1
fi

log_info "環境変数ファイルの確認完了"

# Gitの変更を確認（オプション）
if [ -n "$(git status --porcelain)" ]; then
    log_warn "未コミットの変更があります。本番環境へのデプロイ前にコミットすることを推奨します"
    read -p "続行しますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "デプロイを中止しました"
        exit 0
    fi
fi

# 既存のコンテナを停止
log_info "既存のコンテナを停止しています..."
docker-compose -f docker-compose.prod.yml down || true

# イメージのビルド
log_info "Dockerイメージをビルドしています..."
docker-compose -f docker-compose.prod.yml build --no-cache

# コンテナの起動
log_info "コンテナを起動しています..."
docker-compose -f docker-compose.prod.yml up -d

# ヘルスチェック
log_info "ヘルスチェックを実行しています..."
sleep 10

# バックエンドのヘルスチェック
BACKEND_HEALTH=$(docker exec markitdown-backend-prod curl -s http://localhost:8000/health || echo "failed")
if [[ $BACKEND_HEALTH == *"healthy"* ]] || [[ $BACKEND_HEALTH == *"ok"* ]]; then
    log_info "バックエンドの起動を確認しました"
else
    log_error "バックエンドの起動に失敗しました"
    log_error "ログを確認してください: docker logs markitdown-backend-prod"
    exit 1
fi

# フロントエンドのヘルスチェック
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80 || echo "000")
if [ "$FRONTEND_HEALTH" == "200" ]; then
    log_info "フロントエンドの起動を確認しました"
else
    log_error "フロントエンドの起動に失敗しました (HTTPステータス: $FRONTEND_HEALTH)"
    log_error "ログを確認してください: docker logs markitdown-frontend-prod"
    exit 1
fi

# デプロイ完了
log_info "========================================="
log_info "バックエンドのデプロイが正常に完了しました！"
log_info "========================================="
log_info "バックエンドAPI: http://localhost/api"
log_info "ヘルスチェック: http://localhost/health"
log_info "APIドキュメント: http://localhost/docs"
log_info ""
log_info "次のステップ:"
log_info "1. フロントエンドをVercelにデプロイ"
log_info "   cd frontend && vercel --prod"
log_info ""
log_info "2. Vercelの環境変数を設定"
log_info "   REACT_APP_API_URL=https://api.your-domain.com"
log_info "   REACT_APP_WS_URL=wss://api.your-domain.com"
log_info ""
log_info "ログの確認:"
log_info "  docker-compose -f docker-compose.prod.yml logs -f"
log_info ""
log_info "停止方法:"
log_info "  docker-compose -f docker-compose.prod.yml down"
