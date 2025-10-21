# MarkItDown Web App - ハイブリッドデプロイガイド

## アーキテクチャ概要

本プロジェクトは、**ハイブリッドデプロイアーキテクチャ**を採用しています：

- **フロントエンド**: Vercel（グローバルCDN + 自動デプロイ）
- **バックエンド**: Docker + VPS/クラウドサーバー（Nginx + FastAPI）

```
┌─────────────────────────────────────────────────────┐
│                    ユーザー                         │
└────────────┬────────────────────────┬───────────────┘
             │                        │
             │                        │
   ┌─────────▼──────────┐   ┌────────▼─────────────┐
   │   Vercel CDN      │   │  自社サーバー/VPS    │
   │  (フロントエンド)  │   │   (バックエンド)     │
   │                    │   │                      │
   │  - React App      │   │  - Nginx (Gateway)   │
   │  - 静的ファイル   │   │  - FastAPI           │
   │  - 自動SSL        │   │  - PostgreSQL        │
   └────────────────────┘   │  - Redis (オプション)│
                            └──────────────────────┘
```

## メリット

### フロントエンド（Vercel）
- ✅ グローバルCDN - 高速な配信
- ✅ 自動デプロイ - Git pushで自動更新
- ✅ プレビュー環境 - PRごとの環境
- ✅ 無料SSL証明書
- ✅ 無料プラン利用可能

### バックエンド（自社サーバー）
- ✅ データの完全なコントロール
- ✅ ファイルストレージの自由度
- ✅ コスト管理が容易
- ✅ カスタマイズの自由度

---

## 目次

