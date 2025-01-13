import requests
import json
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app, resources={r"/check_url": {"origins": "*"}})

# Google Safe Browsing APIキー
API_KEY = 'YOUR_GOOGLE_SAFE_BROWSING_API_KEY'

# 短縮URLを展開する関数
def expand_url(short_url):
    try:
        response = requests.head(short_url, allow_redirects=True, timeout=5)
        return response.url  # 展開されたURLを返す
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"短縮URLの展開に失敗しました: {e}"}

# URLの安全性をチェックする関数
def is_safe_url(url):
    expanded_result = expand_url(url)  # 短縮URLを展開

    # 短縮URLの展開が失敗した場合
    if isinstance(expanded_result, dict) and not expanded_result.get("success", True):
        return {
            "is_safe": None,
            "message": "URLの安全性を確認できませんでした。",
            "reasons": [expanded_result["error"]],
            "checked_url": url
        }

    # 短縮URL展開が成功した場合
    checked_url = expanded_result if isinstance(expanded_result, str) else url

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
            "threatEntries": [{"url": checked_url}]
        }
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()

        if 'matches' in result:
            threats = [match['threatType'] for match in result['matches']]
            return {
                "is_safe": False,
                "message": "危険なURLです。",
                "reasons": threats,
                "checked_url": checked_url
            }

        return {
            "is_safe": True,
            "message": "安全なURLです。",
            "reasons": [],
            "checked_url": checked_url
        }

    except requests.exceptions.RequestException as e:
        return {
            "is_safe": None,
            "message": "Google Safe Browsing APIエラー",
            "reasons": [f"Google APIエラー: {e}"],
            "checked_url": checked_url
        }

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

    return jsonify({
        'is_safe': result["is_safe"],
        'message': result["message"],
        'reasons': result["reasons"],
        'checked_url': result["checked_url"]
    })

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
