#!/bin/bash

# ========================================
# フロントエンド Vercelデプロイスクリプト
# ========================================

set -e

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_DIR/frontend"

cd "$FRONTEND_DIR"

log_info "========================================="
log_info "MarkItDown フロントエンド - Vercelデプロイ"
log_info "========================================="
echo ""

# Vercel CLIのインストール確認
if ! command -v vercel &> /dev/null; then
    log_error "Vercel CLIがインストールされていません"
    echo ""
    log_info "以下のコマンドでインストールしてください:"
    echo "  npm install -g vercel"
    exit 1
fi

# 環境変数の確認
log_step "1. 環境変数の確認"
echo ""

if [ ! -f ".env.vercel" ]; then
    log_warn ".env.vercel ファイルが見つかりません"
    log_info "環境変数の設定例を表示します"
    echo ""
    echo "必須の環境変数:"
    echo "  REACT_APP_API_URL=https://api.your-domain.com"
    echo "  REACT_APP_WS_URL=wss://api.your-domain.com"
    echo ""
fi

# デプロイタイプの選択
log_step "2. デプロイタイプの選択"
echo ""
echo "デプロイ先を選択してください:"
echo "  1) プレビュー環境（開発・テスト用）"
echo "  2) 本番環境（Production）"
echo ""
read -p "選択 (1 or 2): " -n 1 -r
echo ""

if [[ $REPLY == "2" ]]; then
    DEPLOY_FLAG="--prod"
    ENV_TYPE="production"
    log_info "本番環境へのデプロイを開始します"
else
    DEPLOY_FLAG=""
    ENV_TYPE="preview"
    log_info "プレビュー環境へのデプロイを開始します"
fi

echo ""

# 環境変数の確認
log_step "3. Vercel環境変数の確認"
echo ""
log_info "Vercelダッシュボードで以下の環境変数が設定されているか確認してください:"
echo ""
echo "必須:"
echo "  ✓ REACT_APP_API_URL"
echo "  ✓ REACT_APP_WS_URL"
echo ""
echo "オプション:"
echo "  ○ REACT_APP_GA_MEASUREMENT_ID (Google Analytics)"
echo "  ○ REACT_APP_SENTRY_DSN (Sentry)"
echo ""
read -p "環境変数の設定は完了していますか？ (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_warn "環境変数を設定してから再度実行してください"
    log_info ""
    log_info "環境変数の設定方法:"
    log_info "  vercel env add REACT_APP_API_URL $ENV_TYPE"
    log_info "  vercel env add REACT_APP_WS_URL $ENV_TYPE"
    echo ""
    log_info "または、Vercelダッシュボードから設定:"
    log_info "  https://vercel.com/dashboard → プロジェクト → Settings → Environment Variables"
    exit 0
fi

# ビルドテスト
log_step "4. ビルドテスト（オプション）"
echo ""
read -p "デプロイ前にローカルでビルドテストを実行しますか？ (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "ビルドテストを実行中..."
    npm run build

    if [ $? -eq 0 ]; then
        log_info "ビルドテストが成功しました"
    else
        log_error "ビルドに失敗しました"
        exit 1
    fi
fi

echo ""

# デプロイ実行
log_step "5. Vercelへのデプロイ"
echo ""
log_info "デプロイを開始します..."
echo ""

vercel $DEPLOY_FLAG

if [ $? -eq 0 ]; then
    echo ""
    log_info "========================================="
    log_info "デプロイが正常に完了しました！"
    log_info "========================================="
    echo ""

    if [[ $DEPLOY_FLAG == "--prod" ]]; then
        log_info "本番環境のURLを確認:"
        log_info "  vercel ls"
        echo ""
        log_info "カスタムドメインの設定:"
        log_info "  Vercel Dashboard → Settings → Domains"
    else
        log_info "プレビューURLでアプリケーションを確認してください"
    fi

    echo ""
    log_info "次のステップ:"
    log_info "1. デプロイされたURLにアクセスして動作確認"
    log_info "2. バックエンドAPIとの接続を確認"
    log_info "3. 環境変数が正しく反映されているか確認"

else
    log_error "デプロイに失敗しました"
    echo ""
    log_info "トラブルシューティング:"
    log_info "1. ログを確認: vercel logs"
    log_info "2. 環境変数を確認: vercel env ls"
    log_info "3. ビルドエラーを確認: npm run build"
    exit 1
fi
