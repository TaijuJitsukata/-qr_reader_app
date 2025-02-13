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
        logging.debug(f"🔍 APIリクエスト: {json.dumps(payload, indent=2)}")  # リクエストをログに出力

        response = requests.post(api_url, headers=headers, json=payload)  # `json=payload` に変更
        response.raise_for_status()  # HTTPエラーがあれば例外をスロー
        result = response.json()

        logging.debug(f"🔍 APIレスポンス: {json.dumps(result, indent=2)}")  # APIのレスポンスを確認

        if "matches" in result and result["matches"]:
            threats = [match["threatType"] for match in result["matches"]]
            return {"is_safe": False, "message": "⚠️ 危険なURLです！", "reasons": threats}

        return {"is_safe": True, "message": "✅ 安全なURLです。", "reasons": []}

    except requests.exceptions.RequestException as e:
        logging.error(f"🚨 APIエラー: {e}")
        return {"is_safe": None, "message": "🚨 Google Safe Browsing APIエラー", "reasons": [str(e)]}

# QRコードのURLをチェックするエンドポイント
@app.route("/check_url", methods=["POST"])
def check_url():
    data = request.json
    url = data.get("url", "")

    if not url:
        return jsonify({"is_safe": None, "message": "❌ URLが空です。", "reasons": ["入力されたURLがありません。"]})

    result = is_safe_url(url)  # URLの安全性をチェック

    return jsonify({
        "is_safe": result["is_safe"],
        "message": result["message"],
        "reasons": result["reasons"]
    })

# アプリケーションのエントリポイント
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app, resources={r"/check_url": {"origins": "*"}})

# Google Safe Browsing APIキー
API_KEY = 'AIzaSyA4AFpKB4rW-ZSHfcrk3zgs4-Fgy4KTPPI'

def is_safe_url(url):
    api_url = f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}'
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
        response.raise_for_status()  # HTTPエラーをキャッチ
        result = response.json()

        # 危険なURLの場合
        if 'matches' in result:
            threats = [match['threatType'] for match in result['matches']]
            return {"is_safe": False, "message": "危険なURLです。", "reasons": threats}

        # 安全なURLの場合
        return {"is_safe": True, "message": "安全なURLです。", "reasons": []}

    except requests.exceptions.RequestException as e:
        # ネットワークエラーやAPIエラーの場合
        return {"is_safe": None, "message": "Google Safe Browsing APIエラー", "reasons": [str(e)]}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_url', methods=['POST'])
def check_url():
    data = request.json
    url = data.get('url', '')
    result = is_safe_url(url)

    return jsonify({
        'is_safe': result["is_safe"],
        'message': result["message"],
        'reasons': result["reasons"]
    })

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
