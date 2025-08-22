FROM node:18-alpine

WORKDIR /app

# システムの依存関係をインストール
RUN apk add --no-cache python3 make g++

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm ci

# アプリケーションファイルをコピー
COPY . .

# 開発サーバーを起動
CMD ["npm", "start"]