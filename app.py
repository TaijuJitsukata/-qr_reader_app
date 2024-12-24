from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app, resources={r"/check_url": {"origins": "*"}})  # 開発中は全オリジンを許可

# Google Safe Browsing APIキー
API_KEY = 'AIzaSyA4AFpKB4rW-ZSHfcrk3zgs4-Fgy4KTPPI'

# URLの安全性をチェックする関数
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

        # matchesフィールドをチェックして危険か判定
        if 'matches' in result:
            return {"is_safe": False, "message": "危険なURLです。"}
        return {"is_safe": True, "message": "安全なURLです。"}

    except requests.exceptions.RequestException as e:
        print(f"APIリクエストエラー: {e}")
        return {"is_safe": None, "message": "URLの安全性を確認できませんでした。"}

# ホームページを提供
@app.route('/')
def index():
    return render_template('index.html')

# QRコードの内容をチェックするAPI
@app.route('/check_url', methods=['POST'])
def check_url():
    data = request.json
    url = data.get('url', '')
    result = is_safe_url(url)

    if result["is_safe"] is None:
        return jsonify({'is_safe': None, 'message': result["message"]})

    return jsonify({'is_safe': result["is_safe"], 'message': result["message"]})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
