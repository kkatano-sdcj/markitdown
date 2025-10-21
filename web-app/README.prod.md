# MarkItDown Web App - 本番環境クイックスタート

## 🏗️ アーキテクチャ

- **フロントエンド**: Vercel（グローバルCDN）
- **バックエンド**: Docker + 自社サーバー/VPS

## 🚀 クイックスタート

### 1. 前提条件の確認

**バックエンド:**
```bash
docker --version   # 24.0以上
docker-compose --version  # 2.20以上
```

**フロントエンド:**
```bash
node --version   # 18以上
npm install -g vercel
```

### 2. バックエンドの環境変数設定

```bash
nano backend/.env.production
```

**必須設定:**
- `OPENAI_API_KEY`: OpenAI APIキー
- `ALLOWED_ORIGINS`: VercelのドメインCORS設定（例: https://your-app.vercel.app,https://*.vercel.app）
- ドメイン名を `nginx/nginx.conf` で更新

### 3. バックエンドのSSL証明書取得

```bash
./scripts/setup-ssl.sh
```

### 4. バックエンドのデプロイ

```bash
./scripts/deploy.sh
```

### 5. フロントエンドのデプロイ

```bash
# 方法1: デプロイスクリプトを使用
./scripts/deploy-frontend.sh

# 方法2: 直接Vercel CLIを使用
cd frontend
vercel --prod
```

### 6. 確認

```bash
# バックエンドの確認
./scripts/health-check.sh

# フロントエンドの確認
# Vercelが提供するURLにアクセス
```

## 📁 本番環境のファイル構成

```
web-app/
├── backend/                     # バックエンド（Docker運用）
│   ├── .env.production          # 本番環境変数
│   ├── .env.example             # 環境変数テンプレート
│   └── Dockerfile.prod          # 本番用Dockerfile
├── frontend/                    # フロントエンド（Vercel運用）
│   ├── vercel.json              # Vercel設定
│   ├── .vercelignore            # Vercelビルド除外設定
│   ├── .env.vercel              # Vercel環境変数リファレンス
│   └── VERCEL_DEPLOYMENT.md     # Vercelデプロイガイド
├── nginx/                       # APIゲートウェイ
│   ├── nginx.conf               # Nginx設定（API専用）
│   └── Dockerfile               # NginxのDockerfile
├── scripts/
│   ├── deploy.sh                # バックエンドデプロイ
│   ├── deploy-frontend.sh       # フロントエンドデプロイ（Vercel）
│   ├── setup-ssl.sh             # SSL証明書設定
│   ├── backup.sh                # バックアップ
│   ├── restore.sh               # リストア
│   └── health-check.sh          # ヘルスチェック
├── docker-compose.prod.yml      # 本番用Docker Compose（バックエンドのみ）
├── DEPLOYMENT.md                # 詳細なデプロイガイド（旧版）
├── DEPLOYMENT_HYBRID.md         # ハイブリッドデプロイガイド（最新版）
└── README.prod.md               # このファイル
```

## 🔧 よく使うコマンド

```bash
# デプロイ
./scripts/deploy.sh

# ヘルスチェック
./scripts/health-check.sh

# バックアップ
./scripts/backup.sh

# ログの確認
docker-compose -f docker-compose.prod.yml logs -f

# コンテナの再起動
docker-compose -f docker-compose.prod.yml restart

# コンテナの停止
docker-compose -f docker-compose.prod.yml down

# 完全なクリーンアップ
docker-compose -f docker-compose.prod.yml down -v
```

## 📊 モニタリング

```bash
# サービスの状態確認
docker-compose -f docker-compose.prod.yml ps

# リソース使用状況
docker stats

# ログの確認
docker-compose -f docker-compose.prod.yml logs [service-name]
```

## 🔐 セキュリティ

### 環境変数の保護

```bash
chmod 600 backend/.env.production
chmod 600 frontend/.env.production
```

### ファイアウォール設定

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 🆘 トラブルシューティング

### コンテナが起動しない

```bash
# ログを確認
docker-compose -f docker-compose.prod.yml logs

# 再ビルド
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### SSL証明書のエラー

```bash
# 証明書の確認
docker run --rm -v "$(pwd)/certbot/conf:/etc/letsencrypt" certbot/certbot certificates

# 証明書の更新
./scripts/setup-ssl.sh
```

## 📚 詳細情報

詳細なデプロイ手順とトラブルシューティングについては、[DEPLOYMENT.md](DEPLOYMENT.md)を参照してください。

## 🔄 更新手順

```bash
# 1. 最新のコードを取得
git pull origin main

# 2. バックアップを作成
./scripts/backup.sh

# 3. デプロイ
./scripts/deploy.sh

# 4. 確認
./scripts/health-check.sh
```

## 🎯 本番環境の特徴

- ✅ マルチステージビルドによる最適化
- ✅ Nginxリバースプロキシ
- ✅ SSL/TLS対応
- ✅ ヘルスチェック機能
- ✅ 自動再起動（restart: unless-stopped）
- ✅ リソース制限設定
- ✅ ログローテーション
- ✅ セキュリティヘッダー
- ✅ Gzip圧縮
- ✅ 静的ファイルキャッシング

## 📞 サポート

問題が発生した場合:
1. [DEPLOYMENT.md](DEPLOYMENT.md)のトラブルシューティングを確認
2. ログファイルを確認
3. GitHub Issuesで報告
