from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app, resources={r"/check_url": {"origins": "*"}})

# Google Safe Browsing APIキー（必ず有効なものを使用）
API_KEY = 'AIzaSyA4AFpKB4rW-ZSHfcrk3zgs4-Fgy4KTPPI'

# Google Safe Browsing API で URL の安全性をチェックする関数
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
        response.raise_for_status()
        result = response.json()

        print(f"Google Safe Browsing API レスポンス: {result}")  # デバッグ用ログ

        # APIレスポンスが "matches" を含んでいる場合 → 危険
        if 'matches' in result:
            threats = [match['threatType'] for match in result['matches']]
            return {"is_safe": False, "message": "⚠️ 危険なURLです！", "reasons": threats}

        # "matches" が無い場合は安全とみなす
        return {"is_safe": True, "message": "✅ 安全なURLです。", "reasons": []}

    except requests.exceptions.RequestException as e:
        return {"is_safe": None, "message": "🚨 Google Safe Browsing APIエラー", "reasons": [str(e)]}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_url', methods=['POST'])
def check_url():
    data = request.json
    url = data.get('url', '')

    # URLが短縮URLの場合、展開する（オプション）
    expanded_url = expand_url(url)

    result = is_safe_url(expanded_url)

    return jsonify({
        'is_safe': result["is_safe"],
        'message': result["message"],
        'reasons': result["reasons"]
    })

# 短縮URLを展開する関数（オプション）
def expand_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.url  # リダイレクト後の最終URLを取得
    except requests.RequestException:
        return url  # エラーの場合はそのまま返す

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
