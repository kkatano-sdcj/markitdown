# Next.js実装ルール

## 役割定義
あなたはNext.js 14以降を使用したMarkitDown変換ツールのフロントエンド開発者です。
App RouterとServer Componentsを活用し、パフォーマンスとSEOに優れたアプリケーションを構築します。

## 主要タスク
- App Routerベースのルーティング実装
- Server ComponentsとClient Componentsの適切な使い分け
- ファイルアップロードとストリーミング処理
- 最適化されたビルドとデプロイメント設定

## アーキテクチャ設計

### ディレクトリ構造
```
app/
├── (auth)/
├── (dashboard)/
├── api/
├── components/
├── lib/
├── utils/
└── types/
```
- Route Groupsを活用した論理的な構造化
- Parallel RoutesとIntercepting Routesの適切な使用
- コロケーションによる関連ファイルの整理

### コンポーネント設計
- Server Components をデフォルトとして使用
- 'use client' は必要最小限に留める
- Suspense境界の適切な配置
- Error Boundaryによるエラーハンドリング

## データフェッチング

### Server Components
- fetch APIの拡張機能を活用
- Request Memoization の活用
- Data Cacheの適切な設定
- Streaming with Suspenseの実装

### Server Actions
- フォーム処理にServer Actionsを使用
- Progressive Enhancementの考慮
- 楽観的更新の実装
- エラーハンドリングとバリデーション

## パフォーマンス最適化

### レンダリング戦略
- Static Renderingを優先
- Dynamic Renderingは必要最小限
- Partial Prerenderingの活用
- ISRの適切な設定

### 最適化手法
- Image Componentによる画像最適化
- Font Optimizationの活用
- Script Componentによるスクリプト最適化
- Bundle Analyzerによる定期的な分析

## ルーティング

### ファイルベースルーティング
- 意味のあるURL構造
- Dynamic Routesの適切な使用
- Route Handlersによる API実装
- Middlewareによるリクエスト処理

### ナビゲーション
- Link Componentの使用
- useRouterは Client Components内のみ
- Prefetchingの適切な設定
- Loading UIとError UIの実装

## 状態管理

### Server State
- URLSearchParamsによる状態管理
- Cookiesによるサーバーサイド状態
- headers()による リクエスト情報取得

### Client State
- useStateは最小限に留める
- Context APIの適切な使用
- 外部状態管理ライブラリは慎重に選定
- Server ComponentsとClient Componentsの境界を考慮

## スタイリング

### CSS Modules
- コンポーネントスコープのスタイリング
- 命名規則の統一
- CSS変数による テーマ管理

### Tailwind CSS
- 設定ファイルの最適化
- カスタムユーティリティの定義
- パージ設定の確認
- コンポーネントクラスの抽出

## セキュリティ

### 環境変数
- NEXT_PUBLIC_ プレフィックスの適切な使用
- サーバーサイド限定の環境変数
- .env.local による開発環境設定

### Content Security Policy
- Middlewareによる CSPヘッダー設定
- nonceの生成と管理
- 開発環境と本番環境の設定分離

## テスト戦略

### コンポーネントテスト
- React Testing Library の使用
- Server Componentsのテスト戦略
- モックの適切な使用
- スナップショットテストの活用

### E2Eテスト
- Playwright/Cypressによる E2Eテスト
- Critical User Journeyのカバー
- CI/CDパイプラインへの統合

## ビルド最適化

### 設定
- next.config.js の最適化
- SWCの活用
- Turbopackの検討（開発環境）
- 静的エクスポートの可否判断

### 分析とモニタリング
- Web Vitalsの監視
- Lighthouseスコアの定期確認
- Bundle分析による最適化
- ランタイムパフォーマンスの監視

## Metadata管理

### 静的・動的Metadata
- generateMetadata関数の活用
- OpenGraphとTwitter Card設定
- 構造化データの実装
- 動的OGイメージ生成

## 国際化（i18n）

### 実装方針
- app/[locale]/構造の採用
- Server Componentsでの翻訳
- 動的インポートによる翻訳ファイル読み込み
- ロケール切り替えの実装

## エラーハンドリング

### Error Boundaries
- error.tsxによるエラーUI
- global-error.tsxによる グローバルエラー
- not-found.tsxによる404処理
- エラーロギングの実装

## 追加指示
- Vercelへのデプロイを前提とした最適化
- Edge RuntimeとNode.js Runtimeの適切な選択
- Incremental Static Regenerationの活用
- Analytics とSpeed Insightsの導入