1. [バックエンドのデプロイ](#バックエンドのデプロイ)
2. [フロントエンドのデプロイ](#フロントエンドのデプロイ)
3. [環境変数の設定](#環境変数の設定)
4. [CORS設定](#cors設定)
5. [トラブルシューティング](#トラブルシューティング)

---

## バックエンドのデプロイ

### 1. サーバーの準備

```bash
# Docker & Docker Composeのインストール
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Composeのインストール
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. リポジトリのクローン

```bash
git clone <your-repository-url>
cd markitdown/web-app
```

### 3. 環境変数の設定

```bash
# バックエンドの環境変数を編集
nano backend/.env.production
```

**重要な設定項目:**

```bash
# OpenAI API（AI機能を使用する場合）
OPENAI_API_KEY=sk-your-openai-api-key

# CORS設定 - Vercelのドメインを許可
# プレビュー環境も含める場合は *.vercel.app を使用
ALLOWED_ORIGINS=https://your-app.vercel.app,https://*.vercel.app,https://app.your-domain.com

# その他の設定
APP_ENV=production
DEBUG=false
API_SECRET_KEY=$(openssl rand -hex 32)
```

### 4. SSL証明書の取得

```bash
# Let's Encryptを使用
./scripts/setup-ssl.sh
```

### 5. デプロイ実行

```bash
# バックエンドのデプロイ
./scripts/deploy.sh
```

### 6. ヘルスチェック

```bash
# サービスの確認
./scripts/health-check.sh

# または直接確認
curl http://your-server-ip/health
```

---

## フロントエンドのデプロイ

### 方法1: Vercel CLIを使用（推奨）

#### 1. Vercel CLIのインストール

```bash
npm install -g vercel
```

#### 2. フロントエンドディレクトリに移動

```bash
cd frontend
```

#### 3. デプロイスクリプトを実行

```bash
# 対話形式でデプロイ
../scripts/deploy-frontend.sh

# または直接実行
vercel --prod
```

### 方法2: GitHubと連携（最も簡単）

#### 1. GitHubにプッシュ

```bash
git add .
git commit -m "Add Vercel configuration"
git push origin main
```

#### 2. Vercelダッシュボードから設定

1. [Vercelダッシュボード](https://vercel.com/dashboard)にアクセス
2. "New Project" をクリック
3. GitHubリポジトリを選択
4. プロジェクト設定:
   - **Root Directory**: `web-app/frontend`
   - **Framework Preset**: Create React App
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

#### 3. 環境変数の設定

Vercelダッシュボード → Settings → Environment Variables

| 変数名 | 値 | 環境 |
|--------|-----|------|
| `REACT_APP_API_URL` | `https://api.your-domain.com` | Production |
| `REACT_APP_WS_URL` | `wss://api.your-domain.com` | Production |
| `REACT_APP_ENV` | `production` | Production |
| `GENERATE_SOURCEMAP` | `false` | Production |

#### 4. デプロイ

"Deploy" をクリックするか、`main`ブランチにプッシュすると自動デプロイされます。

---

## 環境変数の設定

### バックエンド（backend/.env.production）

```bash
# API設定
OPENAI_API_KEY=sk-xxxxx

# CORS設定（重要！）
ALLOWED_ORIGINS=https://your-app.vercel.app,https://app.your-domain.com,https://*.vercel.app

# アプリケーション設定
APP_ENV=production
DEBUG=false
RELOAD=false

# セキュリティ
API_SECRET_KEY=<ランダムな文字列>

# データベース（オプション）
DATABASE_URL=postgresql://user:password@localhost/dbname
FIREBASE_API_KEY=xxxxx
```

### フロントエンド（Vercel環境変数）

**Vercel CLIで設定:**

```bash
cd frontend

# 本番環境の環境変数を設定
vercel env add REACT_APP_API_URL production
# 入力: https://api.your-domain.com

vercel env add REACT_APP_WS_URL production
# 入力: wss://api.your-domain.com

# プレビュー環境も設定（オプション）
vercel env add REACT_APP_API_URL preview
# 入力: https://api-staging.your-domain.com
```

**Vercelダッシュボードで設定:**

1. Project → Settings → Environment Variables
2. 以下を追加:

```
REACT_APP_API_URL=https://api.your-domain.com
REACT_APP_WS_URL=wss://api.your-domain.com
REACT_APP_ENV=production
GENERATE_SOURCEMAP=false
```

---

## CORS設定

### 重要: バックエンドのCORS設定

フロントエンドがVercelでホストされるため、バックエンドのCORS設定が重要です。

#### 1. 環境変数で設定（推奨）

`backend/.env.production`:

```bash
# 複数のオリジンをカンマ区切りで指定
ALLOWED_ORIGINS=https://your-app.vercel.app,https://app.your-domain.com

# またはワイルドカードを使用（Vercelのプレビュー環境を含める）
ALLOWED_ORIGINS=https://*.vercel.app,https://app.your-domain.com
```

#### 2. 動作確認

```bash
# ブラウザの開発者ツールで確認
# Network タブ → APIリクエスト → Response Headers
# Access-Control-Allow-Origin が正しく設定されているか確認
```

---

## カスタムドメインの設定

### フロントエンド（Vercel）

1. Vercelダッシュボード → Settings → Domains
2. カスタムドメインを追加（例: `app.your-domain.com`）
3. DNS設定:

```
CNAME app.your-domain.com → cname.vercel-dns.com
```

### バックエンド（自社サーバー）

1. DNS設定:

```
A    api.your-domain.com → <your-server-ip>
```

2. Nginx設定を更新:

```nginx
server_name api.your-domain.com;
ssl_certificate /etc/letsencrypt/live/api.your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/api.your-domain.com/privkey.pem;
```

3. SSL証明書を再取得:

```bash
./scripts/setup-ssl.sh
```

---

## デプロイフロー

### 開発から本番へのフロー

```
1. 開発 (ローカル)
   ├─ frontend: npm start (localhost:3000)
   └─ backend: docker-compose up (localhost:8000)

2. コミット & プッシュ
   └─ git push origin main

3. 自動デプロイ
   ├─ フロントエンド: Vercel が自動デプロイ
   └─ バックエンド: 手動デプロイまたはCI/CD

4. 本番環境
   ├─ フロントエンド: https://app.your-domain.com (Vercel)
   └─ バックエンド: https://api.your-domain.com (自社サーバー)
```

### 更新デプロイ

#### フロントエンド

```bash
# 自動デプロイ（GitHubと連携している場合）
git push origin main

# または手動デプロイ
cd frontend
vercel --prod
```

#### バックエンド

```bash
# サーバーにSSH接続
ssh user@your-server

# 最新のコードを取得
cd /path/to/markitdown/web-app
git pull origin main

# バックアップ
./scripts/backup.sh

# 再デプロイ
./scripts/deploy.sh
```

---

## トラブルシューティング

### CORSエラー

**症状:**
```
Access to fetch at 'https://api.your-domain.com/api/...' from origin 'https://your-app.vercel.app' has been blocked by CORS policy
```

**解決方法:**

1. バックエンドの環境変数を確認:
```bash
docker exec markitdown-backend-prod printenv | grep ALLOWED_ORIGINS
```

2. Vercelのドメインが含まれているか確認

3. バックエンドを再起動:
```bash
docker-compose -f docker-compose.prod.yml restart backend
```

### APIに接続できない

**チェックリスト:**

- [ ] バックエンドが起動しているか: `./scripts/health-check.sh`
- [ ] Vercelの環境変数が正しいか: `vercel env ls`
- [ ] CORS設定が正しいか: バックエンドの `.env.production`
- [ ] ファイアウォールが開いているか: `sudo ufw status`
- [ ] SSL証明書が有効か: `curl https://api.your-domain.com/health`

### Vercelビルドエラー

```bash
# ローカルでビルドテスト
cd frontend
npm run build

# ビルドログを確認
vercel logs <deployment-url>

# 環境変数を確認
vercel env ls
```

---

## モニタリング

### バックエンド

```bash
# ログの確認
docker-compose -f docker-compose.prod.yml logs -f

# リソース使用状況
docker stats

# ヘルスチェック
curl https://api.your-domain.com/health
```

### フロントエンド

```bash
# デプロイ履歴
vercel ls

# ログの確認
vercel logs <deployment-url>

# Analytics（Vercelダッシュボード）
https://vercel.com/dashboard → Analytics
```

---

## セキュリティチェックリスト

- [ ] バックエンドのSSL証明書が有効
- [ ] フロントエンドのSSL証明書が有効（Vercelが自動管理）
- [ ] CORS設定が適切（必要なオリジンのみ許可）
- [ ] 環境変数がGitにコミットされていない
- [ ] ファイアウォールが設定されている
- [ ] APIキーが安全に管理されている
- [ ] セキュリティヘッダーが設定されている
- [ ] 定期的なバックアップが設定されている

---

## コスト概算

### Vercel（フロントエンド）

- **Hobby（無料）**: 個人プロジェクト向け
  - 帯域幅: 100GB/月
  - ビルド時間: 100時間/月

- **Pro（$20/月）**: 商用プロジェクト向け
  - 帯域幅: 1TB/月
  - ビルド時間: 400時間/月

### 自社サーバー（バックエンド）

- **VPS**: $5-20/月（Linode, DigitalOcean, Vultrなど）
- **クラウド**: 使用量に応じて（AWS, GCP, Azureなど）

---

## よくある質問

**Q: なぜフロントエンドとバックエンドを分離？**

A:
- フロントエンド: グローバルCDNで高速配信、自動デプロイ
- バックエンド: データの完全なコントロール、コスト管理

**Q: Vercelの無料プランで十分？**

A: 小規模〜中規模プロジェクトなら無料プランで十分です。

**Q: バックエンドもVercelにデプロイできる？**

A: Vercelはファイルアップロードに制限があるため、このプロジェクトでは推奨しません。

---

## 参考リンク

- [Vercel公式ドキュメント](https://vercel.com/docs)
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [Docker公式ドキュメント](https://docs.docker.com/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**最終更新日**: 2025-01-20
