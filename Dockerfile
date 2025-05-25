# Pythonの公式イメージをベースイメージとして使用
FROM python:3.13-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピーしてインストール
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 環境変数PORTが設定されていない場合のデフォルト値を設定
ENV PORT=8080

# FastAPIアプリケーションを起動
# Cloud RunのPORT環境変数を使用
CMD uvicorn main:app --host 0.0.0.0 --port $PORT