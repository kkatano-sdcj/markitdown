# Nginx Dockerfile for Production

FROM nginx:1.25-alpine

# Nginxの設定ファイルをコピー
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Let's Encrypt証明書検証用のディレクトリを作成
RUN mkdir -p /var/www/certbot

# ヘルスチェック用
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
