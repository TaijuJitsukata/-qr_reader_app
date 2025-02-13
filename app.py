from flask import Flask, render_template, request, jsonify
import requests
import json
import os
import logging
from flask_cors import CORS

# Flaskアプリのセットアップ
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app, resources={r"/check_url": {"origins": "*"}})

# Google Safe Browsing APIキー
API_KEY = "AIzaSyA4AFpKB4rW-ZSHfcrk3zgs4-Fgy4KTPPI"

# ログ設定
logging.basicConfig(level=logging.DEBUG)  # デバッグ用

# Google Safe Browsing API を使ってURLの安全性を確認
def is_safe_url(url):
    api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}"
    payload = {
        "client": {
            "clientId": "qr_reader_app",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # HTTPエラーがあれば例外をスロー
        result = response.json()

        logging.debug(f"🔍 APIレスポンス: {json.dumps(result, indent=2)}")  # デバッグログ

        if "matches" in result:
            threats = [match["threatType"] for match in result["matches"]]
            return {"is_safe": False, "message": "⚠️ 危険なURLです！", "reasons": threats}

        return {"is_safe": True, "message": "✅ 安全なURLです。", "reasons": []}

    except requests.exceptions.RequestException as e:
        logging.error(f"🚨 APIエラー: {e}")
        return {"is_safe": None, "message": "🚨 Google Safe Browsing APIエラー", "reasons": [str(e)]}

# 短縮URLを展開する関数（bit.ly など）
def expand_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        logging.debug(f"🔍 短縮URL展開: {url} → {response.url}")  # 展開結果をログに出力
        return response.url  # 最終リダイレクトURLを取得
    except requests.RequestException:
        return url  # エラーの場合はそのまま返す

# ホームページの表示
@app.route("/")
def index():
    return render_template("index.html")

# QRコードのURLをチェックするエンドポイント
@app.route("/check_url", methods=["POST"])
def check_url():
    data = request.json
    url = data.get("url", "")

    if not url:
        return jsonify({"is_safe": None, "message": "❌ URLが空です。", "reasons": ["入力されたURLがありません。"]})

    expanded_url = expand_url(url)  # 短縮URLを展開
    result = is_safe_url(expanded_url)  # 展開後のURLをチェック

    return jsonify({
        "is_safe": result["is_safe"],
        "message": result["message"],
        "reasons": result["reasons"]
    })

# アプリケーションのエントリポイント
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
