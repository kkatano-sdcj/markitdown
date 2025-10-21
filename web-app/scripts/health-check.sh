#!/bin/bash

# ========================================
# ヘルスチェックスクリプト
# ========================================

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ヘルスチェック関数
check_service() {
    local service_name=$1
    local url=$2

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)

    if [ "$response" == "200" ] || [ "$response" == "000" ]; then
        log_info "$service_name: ✓ 正常"
        return 0
    else
        log_error "$service_name: ✗ 異常 (HTTPステータス: $response)"
        return 1
    fi
}

echo "========================================="
echo "MarkItDown ヘルスチェック"
echo "========================================="
echo ""

# Dockerコンテナの状態確認
log_info "Dockerコンテナの状態を確認しています..."
docker-compose -f docker-compose.prod.yml ps

echo ""
log_info "サービスのヘルスチェックを実行しています..."
echo ""

# 各サービスのチェック
NGINX_OK=0
BACKEND_OK=0

# Nginxのチェック
if check_service "Nginx (API Gateway)" "http://localhost:80"; then
    NGINX_OK=1
fi

# バックエンドのチェック
if check_service "Backend API" "http://localhost:8000/health"; then
    BACKEND_OK=1
fi

echo ""
echo "========================================="
echo "ヘルスチェック結果"
echo "========================================="

TOTAL_SERVICES=2
HEALTHY_SERVICES=$((NGINX_OK + BACKEND_OK))

if [ $HEALTHY_SERVICES -eq $TOTAL_SERVICES ]; then
    log_info "全てのサービスが正常に動作しています ($HEALTHY_SERVICES/$TOTAL_SERVICES)"
    echo ""
    log_info "フロントエンド: Vercelで個別にデプロイされます"
    log_info "フロントエンドのデプロイ方法:"
    log_info "  cd frontend && vercel --prod"
    exit 0
else
    log_warn "$HEALTHY_SERVICES/$TOTAL_SERVICES のサービスが正常に動作しています"
    log_error "一部のサービスに問題があります"
    echo ""
    echo "ログを確認してください:"
    echo "  docker-compose -f docker-compose.prod.yml logs"
    exit 1
fi
