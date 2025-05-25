# Pythonの公式イメージをベースイメージとして使用
FROM python:3.13-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピーしてインストール
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# FastAPIアプリケーションのメインファイルとポートを指定
# main.py がアプリケーションのエントリポイントであると仮定しています。
# ポートはCloud Runがデフォルトでリッスンする8080番ポートを想定しています。
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]