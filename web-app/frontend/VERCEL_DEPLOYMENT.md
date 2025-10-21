# MarkItDown Frontend - Vercelデプロイガイド

## 目次

1. [Vercelとは](#vercelとは)
2. [前提条件](#前提条件)
3. [初回デプロイ手順](#初回デプロイ手順)
4. [環境変数の設定](#環境変数の設定)
5. [カスタムドメインの設定](#カスタムドメインの設定)
6. [継続的デプロイ](#継続的デプロイ)
7. [トラブルシューティング](#トラブルシューティング)

---

## Vercelとは

Vercelは、フロントエンドアプリケーションのデプロイに最適化されたクラウドプラットフォームです。

### メリット
- ✅ 自動デプロイ（GitHubと連携）
- ✅ グローバルCDN
- ✅ 無料SSL証明書
- ✅ プレビュー環境（プルリクエスト毎）
- ✅ 高速なビルドとデプロイ
- ✅ 自動スケーリング

---

## 前提条件

### 必要なもの

1. **Vercelアカウント**
   - [https://vercel.com/signup](https://vercel.com/signup) で無料登録

2. **GitHubアカウント**
   - リポジトリをGitHubにプッシュしておく

3. **バックエンドAPI**
   - 別途デプロイされたバックエンドAPIのURL

---

## 初回デプロイ手順

### 方法1: Vercel CLIを使用（推奨）

#### 1. Vercel CLIのインストール

```bash
npm install -g vercel
```

#### 2. ログイン

```bash
vercel login
```

#### 3. プロジェクトディレクトリに移動

```bash
cd /path/to/markitdown/web-app/frontend
```

#### 4. デプロイ

```bash
# 初回デプロイ
vercel

# プロダクション環境にデプロイ
vercel --prod
```

対話形式で以下を設定します：
- プロジェクト名
- ディレクトリ（デフォルトでOK）
- ビルド設定（自動検出されます）

### 方法2: Vercelダッシュボードから（簡単）

#### 1. GitHubにプッシュ

```bash
git add .
git commit -m "Add Vercel configuration"
git push origin main
```

#### 2. Vercelダッシュボードにアクセス

1. [https://vercel.com/dashboard](https://vercel.com/dashboard) にアクセス
2. "Add New Project" をクリック
3. GitHubリポジトリを選択
4. "Import" をクリック

#### 3. プロジェクト設定

- **Framework Preset**: Create React App
- **Root Directory**: `web-app/frontend` を指定
- **Build Command**: `npm run build`（自動検出）
- **Output Directory**: `build`（自動検出）

#### 4. 環境変数の設定（後述）

#### 5. "Deploy" をクリック

---

## 環境変数の設定

### Vercelダッシュボードでの設定

1. プロジェクトの Settings > Environment Variables に移動
2. 以下の環境変数を追加

#### 必須の環境変数

| 変数名 | 値 | 環境 |
|--------|-----|------|
| `REACT_APP_API_URL` | `https://api.your-domain.com` | Production, Preview, Development |
| `REACT_APP_WS_URL` | `wss://api.your-domain.com` | Production, Preview, Development |
| `REACT_APP_ENV` | `production` | Production |
| `GENERATE_SOURCEMAP` | `false` | Production |

#### オプションの環境変数

| 変数名 | 値 | 環境 |
|--------|-----|------|
| `REACT_APP_GA_MEASUREMENT_ID` | Google Analytics ID | Production |
| `REACT_APP_SENTRY_DSN` | Sentry DSN | Production |
| `REACT_APP_ENABLE_AI_MODE` | `true` または `false` | All |
| `REACT_APP_ENABLE_YOUTUBE` | `true` または `false` | All |
| `REACT_APP_MAX_FILE_SIZE_MB` | `50` | All |

### CLI経由での設定

```bash
# 本番環境の環境変数を設定
vercel env add REACT_APP_API_URL production
# 入力: https://api.your-domain.com

vercel env add REACT_APP_WS_URL production
# 入力: wss://api.your-domain.com

# プレビュー環境の環境変数を設定
vercel env add REACT_APP_API_URL preview
# 入力: https://api-staging.your-domain.com

# 全ての環境変数を一覧表示
vercel env ls
```

---

## カスタムドメインの設定

### 1. Vercelダッシュボードで設定

1. プロジェクトの Settings > Domains に移動
2. カスタムドメインを追加（例: `app.your-domain.com`）
3. DNS設定の指示に従う

### 2. DNS設定

#### Aレコード方式
```
A レコード: app.your-domain.com → 76.76.21.21
```

#### CNAMEレコード方式（推奨）
```
CNAME レコード: app.your-domain.com → cname.vercel-dns.com
```

### 3. SSL証明書

Vercelが自動的にLet's Encrypt証明書を発行します（数分〜数十分）。

---

## 継続的デプロイ

### 自動デプロイの仕組み

GitHubと連携している場合、以下のタイミングで自動デプロイされます：

1. **本番環境（Production）**
   - `main` ブランチへのプッシュ
   - マージされたプルリクエスト

2. **プレビュー環境（Preview）**
   - プルリクエストの作成・更新
   - その他のブランチへのプッシュ

### デプロイの確認

```bash
# デプロイ履歴の確認
vercel ls

# 特定のデプロイの詳細を確認
vercel inspect <deployment-url>

# ログの確認
vercel logs <deployment-url>
```

---

## バックエンドとの連携

### 1. バックエンドのCORS設定更新

バックエンドの `.env.production` を更新:

```bash
# Vercelのドメインを追加
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app,https://app.your-domain.com

# またはサブドメインを許可
ALLOWED_ORIGINS=https://*.your-domain.com
```

### 2. API URLの設定

フロントエンドの環境変数でバックエンドAPIのURLを指定:

```bash
REACT_APP_API_URL=https://api.your-domain.com
REACT_APP_WS_URL=wss://api.your-domain.com
```

---

## ビルド設定のカスタマイズ

### vercel.json（既に作成済み）

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": "create-react-app",
  "regions": ["hnd1"],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

### package.json スクリプト

必要に応じて追加:

```json
{
  "scripts": {
    "build": "react-scripts build",
    "vercel-build": "react-scripts build",
    "analyze": "source-map-explorer 'build/static/js/*.js'"
  }
}
```

---

## パフォーマンス最適化

### 1. ビルドサイズの最適化

```bash
# ビルドサイズの分析
npm install -g source-map-explorer
npm run build
source-map-explorer 'build/static/js/*.js'
```

### 2. キャッシュの活用

Vercelは自動的に以下をキャッシュします：
- 静的アセット（JS, CSS, 画像など）
- ビルド成果物
- node_modules（高速ビルド用）

### 3. 画像の最適化

Vercelの自動画像最適化を活用できます（Next.jsの場合）。
CRAの場合は、ビルド時に最適化するか、Cloudinaryなどを使用。

---

## モニタリングと分析

### 1. Vercel Analytics

```bash
# Vercel Analyticsを有効化（ダッシュボードから）
```

プロジェクトの Analytics タブで以下を確認：
- ページビュー
- パフォーマンス（Web Vitals）
- トラフィック

### 2. Google Analytics

環境変数で設定済み:
```bash
REACT_APP_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

### 3. Sentry（エラートラッキング）

環境変数で設定済み:
```bash
REACT_APP_SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

## トラブルシューティング

### ビルドエラー

#### エラー: "Module not found"

```bash
# node_modulesを削除して再インストール
rm -rf node_modules package-lock.json
npm install

# ローカルでビルドテスト
npm run build
```

#### エラー: "Environment variable not defined"

Vercelダッシュボードで環境変数を確認:
- Settings > Environment Variables
- 本番環境とプレビュー環境の両方に設定されているか確認

### デプロイエラー

#### 問題: デプロイが成功するがページが表示されない

1. ビルド出力ディレクトリを確認
   - Settings > General > Output Directory が `build` になっているか

2. ルーティング設定を確認
   - `vercel.json` の routes 設定を確認

#### 問題: APIに接続できない

1. 環境変数を確認
   ```bash
   vercel env ls
   ```

2. バックエンドのCORS設定を確認
   - Vercelのドメインが許可されているか

3. ブラウザのコンソールでエラーを確認
   - Network タブでAPIリクエストを確認

### パフォーマンス問題

#### 問題: 初回ロードが遅い

1. Code Splitting を実装
   ```javascript
   const Component = React.lazy(() => import('./Component'));
   ```

2. 不要なパッケージを削除
   ```bash
   npm run build
   # ビルドサイズを確認
   ```

3. Service Workerの活用（PWA化）

---

## セキュリティベストプラクティス

### 1. 環境変数の管理

- ❌ `.env` ファイルをGitにコミットしない
- ✅ Vercelダッシュボードで管理
- ✅ シークレット情報は `@` プレフィックス付きで管理

### 2. セキュリティヘッダー

`vercel.json` で設定済み:
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection
- Referrer-Policy

### 3. HTTPS

- Vercelが自動的にHTTPSを有効化
- HTTP→HTTPSリダイレクトも自動

---

## CLI コマンドリファレンス

```bash
# デプロイ
vercel                  # プレビューデプロイ
vercel --prod           # 本番デプロイ

# プロジェクト管理
vercel ls               # デプロイ一覧
vercel rm [id]          # デプロイ削除
vercel alias            # エイリアス管理

# 環境変数
vercel env ls           # 環境変数一覧
vercel env add [name]   # 環境変数追加
vercel env rm [name]    # 環境変数削除

# ログとモニタリング
vercel logs [url]       # デプロイログ
vercel inspect [url]    # デプロイ詳細

# プロジェクト設定
vercel link             # プロジェクトをリンク
vercel pull             # 環境変数をダウンロード
```

---

## チェックリスト

デプロイ前に確認:

- [ ] GitHubリポジトリにコードがプッシュされている
- [ ] Vercelアカウントが作成されている
- [ ] 環境変数が設定されている（REACT_APP_API_URL など）
- [ ] バックエンドAPIが稼働している
- [ ] バックエンドのCORS設定にVercelドメインが含まれている
- [ ] カスタムドメインのDNS設定が完了している（オプション）
- [ ] Google Analytics/Sentryの設定が完了している（オプション）

---

## 参考リンク

- [Vercel公式ドキュメント](https://vercel.com/docs)
- [Create React App デプロイガイド](https://create-react-app.dev/docs/deployment/)
- [Vercel環境変数ドキュメント](https://vercel.com/docs/concepts/projects/environment-variables)

---

**最終更新日**: 2025-01-20
