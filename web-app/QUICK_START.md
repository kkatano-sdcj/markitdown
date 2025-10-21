# MarkItDown Web App - クイックスタートガイド

## 📋 概要

このプロジェクトは**ハイブリッドデプロイ**を採用しています：

| コンポーネント | デプロイ先 | 理由 |
|---------------|-----------|------|
| **フロントエンド** | Vercel | グローバルCDN、自動デプロイ、無料SSL |
| **バックエンド** | Docker (VPS) | データ管理、ファイルストレージの自由度 |

---

## 🚀 5分でデプロイ

### ステップ1: バックエンドをデプロイ

```bash
# 1. サーバーにSSH接続
ssh user@your-server

# 2. リポジトリをクローン
git clone <your-repo-url>
cd markitdown/web-app

# 3. 環境変数を設定
nano backend/.env.production
# OPENAI_API_KEY と ALLOWED_ORIGINS を設定

# 4. デプロイ
./scripts/deploy.sh
```

✅ バックエンドが `http://your-server-ip:8000` で起動します

### ステップ2: フロントエンドをVercelにデプロイ

**方法A: GitHub連携（最も簡単）**

1. GitHubにプッシュ
2. [Vercel](https://vercel.com)にアクセス → "New Project"
3. GitHubリポジトリを選択
4. Root Directory: `web-app/frontend` を指定
5. 環境変数を設定:
   - `REACT_APP_API_URL` = `https://api.your-domain.com`
   - `REACT_APP_WS_URL` = `wss://api.your-domain.com`
6. "Deploy" をクリック

**方法B: CLI（柔軟）**

```bash
# Vercel CLIをインストール
npm install -g vercel

# フロントエンドをデプロイ
cd frontend
vercel --prod
```

✅ フロントエンドが `https://your-app.vercel.app` にデプロイされます

### ステップ3: CORS設定を更新

バックエンドの環境変数を更新:

```bash
nano backend/.env.production
```

```bash
# Vercelのドメインを追加
ALLOWED_ORIGINS=https://your-app.vercel.app,https://*.vercel.app
```

バックエンドを再起動:

```bash
docker-compose -f docker-compose.prod.yml restart backend
```

---

## ✅ 動作確認

### バックエンド

```bash
# ヘルスチェック
curl https://api.your-domain.com/health

# またはスクリプトを使用
./scripts/health-check.sh
```

### フロントエンド

1. Vercelが提供するURLにアクセス
2. ファイルアップロード機能を試す
3. ブラウザのコンソールでエラーがないか確認

---

## 🎯 次のステップ

### カスタムドメインの設定

**フロントエンド（Vercel）:**
1. Vercel Dashboard → Settings → Domains
2. `app.your-domain.com` を追加
3. DNS設定: `CNAME app → cname.vercel-dns.com`

**バックエンド:**
1. DNS設定: `A api → your-server-ip`
2. SSL証明書取得: `./scripts/setup-ssl.sh`

### 自動バックアップの設定

```bash
# Cronジョブを追加
crontab -e

# 毎日午前3時にバックアップ
0 3 * * * cd /path/to/markitdown/web-app && ./scripts/backup.sh
```

### モニタリング設定

- **Vercel Analytics**: ダッシュボードで有効化
- **Sentry**: エラートラッキング用
- **Google Analytics**: アクセス解析用

---

## 📚 詳細ドキュメント

| ドキュメント | 内容 |
|-------------|------|
| [DEPLOYMENT_HYBRID.md](DEPLOYMENT_HYBRID.md) | ハイブリッドデプロイの詳細ガイド |
| [frontend/VERCEL_DEPLOYMENT.md](frontend/VERCEL_DEPLOYMENT.md) | Vercelデプロイの完全ガイド |
| [DEPLOYMENT.md](DEPLOYMENT.md) | 従来のデプロイガイド（参考） |
| [README.prod.md](README.prod.md) | 本番環境リファレンス |

---

## 🆘 トラブルシューティング

### CORSエラーが発生

```bash
# バックエンドの環境変数を確認
docker exec markitdown-backend-prod printenv | grep ALLOWED_ORIGINS

# Vercelのドメインが含まれているか確認
# 含まれていない場合は追加して再起動
```

### APIに接続できない

```bash
# バックエンドのヘルスチェック
curl https://api.your-domain.com/health

# Vercelの環境変数を確認
cd frontend
vercel env ls
```

### Vercelビルドエラー

```bash
# ローカルでビルドテスト
cd frontend
npm run build

# エラーを修正後、再デプロイ
vercel --prod
```

---

## 💡 ヒント

- **開発環境**: `docker-compose up` でローカル開発
- **プレビュー環境**: PRを作成すると自動でVercelプレビュー環境が作成される
- **本番環境**: `main`ブランチへのプッシュで自動デプロイ（Vercel）

---

## 📞 サポート

問題が発生した場合:
1. ログを確認: `docker-compose logs` / `vercel logs`
2. ドキュメントを参照: 上記の詳細ドキュメント
3. GitHub Issuesで報告

---

**Happy Deploying! 🎉**
