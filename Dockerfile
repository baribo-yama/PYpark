# ベースイメージ（Python 3.11）
FROM python:3.11-slim

# MediaPipe/OpenCVに必要なOSライブラリのインストール
# slimイメージには最小限のソフトしか入っていないため、描画系ライブラリを追加します
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ
WORKDIR /app

# 依存関係のコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -r requirements.txt

# アプリケーションをコピー（flask以下とtemplatesなど）
COPY flask ./flask

# Cloud Runのポート設定（環境変数PORTを使用. デフォルトは8080）
ENV PORT=8080
EXPOSE 8080

# アプリのディレクトリに移動してからgunicornで起動
WORKDIR /app/flask
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
