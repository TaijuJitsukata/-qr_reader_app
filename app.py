from flask import Flask, render_template, request, jsonify
import requests
import json
import os
import logging

# Flaskアプリの設定
app = Flask(__name__, static_folder="static", template_folder="templates")

# Google Safe Browsing APIキー（環境変数から取得）
API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "AIzaSyA4AFpKB4rW-ZSHfcrk3zgs4-Fgy4KTPPI")

# ロギング設定
logging.basicConfig(level=logging.DEBUG)

# URLの安全性をチェックする関数
def is_safe_url(url):
    api_url = f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}'
    payload = {
        "client": {
            "clientId": "qr_reader_app",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # HTTPエラーがあれば例外を発生
        result = response.json()
        logging.debug(f"🔍 APIレスポンス: {json.dumps(result, indent=2)}")

        # URLが危険である場合、APIレスポンスに `matches` が含まれる
        if "matches" in result:
            reasons = [match["threatType"] for match in result["matches"]]
            return False, reasons  # 危険なURL
        return True, []  # 安全なURL

    except requests.exceptions.RequestException as e:
        logging.error(f"🚨 APIエラー: {e}")
        return None, ["Google Safe Browsing API のエラー"]

# ホームページを提供
@app.route('/')
def index():
    return render_template('index.html')

# QRコードの内容をチェックするAPI
@app.route('/check_url', methods=['POST'])
def check_url():
    data = request.json
    url = data.get('url', '')

    if not url:
        return jsonify({'error': 'URLが提供されていません'}), 400

    logging.info(f"🔍 URLチェック開始: {url}")
    
    is_safe, reasons = is_safe_url(url)
    
    return jsonify({
        'is_safe': is_safe,
        'reasons': reasons,
        'url': url
    })

# アプリケーションのエントリポイント
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
