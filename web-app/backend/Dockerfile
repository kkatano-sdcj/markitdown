FROM python:3.11-slim

WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 依存関係ファイルをコピー
COPY requirements.txt .

# Python依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY app/ /app/

# アップロードと変換済みファイル用のディレクトリを作成
RUN mkdir -p /uploads /converted

# 非rootユーザーを作成
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /uploads /converted

USER appuser

# アプリケーションを起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]