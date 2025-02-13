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
API_KEY = "YOUR_GOOGLE_SAFE_BROWSING_API_KEY"

# ログ設定
logging.basicConfig(level=logging.DEBUG)  # デバッグログを有効化

# ルートページ（ホーム画面）
@app.route("/")
def index():
    logging.debug("🟢 ルートページにアクセスがありました")
    return render_template("index.html")  # `templates/index.html` を返す

# URLの安全性をチェックするエンドポイント
@app.route("/check_url", methods=["POST"])
def check_url():
    data = request.json
    url = data.get("url", "")

    logging.debug(f"🔍 受信したURL: {url}")

    if not url:
        logging.warning("⚠️ 空のURLが送信されました")
        return jsonify({"is_safe": None, "message": "❌ URLが空です。", "reasons": ["入力されたURLがありません。"]})

    result = is_safe_url(url)  # URLの安全性をチェック

    logging.debug(f"🔍 URLのチェック結果: {result}")

    return jsonify({
        "is_safe": result["is_safe"],
        "message": result["message"],
        "reasons": result["reasons"]
    })

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
        logging.debug(f"🔍 APIリクエスト: {json.dumps(payload, indent=2)}")  # リクエスト内容をログに記録

        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # HTTPエラーが発生したら例外をスロー
        result = response.json()

        logging.debug(f"🔍 APIレスポンス: {json.dumps(result, indent=2)}")  # APIのレスポンスを記録

        if "matches" in result and result["matches"]:
            threats = [match["threatType"] for match in result["matches"]]
            return {"is_safe": False, "message": "⚠️ 危険なURLです！", "reasons": threats}

        return {"is_safe": True, "message": "✅ 安全なURLです。", "reasons": []}

    except requests.exceptions.RequestException as e:
        logging.error(f"🚨 APIエラー: {e}")
        return {"is_safe": None, "message": "🚨 Google Safe Browsing APIエラー", "reasons": [str(e)]}

# アプリケーションのエントリポイント
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
