#!/bin/bash

# ========================================
# リストアスクリプト
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

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_DIR}/backups"

# バックアップファイルの選択
if [ -z "$1" ]; then
    log_info "利用可能なバックアップファイル:"
    ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null || {
        log_error "バックアップファイルが見つかりません"
        exit 1
    }
    echo ""
    read -p "リストアするバックアップファイル名を入力してください: " BACKUP_FILE
else
    BACKUP_FILE="$1"
fi

BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILE}"

if [ ! -f "$BACKUP_PATH" ]; then
    log_error "バックアップファイルが見つかりません: $BACKUP_PATH"
    exit 1
fi

log_warn "========================================="
log_warn "警告: この操作は現在のデータを上書きします"
log_warn "========================================="
read -p "本当にリストアしますか？ (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log_info "リストアを中止しました"
    exit 0
fi

# バックアップの展開
log_info "バックアップファイルを展開しています..."
TEMP_DIR="${BACKUP_DIR}/temp_restore"
mkdir -p "$TEMP_DIR"
tar xzf "$BACKUP_PATH" -C "$TEMP_DIR"

# 展開されたディレクトリを取得
EXTRACTED_DIR=$(find "$TEMP_DIR" -maxdepth 1 -type d -name "markitdown_backup_*" | head -1)

if [ -z "$EXTRACTED_DIR" ]; then
    log_error "バックアップの展開に失敗しました"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# コンテナの停止
log_info "コンテナを停止しています..."
docker-compose -f "${PROJECT_DIR}/docker-compose.prod.yml" down || true

# Dockerボリュームのリストア
log_info "Dockerボリュームをリストアしています..."

# uploadsボリューム
if [ -f "${EXTRACTED_DIR}/uploads.tar.gz" ]; then
    docker run --rm \
        -v markitdown_uploads:/data \
        -v "${EXTRACTED_DIR}":/backup \
        alpine sh -c "rm -rf /data/* && tar xzf /backup/uploads.tar.gz -C /data"
    log_info "uploadsボリュームをリストアしました"
fi

# convertedボリューム
if [ -f "${EXTRACTED_DIR}/converted.tar.gz" ]; then
    docker run --rm \
        -v markitdown_converted:/data \
        -v "${EXTRACTED_DIR}":/backup \
        alpine sh -c "rm -rf /data/* && tar xzf /backup/converted.tar.gz -C /data"
    log_info "convertedボリュームをリストアしました"
fi

# logsボリューム
if [ -f "${EXTRACTED_DIR}/logs.tar.gz" ]; then
    docker run --rm \
        -v markitdown_logs:/data \
        -v "${EXTRACTED_DIR}":/backup \
        alpine sh -c "rm -rf /data/* && tar xzf /backup/logs.tar.gz -C /data"
    log_info "logsボリュームをリストアしました"
fi

# 設定ファイルのリストア
log_info "設定ファイルをリストアしています..."
if [ -d "${EXTRACTED_DIR}/nginx" ]; then
    cp -r "${EXTRACTED_DIR}/nginx" "${PROJECT_DIR}/"
    log_info "Nginx設定をリストアしました"
fi

if [ -d "${EXTRACTED_DIR}/certbot" ]; then
    cp -r "${EXTRACTED_DIR}/certbot" "${PROJECT_DIR}/"
    log_info "SSL証明書をリストアしました"
fi

# 一時ディレクトリの削除
rm -rf "$TEMP_DIR"

log_info "========================================="
log_info "リストアが完了しました"
log_info "========================================="
log_info ""
log_info "次のステップ:"
log_info "1. 環境変数ファイルを確認してください"
log_info "2. コンテナを起動してください: ./scripts/deploy.sh"
