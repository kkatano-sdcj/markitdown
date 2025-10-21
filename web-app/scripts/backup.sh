#!/bin/bash

# ========================================
# バックアップスクリプト
# ========================================

set -e

# 色の定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# バックアップディレクトリ
BACKUP_DIR="${PROJECT_DIR}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="markitdown_backup_${TIMESTAMP}"

mkdir -p "$BACKUP_DIR"

log_info "バックアップを開始します: $BACKUP_NAME"

# バックアップディレクトリの作成
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"
mkdir -p "$BACKUP_PATH"

# 1. Dockerボリュームのバックアップ
log_info "Dockerボリュームをバックアップしています..."

# uploadsボリューム
docker run --rm \
    -v markitdown_uploads:/data \
    -v "$BACKUP_PATH":/backup \
    alpine tar czf /backup/uploads.tar.gz -C /data .

# convertedボリューム
docker run --rm \
    -v markitdown_converted:/data \
    -v "$BACKUP_PATH":/backup \
    alpine tar czf /backup/converted.tar.gz -C /data .

# logsボリューム
docker run --rm \
    -v markitdown_logs:/data \
    -v "$BACKUP_PATH":/backup \
    alpine tar czf /backup/logs.tar.gz -C /data .

# 2. 設定ファイルのバックアップ
log_info "設定ファイルをバックアップしています..."
cp "${PROJECT_DIR}/docker-compose.prod.yml" "$BACKUP_PATH/"
cp -r "${PROJECT_DIR}/nginx" "$BACKUP_PATH/" 2>/dev/null || true
cp -r "${PROJECT_DIR}/certbot" "$BACKUP_PATH/" 2>/dev/null || true

# 環境変数ファイル（センシティブ情報があるため注意）
log_warn "環境変数ファイルをバックアップしています（センシティブ情報を含む可能性があります）"
cp "${PROJECT_DIR}/backend/.env.production" "$BACKUP_PATH/backend.env.production" 2>/dev/null || true
cp "${PROJECT_DIR}/frontend/.env.production" "$BACKUP_PATH/frontend.env.production" 2>/dev/null || true

# 3. バックアップの圧縮
log_info "バックアップを圧縮しています..."
cd "$BACKUP_DIR"
tar czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# バックアップサイズの表示
BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
log_info "バックアップが完了しました: ${BACKUP_NAME}.tar.gz (サイズ: $BACKUP_SIZE)"

# 古いバックアップの削除（30日以上前のもの）
log_info "30日以上前の古いバックアップを削除しています..."
find "$BACKUP_DIR" -name "markitdown_backup_*.tar.gz" -mtime +30 -delete

log_info "バックアップ処理が完了しました"
log_info "バックアップファイル: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
