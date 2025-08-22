# ファイルコンバーター - Markdown変換アプリケーション

様々な形式のファイル（docx、xlsx、PDF、pptx）をMarkdown形式に変換するデスクトップアプリケーションです。

## 機能

- 複数ファイルの一括変換
- サポート形式: Word文書（.docx）、Excelファイル（.xlsx）、PDF（.pdf）、PowerPoint（.pptx）
- OpenAI APIを使用した変換結果の強化（オプション）
- 直感的なGUIインターフェース
- 設定の永続化

## インストール

### 開発環境のセットアップ

1. Pythonの仮想環境を作成：
```bash
python -m venv venv
```

2. 仮想環境をアクティベート：
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. 依存関係をインストール：
```bash
pip install -r requirements.txt
```

## 使用方法

### アプリケーションの起動

```bash
python src/main.py
```

### 実行可能ファイルのビルド

```bash
python build_exe.py
```

ビルドが完了すると、`dist`フォルダに`FileConverter.exe`が作成されます。

## 設定

### OpenAI API設定

1. アプリケーションのメニューから「設定」→「API設定」を選択
2. OpenAI APIキーを入力
3. 「接続テスト」ボタンで接続を確認
4. 「保存」ボタンで設定を保存

APIキーは安全にローカルに保存されます。

## プロジェクト構造

```
markitdown/
├── src/
│   ├── gui/
│   │   ├── main_window.py      # メインウィンドウ
│   │   └── settings_dialog.py  # 設定ダイアログ
│   ├── services/
│   │   ├── conversion_service.py  # ファイル変換
│   │   ├── api_service.py         # OpenAI API統合
│   │   └── config_manager.py     # 設定管理
│   ├── models/
│   │   └── data_models.py        # データモデル
│   └── main.py                   # エントリーポイント
├── requirements.txt
├── build_exe.py
└── README.md
```