from flask import Flask, render_template, request, jsonify
import requests
import json
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

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
        response.raise_for_status()  # HTTPステータスコードエラーをキャッチ
        result = response.json()

        # レスポンスのmatchesフィールドをチェック
        if 'matches' in result:
            return False  # 危険なURL
        return True  # 安全なURL

    except requests.exceptions.RequestException as e:
        print(f"APIリクエストエラー: {e}")
        return None  # エラー時はNoneを返す

# ホームページを提供
@app.route('/')
def index():
    return render_template('index.html')

# QRコードの内容をチェックするAPI
@app.route('/check_url', methods=['POST'])
def check_url():
    data = request.json
    url = data.get('url', '')
    is_safe = is_safe_url(url)

    if is_safe is None:
        return jsonify({'error': 'URLの安全性を確認できませんでした。'})

    return jsonify({'is_safe': is_safe})

# アプリケーションのエントリポイント
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
