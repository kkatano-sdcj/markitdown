# MarkItDown Web App - 本番環境デプロイガイド

## 目次

1. [前提条件](#前提条件)
2. [サーバーのセットアップ](#サーバーのセットアップ)
3. [環境変数の設定](#環境変数の設定)
4. [SSL証明書の取得](#ssl証明書の取得)
5. [デプロイ手順](#デプロイ手順)
6. [バックアップとリストア](#バックアップとリストア)
7. [モニタリング](#モニタリング)
8. [トラブルシューティング](#トラブルシューティング)
9. [セキュリティ対策](#セキュリティ対策)

---

## 前提条件

### 必要なソフトウェア

- **Docker**: バージョン 24.0 以上
- **Docker Compose**: バージョン 2.20 以上
- **Git**: バージョン管理用
- **ドメイン**: SSL証明書取得用（推奨）

### サーバー要件

#### 最小構成
- CPU: 2コア
- メモリ: 4GB
- ストレージ: 20GB

#### 推奨構成
- CPU: 4コア以上
- メモリ: 8GB以上
- ストレージ: 50GB以上（SSD推奨）

---

## サーバーのセットアップ

### 1. Dockerのインストール

```bash
# Dockerの公式スクリプトを使用してインストール
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 現在のユーザーをdockerグループに追加
sudo usermod -aG docker $USER

# Dockerサービスの起動と自動起動設定
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. Docker Composeのインストール

```bash
# Docker Composeのインストール
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# バージョン確認
docker-compose --version
```

### 3. リポジトリのクローン

```bash
# プロジェクトのクローン
git clone <your-repository-url>
cd markitdown/web-app
```

---

## 環境変数の設定

### 1. バックエンド環境変数

```bash
# .env.productionファイルを編集
cd backend
nano .env.production
```

**必須設定項目:**

```bash
# OpenAI API（AI機能を使用する場合）
OPENAI_API_KEY=sk-your-openai-api-key

# フロントエンドURL（実際のドメインに変更）
FRONTEND_URL=https://your-domain.com

# CORS設定（実際のドメインに変更）
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# APIシークレットキー（ランダムな文字列を生成）
API_SECRET_KEY=$(openssl rand -hex 32)

# 本番環境設定
APP_ENV=production
DEBUG=false
RELOAD=false
```

**オプション設定:**

```bash
# Firebase（ストレージを使用する場合）
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_PROJECT_ID=your-project-id
# ... その他のFirebase設定

# 通知設定
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
```

### 2. フロントエンド環境変数

```bash
# .env.productionファイルを編集
cd ../frontend
nano .env.production
```

**必須設定項目:**

```bash
# APIのURL（実際のドメインに変更）
REACT_APP_API_URL=https://api.your-domain.com
REACT_APP_WS_URL=wss://api.your-domain.com

# 環境設定
REACT_APP_ENV=production
REACT_APP_DEBUG=false

# ビルド最適化
GENERATE_SOURCEMAP=false
```

**オプション設定:**

```bash
# Google Analytics
REACT_APP_GA_MEASUREMENT_ID=G-XXXXXXXXXX

# Sentry（エラートラッキング）
REACT_APP_SENTRY_DSN=https://your-sentry-dsn
REACT_APP_SENTRY_ENVIRONMENT=production
```

### 3. Nginx設定の更新

```bash
# Nginx設定ファイルを編集
cd ../nginx
nano nginx.conf
```

以下の箇所を実際のドメインに変更:

```nginx
server_name your-domain.com www.your-domain.com;
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
```

---

## SSL証明書の取得

### Let's Encryptを使用した無料SSL証明書の取得

```bash
# SSL証明書セットアップスクリプトを実行
cd /path/to/markitdown/web-app
./scripts/setup-ssl.sh
```

スクリプトの指示に従い、以下を入力:
1. ドメイン名（例: example.com）
2. メールアドレス
3. ステージング環境でテストするか（初回は推奨）

**注意:** ステージング環境でテストした後、本番環境の証明書を取得してください。

### 証明書の自動更新設定

```bash
# Cronジョブを追加
crontab -e
```

以下の行を追加:

```cron
# 毎日午前2時にSSL証明書の更新を確認
0 2 * * * cd /path/to/markitdown/web-app && docker run --rm -v "$(pwd)/certbot/conf:/etc/letsencrypt" -v "$(pwd)/certbot/www:/var/www/certbot" certbot/certbot renew --webroot --webroot-path=/var/www/certbot && docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

---

## デプロイ手順

### 1. 初回デプロイ

```bash
# プロジェクトディレクトリに移動
cd /path/to/markitdown/web-app

# デプロイスクリプトを実行
./scripts/deploy.sh
```

スクリプトは以下を自動的に実行します:
1. 環境変数ファイルの確認
2. 既存コンテナの停止
3. Dockerイメージのビルド
4. コンテナの起動
5. ヘルスチェック

### 2. 更新デプロイ

```bash
# 最新のコードを取得
git pull origin main

# デプロイスクリプトを実行
./scripts/deploy.sh
```

### 3. デプロイの確認

```bash
# ヘルスチェックスクリプトを実行
./scripts/health-check.sh

# ログの確認
docker-compose -f docker-compose.prod.yml logs -f

# 特定のサービスのログを確認
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### 4. サービスの状態確認

```bash
# 実行中のコンテナを確認
docker-compose -f docker-compose.prod.yml ps

# リソース使用状況を確認
docker stats
```

---

## バックアップとリストア

### バックアップの作成

```bash
# バックアップスクリプトを実行
./scripts/backup.sh
```

バックアップには以下が含まれます:
- アップロードされたファイル（uploads）
- 変換済みファイル（converted）
- ログファイル（logs）
- 設定ファイル
- SSL証明書

バックアップファイルは `backups/` ディレクトリに保存されます。

### 自動バックアップの設定

```bash
# Cronジョブを追加
crontab -e
```

以下の行を追加:

```cron
# 毎日午前3時にバックアップを実行
0 3 * * * cd /path/to/markitdown/web-app && ./scripts/backup.sh
```

### リストア（復元）

```bash
# リストアスクリプトを実行
./scripts/restore.sh

# または、バックアップファイルを指定
./scripts/restore.sh markitdown_backup_20250120_030000.tar.gz
```

---

## モニタリング

### 1. ヘルスチェック

```bash
# 定期的なヘルスチェック
./scripts/health-check.sh

# または、手動で確認
curl http://localhost/health
curl http://localhost:8000/health
```

### 2. ログの監視

```bash
# 全サービスのログをリアルタイムで監視
docker-compose -f docker-compose.prod.yml logs -f

# エラーログのみを表示
docker-compose -f docker-compose.prod.yml logs | grep -i error
```

### 3. リソース監視

```bash
# リソース使用状況の監視
docker stats

# ディスク使用量の確認
df -h
du -sh uploads/ converted/
```

### 4. 外部モニタリングサービスの設定（推奨）

以下のサービスを検討してください:
- **Uptime Monitoring**: UptimeRobot, Pingdom
- **Error Tracking**: Sentry（フロントエンド・バックエンド）
- **Analytics**: Google Analytics（フロントエンド）
- **Log Management**: ELK Stack, Datadog

---

## トラブルシューティング

### コンテナが起動しない場合

```bash
# ログを確認
docker-compose -f docker-compose.prod.yml logs

# 特定のコンテナのログを確認
docker logs markitdown-backend-prod
docker logs markitdown-frontend-prod
docker logs markitdown-nginx-prod

# コンテナの再起動
docker-compose -f docker-compose.prod.yml restart

# 完全な再ビルド
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### バックエンドAPIに接続できない場合

1. **ヘルスチェックの確認**
   ```bash
   curl http://localhost:8000/health
   ```

2. **CORS設定の確認**
   - `backend/.env.production` の `ALLOWED_ORIGINS` を確認
   - フロントエンドのドメインが含まれているか確認

3. **ネットワーク設定の確認**
   ```bash
   docker network ls
   docker network inspect markitdown-network
   ```

### フロントエンドが表示されない場合

1. **ビルドの確認**
   ```bash
   docker-compose -f docker-compose.prod.yml logs frontend
   ```

2. **Nginx設定の確認**
   ```bash
   docker exec markitdown-nginx-prod nginx -t
   docker exec markitdown-nginx-prod cat /etc/nginx/conf.d/default.conf
   ```

3. **環境変数の確認**
   - `frontend/.env.production` のAPI URLが正しいか確認

### SSL証明書のエラー

1. **証明書の有効期限確認**
   ```bash
   docker run --rm -v "$(pwd)/certbot/conf:/etc/letsencrypt" certbot/certbot certificates
   ```

2. **証明書の手動更新**
   ```bash
   docker run --rm -v "$(pwd)/certbot/conf:/etc/letsencrypt" -v "$(pwd)/certbot/www:/var/www/certbot" certbot/certbot renew --force-renewal
   docker-compose -f docker-compose.prod.yml restart nginx
   ```

### ディスク容量不足

```bash
# 未使用のDockerイメージを削除
docker image prune -a

# 未使用のボリュームを削除
docker volume prune

# 古いログファイルを削除
find ./logs -name "*.log" -mtime +30 -delete

# 古い変換ファイルを削除（FILE_RETENTION_HOURSの設定に応じて自動削除されます）
```

### パフォーマンスの問題

1. **ワーカー数の調整**
   - `backend/.env.production` の `WORKERS` を増やす
   - 推奨値: CPUコア数

2. **リソース制限の調整**
   - `docker-compose.prod.yml` のリソース制限を調整

3. **キャッシュの有効化**
   - `backend/.env.production` で `ENABLE_CACHE=true` を設定

---

## セキュリティ対策

### 1. 環境変数の保護

```bash
# .env.productionファイルのパーミッション設定
chmod 600 backend/.env.production
chmod 600 frontend/.env.production

# Gitにコミットされないことを確認
git status --ignored
```

### 2. ファイアウォール設定

```bash
# UFWを使用した基本的なファイアウォール設定
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. 定期的な更新

```bash
# システムパッケージの更新
sudo apt update && sudo apt upgrade -y

# Dockerイメージの更新
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### 4. セキュリティヘッダーの確認

```bash
# セキュリティヘッダーの確認
curl -I https://your-domain.com

# 期待される結果:
# - Strict-Transport-Security
# - X-Frame-Options
# - X-Content-Type-Options
# - X-XSS-Protection
```

### 5. ログの定期的な確認

```bash
# 不審なアクセスログの確認
docker-compose -f docker-compose.prod.yml logs nginx | grep -E "40[0-9]|50[0-9]"

# エラーログの確認
docker-compose -f docker-compose.prod.yml logs backend | grep -i error
```

---

## 運用Tips

### 1. ゼロダウンタイムデプロイ

ロードバランサーを使用したゼロダウンタイムデプロイの実装を検討してください。

### 2. CI/CDパイプラインの構築

GitHub Actions、GitLab CI、またはJenkinsを使用した自動デプロイの設定を推奨します。

### 3. データベースのマイグレーション

データベースを使用する場合は、マイグレーションスクリプトを作成し、デプロイ前に実行してください。

### 4. ロギング戦略

- 重要なイベントのログ記録
- ログローテーションの設定
- 外部ログ管理サービスの使用

---

## サポートとお問い合わせ

問題が発生した場合は、以下を確認してください:

1. このドキュメントのトラブルシューティングセクション
2. プロジェクトの GitHub Issues
3. ログファイルの確認

---

## チェックリスト

デプロイ前に以下を確認してください:

- [ ] DockerとDocker Composeがインストールされている
- [ ] ドメインが設定されている
- [ ] `backend/.env.production` が正しく設定されている
- [ ] `frontend/.env.production` が正しく設定されている
- [ ] `nginx/nginx.conf` のドメイン名が更新されている
- [ ] SSL証明書が取得されている
- [ ] ファイアウォールが設定されている
- [ ] バックアップスクリプトが設定されている
- [ ] モニタリングが設定されている

---

**最終更新日**: 2025-01-20
