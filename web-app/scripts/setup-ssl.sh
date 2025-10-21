#!/bin/bash

# ========================================
# SSL証明書セットアップスクリプト (Let's Encrypt)
# ========================================

set -e

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ドメイン名の入力
read -p "ドメイン名を入力してください (例: example.com): " DOMAIN
read -p "メールアドレスを入力してください: " EMAIL

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    log_error "ドメイン名とメールアドレスは必須です"
    exit 1
fi

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Certbotディレクトリの作成
mkdir -p ./certbot/conf
mkdir -p ./certbot/www

log_info "Let's Encryptを使用してSSL証明書を取得します..."
log_info "ドメイン: $DOMAIN"
log_info "メール: $EMAIL"

# ステージング環境でテスト（最初は--stagingを使用することを推奨）
read -p "ステージング環境でテストしますか？ (推奨) (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    STAGING_FLAG=""
    log_info "本番環境の証明書を取得します"
else
    STAGING_FLAG="--staging"
    log_info "ステージング環境で証明書を取得します"
fi

# Certbotコンテナを使用して証明書を取得
docker run -it --rm \
    -v "${PROJECT_DIR}/certbot/conf:/etc/letsencrypt" \
    -v "${PROJECT_DIR}/certbot/www:/var/www/certbot" \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    $STAGING_FLAG \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

if [ $? -eq 0 ]; then
    log_info "SSL証明書の取得に成功しました！"
    log_info ""
    log_info "次のステップ:"
    log_info "1. nginx/nginx.confのドメイン名を '$DOMAIN' に更新してください"
    log_info "2. バックエンドとフロントエンドの.env.productionファイルのURLを更新してください"
    log_info "3. デプロイスクリプトを実行してください: ./scripts/deploy.sh"
    log_info ""
    log_info "証明書の自動更新を設定する場合は、以下のcronジョブを追加してください:"
    log_info "0 0 * * * cd $PROJECT_DIR && docker run --rm -v \"$PROJECT_DIR/certbot/conf:/etc/letsencrypt\" -v \"$PROJECT_DIR/certbot/www:/var/www/certbot\" certbot/certbot renew --webroot --webroot-path=/var/www/certbot && docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload"
else
    log_error "SSL証明書の取得に失敗しました"
    exit 1
fi
